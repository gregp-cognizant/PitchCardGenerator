# /src/agent/agent_handler.py
# Utilities
from pathlib import Path
import logging
import traceback
import langchain
from datetime import datetime
import json
from openai import OpenAIError

# Custom modules
from src.utils.config import load_config
from src.tools.setup import ToolSetup
from src.services.azure_llm_service import AzureLlmBuilder, LLmType
from src.utils.arize_phoenix import ArizePhoenix  # Setup LLM Tracing

# Primary Components
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.globals import set_debug

set_debug(True)
langchain.debug = True
langchain.verbose = True

# Global variable to store the agent handler instance.
_agent_instance = None


class AgentHandler:
    """
    Class responsible for initializing and executing the conversational agent.
    Handles OpenAI setup, memory management, and prompt templates.
    """

    def __init__(self):
        self._initialize()

    def _initialize(self):
        """Initialize all components required for the agent."""

        self._setup_config_and_env()
        self._load_agents()
        self.arize_phoenix_instance = ArizePhoenix()

    def _setup_config_and_env(self):
        """Load configurations and setup environment variables."""
        self.CONFIG = load_config()

    def _setup_openai(self, llm_type: LLmType = None):
        """Initialize the OpenAI model based on configurations."""
        try:
            if llm_type is None:
                llm_type = LLmType.AZURE_OPENAI_GPT4
            self.llm = AzureLlmBuilder().get_llm(llm_type)

        except Exception as e:
            logging.error(f"Error initializing OpenAI: {e}")
            raise

    def _setup_memory(
        self, chat_agent: str, chat_history_guid: str
    ) -> ConversationBufferMemory:
        """Setup conversation buffer memory for chat history."""
        memory_path = Path(f"/app/.data/chat/memory/{chat_history_guid}.json")
        metadata_path = Path(
            f"/app/.data/chat/memory/{chat_history_guid}.metadata.json"
        )

        # Create the memory file if it doesn't exist
        if not memory_path.exists():
            memory_path.parent.mkdir(parents=True, exist_ok=True)
            memory_path.touch()
            # Initialize the memory and metadata file
            memory_path.write_text("{}")

        # Create the metadata file with current date and other details
        if not metadata_path.exists():
            date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            metadata = {
                "date": date,
                "chat_agent": chat_agent,
                "chat_history_guid": chat_history_guid,
            }
            json.dump(metadata, metadata_path.open("w"))

        return ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=FileChatMessageHistory(file_path=memory_path),
        )

    def _load_agents(self):
        """Load templates and tools for the ZeroShotAgent's prompts."""
        try:
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            template_path = project_root / "template"

            self.PROMPT_TEMPLATES = {}
            self.AGENT_CONFIGS = {}
            for agent_templates in template_path.glob("**/"):
                self.PROMPT_TEMPLATES[agent_templates.name] = {
                    file.stem: file.read_text()
                    for file in agent_templates.iterdir()
                    if file.suffix == ".txt"
                }

                # Import the config.json file for the agent only if it exists
                if (agent_templates / "config.json").exists():
                    self.AGENT_CONFIGS[agent_templates.name] = json.loads(
                        (agent_templates / "config.json").read_text()
                    )
                # Note: Right now we handle using default values in _stepup_tools(), maybe we should just apply the default values here instead? Discuss with group

        except Exception as e:
            logging.error(f"Error loading prompt templates: {e}")
            raise

    def _initialize_agent_executor(self):
        """Initialize the ZeroShotAgent with proper configurations."""
        self.agent_executor = self._setup_agent()

    def _setup_tools(self, chat_agent: str, custom_tools: list) -> list:
        """
        Initialize and return the tools required for the ZeroShotAgent.
        """

        # initialize the tools list with tracer
        tool_setup_instance = ToolSetup(self.arize_phoenix_instance)

        # Fallback default tools list incase the default config.json is missing
        tools_enabled = ["search_techdocs", "translate_to_jargon"]

        # Prepare function to use the default tools if the agent's config.json is missing
        def use_default_tools():
            tools_enabled = self.AGENT_CONFIGS["default"]["agent_tools_names"]
            logging.info(
                f"Config for chat_agent not found. Using default tools: {tools_enabled}"
            )

        # Use custom tools provided by the API, if they are passed in
        if custom_tools:
            logging.info(f"Using custom tools: {custom_tools}")
            tools_enabled = custom_tools

        else:  # No custom tools list provided, so use the agent's config.json or default tools
            if (
                chat_agent in self.AGENT_CONFIGS
                and "agent_tools_names" in self.AGENT_CONFIGS[chat_agent]
            ):
                tools_enabled = self.AGENT_CONFIGS[chat_agent]["agent_tools_names"]
                logging.info(f"Using {chat_agent}'s tools: {tools_enabled}")

                # Validate the tools list is a list of strings
                if not isinstance(tools_enabled, list) or not all(
                    isinstance(tool_name, str) for tool_name in tools_enabled
                ):
                    raise TypeError(
                        f"agent_tools_names must be a list of strings in {chat_agent}'s config.json"
                    )
            else:  # Otherwise, use the default tools
                use_default_tools()

        # Store the tools list in the agent handler instance to be returned later
        self.agent_tools = tools_enabled

        return tool_setup_instance.setup_tools(
            tools_enabled, self.arize_phoenix_instance
        )

    def _setup_prompt_template(self, chat_agent: str) -> PromptTemplate:
        """
        Construct and return the prompt template for the agent based on loaded templates and tools.

        Returns:
            PromptTemplate: The constructed prompt template.

        Raises:
            KeyError: If a required key is missing in self.PROMPT_TEMPLATES.
        """

        # Extracting the templates from self.PROMPT_TEMPLATES
        try:
            if chat_agent not in self.PROMPT_TEMPLATES:
                self.PROMPT_TEMPLATES[chat_agent] = self.PROMPT_TEMPLATES["default"]

            if "prefix" in self.PROMPT_TEMPLATES[chat_agent]:
                prefix = self.PROMPT_TEMPLATES[chat_agent]["prefix"]
            else:
                prefix = self.PROMPT_TEMPLATES["default"]["prefix"]

            if "react_cot" in self.PROMPT_TEMPLATES[chat_agent]:
                react_cot = self.PROMPT_TEMPLATES[chat_agent]["react_cot"]
            else:
                react_cot = self.PROMPT_TEMPLATES["default"]["react_cot"]

            if "suffix" in self.PROMPT_TEMPLATES[chat_agent]:
                suffix = self.PROMPT_TEMPLATES[chat_agent]["suffix"]
            else:
                suffix = self.PROMPT_TEMPLATES["default"]["suffix"]

        except KeyError as e:
            logging.error(f"Missing key in PROMPT_TEMPLATES: {e}")
            raise

        # Constructing the final template string
        final_template_str = f"{prefix}\n{{tools}}\n{react_cot}\n{suffix}"

        # Creating an instance of PromptTemplate
        prompt_template = PromptTemplate(
            input_variables=[
                "chat_history",
                "input",
                "agent_scratchpad",
                "tools",
                "tool_names",
            ],
            template=final_template_str,
        )

        return prompt_template

    def _setup_agent(
        self,
        chat_history_guid: str,
        chat_agent: str = "AgentFramework",
        custom_tools: list = None,
        llm_type: LLmType = None,
    ) -> AgentExecutor:
        """
        Construct and return the ZeroShotAgent with all its configurations.
        """

        # Set the agent name
        self.agent_name = chat_agent

        if llm_type is None:
            if "llm_type" in self.AGENT_CONFIGS[chat_agent]:
                llm_type = getattr(LLmType, self.AGENT_CONFIGS[chat_agent]["llm_type"])
        self._setup_openai(llm_type)

        memory = self._setup_memory(
            chat_agent=chat_agent, chat_history_guid=chat_history_guid
        )

        tools = self._setup_tools(chat_agent, custom_tools)
        prompt = self._setup_prompt_template(chat_agent=chat_agent)
        agent = create_react_agent(self.llm, tools, prompt)
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
            memory=memory,
            handle_parsing_errors=True,
        )

    def chat_with_agent(
        self, user_input: str, chat_agent: str, chat_history_guid: str
    ) -> str:
        """
        Handle user input to chat with the agent and return its response.
        """
        try:
            logging.info(
                f"Received {chat_agent} chat (guid: {chat_history_guid}) request for input '{user_input}'"
            )

            agent_executor = self._setup_agent(
                chat_agent=chat_agent, chat_history_guid=chat_history_guid
            )
            response = agent_executor.invoke({"input": user_input})

            logging.info(
                f"Successful chat response for input '{user_input}': {response}"
            )
            return (
                response.get("output") if isinstance(response, dict) else response,
                chat_history_guid,
            )
        except OpenAIError as e:
            # Capture the full stack trace for the exception and log it
            logging.error(f"OpenAI error: {e}")
            traceback.print_exc()
            return e
        except Exception as e:
            # Capture the full stack trace for the exception and log it
            logging.error(f"Error: {e}")
            traceback.print_exc()
            return str(e)


def get_agent_handler() -> AgentHandler:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentHandler()
    return _agent_instance
