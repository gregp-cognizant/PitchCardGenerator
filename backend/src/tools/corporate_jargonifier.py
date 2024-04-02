# /backend/src/tools/corporate_jargonifier.py
# NOTE: This tool exists to demonstrate how to create a simple tool and add it to the agent.
# This is also a demonstration of the pattern called "prompt outsourcing" where the agent is simplified by outsourcing conditional but complex rules to external tools

##########################################
### JargonGenius Transformation Engine ###
##########################################
# This tool exist to translate boring regular English into fun and exciting corporate jargon.

# Utilities
import logging
import traceback

# Primary Components
from openai import OpenAIError

# Custom modules
from src.utils.config import load_config
from src.services.azure_llm_service import AzureLlmBuilder, LLmType


class JargonGenius:
    """
    Class to translate text into the most egregious corporate jargon possible.

    """

    def __init__(self):
        """
        Initializes with collection name and user input.

        Parameters:
        - collection_name (str): Name of the collection to be queried.
        - user_input (str): User input query for searching documents.
        """
        self.CONFIG = load_config()
        self._setup_openai()

    def _setup_openai(self, llm_type: LLmType = None):
        """Initialize the OpenAI model based on configurations."""
        try:
            if llm_type is None:
                llm_type = LLmType.AZURE_OPENAI_GPT4
            self.llm = AzureLlmBuilder().get_llm(llm_type)

        except Exception as e:
            logging.error(f"Error initializing OpenAI: {e}")
            raise

    def translate(self, query: str):
        """
        This function uses the OpenAI model to translate the user input into corporate jargon.

        Parameters:
        - query (str): User input query for searching documents.

        Returns:
        - response (str): The translated query.
        """

        try:
            logging.debug(
                f"Initial input query for corporate jargon translator: {query}"
            )

            logging.info("Initiating jargon translation...")

            text = f"""You are a corporate jargon translator, you translate regular English into corporate jargon.
            Make it the most egregious corporate jargon possible.
            Also include tech, devops, and venture capitol type jargon.

            Here are some examples of corporate jargon:
            1. Synergistic Value Co-Creation - Facilitating a multi-lateral, dynamic synergy interface to exponentially enhance shared outcomes and cross-functional team deliverables.
            2. Paradigm Diversification Strategy - Architecting a robust framework for outside-the-conventional-boundary ideation, fostering a culture of continuous innovation and strategic blue-sky thinking.
            3. Low-Effort, High-Impact Trajectory Optimization - Streamlining the identification and cultivation of accessible, yet strategically significant, targets to maximize return on effort and resource investment.
            4. Quantitative Needle Movement Analytics - Employing advanced metrics and analytics to identify and leverage key drivers that materially shift performance indicators and organizational benchmarks.
            5. Revolutionary Paradigm Architecture - Systematically deconstructing and reassembling foundational business models to initiate a groundbreaking shift in operational, cultural, and market engagement methodologies.

            \n\n
            Here is the regular text to translate: [{query}]"""

            self.llm.invoke(text)
            response = self.llm.predict(text)

            logging.info("translate response: ", response)

            return response

        except OpenAIError as e:
            logging.error(f"----------------------------------------")
            logging.error(f"search_documents: OpenAIError - {str(e)}")
            traceback.print_exc()
            raise OpenAIError(str(e))
