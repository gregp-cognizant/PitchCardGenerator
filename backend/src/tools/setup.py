# /src/tools/setup.py

# Primary Components
from langchain_community.utilities import (
    DuckDuckGoSearchAPIWrapper,
    SerpAPIWrapper,
    WikipediaAPIWrapper,
)
from langchain_community.tools import DuckDuckGoSearchResults, WikipediaQueryRun

from langchain.agents import Tool
from src.utils.arize_phoenix import ArizePhoenix

from src.loader.web_document import WebDocumentLoader
from src.tools.doc_search import DocumentSearch
from src.tools.corporate_jargonifier import JargonGenius


class ToolSetup:
    """
    A class dedicated to the setup and initialization of tools used by the agent.
    """

    def __init__(self, phoenix_tracer: ArizePhoenix):
        self.phoenix_tracer = phoenix_tracer

    @staticmethod
    def setup_tools(tools_enabled: list, phoenix_tracer: ArizePhoenix) -> list:
        """
        Static method to initialize and return a list of tools for the agent.
        Returns:
        - list: A list of initialized tools for agent's use.
        """

        def search_google(query: str) -> str:
            """
            This function uses the SerpAPI wrapper to conduct a Google search and returns the raw search results.
            """
            try:
                SerpAPI = SerpAPIWrapper()
                response = SerpAPI.run(query)
            except Exception as e:
                response = e
            return response

        def search_duckduckgo(
            query: str,
            region: str = "wt-wt",  # No region
            # region: str="us-en",  # US
            max_results: int = 10,
            time: str = None,
            source: str = "text",
        ) -> str:
            """
            This function uses the DuckDuckGo Search API wrapper to conduct a web search and returns the raw search results.
            """

            try:
                wrapper = DuckDuckGoSearchAPIWrapper(
                    region=region,
                    time=time,
                    max_results=max_results,
                )
                search = DuckDuckGoSearchResults(api_wrapper=wrapper, source=source)
                response = search.run(query)
            except Exception as e:
                response = e
            return response

        def search_wikipedia(query: str) -> str:
            """
            This function uses the SerpAPI wrapper to conduct a Google search and returns the raw search results.
            """

            try:
                search = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
                response = search.run(query)
            except Exception as e:
                response = e
            return response

        def load_web_document(url: str) -> list:
            """
            This function loads a web document into a specialized vector store named ‘TechDocs,’, where it can be queried
            """
            try:
                nonlocal phoenix_tracer
                loader = WebDocumentLoader(phoenix_tracer=phoenix_tracer)
                loader.load_documents(url=url.strip())
                response = True
            except Exception as e:
                response = e
            return response

        def search_qdrant(query: str, collection: str = "techdocs") -> list:
            """
            This tool enables the querying a qdrant vector store collection via LlamaIndex.
            """

            try:
                nonlocal phoenix_tracer
                search = DocumentSearch(phoenix_tracer=phoenix_tracer)
                response = search.search_documents(
                    collection_name=collection, query=query
                )
            except Exception as e:
                response = e
            return response

        def jargonify(query: str) -> str:
            """
            This tool uses the OpenAI model to translate the user input into corporate jargon.
            """

            try:
                jargon_genius = JargonGenius()
                response = jargon_genius.translate(query)
            except Exception as e:
                response = e
            return response

        tools_available = [
            Tool(
                name="search_google",
                func=search_google,
                description="This is a tool that conducts Google searches via the SerpAPI to retrieve real-time search results programmatically, allowing for efficient extraction and analysis of search data to obtain current and relevant web information for a given query. If you run a search, please provide URL to the useful links in markdown.",
            ),
            Tool(
                name="search_duckduckgo",
                func=lambda query: search_duckduckgo(query=query),
                description="This is a tool that conducts web searches to retrieve real-time search results programmatically, allowing for efficient extraction and analysis of search data to obtain current and relevant web information for a given query. If you run a search, please provide URL to the useful links in markdown.",
            ),
            Tool(
                name="search_duckduckgo_news",
                func=lambda query: search_duckduckgo(query=query, source="news"),
                description="This is a tool that conducts news searches to retrieve real-time news results programmatically, allowing for efficient extraction and analysis of news data to obtain current and relevant news information for a given query. If you run a search, please provide URL to the useful links in markdown.",
            ),
            Tool(
                name="search_duckduckgo_videos",
                func=lambda query: search_duckduckgo(query=query, source="videos"),
                description="This is a tool that conducts video searches to retrieve real-time video results programmatically, allowing for efficient extraction and analysis of video data to obtain current and relevant video information for a given query. If you run a search, please provide URL to the useful links in markdown.",
            ),
            Tool(
                name="search_wikipedia",
                func=search_wikipedia,
                description="This is a tool that conducts Wikipedia searches to retrieve real-time search results programmatically, allowing for efficient extraction and analysis of general information for a given query. Wikipedia is an excellent resource for relevant information about popular topics, people, and places. If you run a search, please provide URL to the useful links in markdown.",
            ),
            Tool(
                name="load_web_document",
                func=load_web_document,
                description="This is a tool that takes a single valid url string as input and retrieve the web page or other document and process it for storage in the vector store named ‘TechDocs’. Once loaded it can be accessed with the search_techdocs tool",
            ),
            Tool(
                name="search_continodocs",
                func=lambda query: search_qdrant(
                    query=query, collection="contino-gdrive"
                ),
                description="This tool enables the querying of a specialized vector store named [‘contino-gdrive’] a repository where users archive valuable technical documentation they have encountered.",
            ),
            Tool(
                name="search_techdocs",
                func=lambda query: search_qdrant(query=query, collection="techdocs"),
                description="This tool enables the querying of a specialized vector store named [’techdocs’] a repository with valuable technical documentation. You may have a wide range of topics withing this vector store. This search tool retrieves results from a vector store using a natural language query as input, and can infer a set of metadata filters as well as the right query string to pass to the vector db (either can also be blank). Try to format queries as fully formed question sentences and include all filters and conditions from original requests and conversation context. It is important to check the ‘TechDocs’ whenever possible to see if it contains useful information.",
            ),
            Tool(
                name="search_cognizant_gen_ai_sales_materials",
                func=lambda query: search_qdrant(
                    query=query, collection="cog_gen_ai_sales_materials"
                ),
                description="This tool enables the querying of a vector store named [’cog_gen_ai_sales_materials’] a repository with Cognizant Gen AI Sales documentation.",
            ),
            Tool(
                name="search_kaiburr_docs",
                func=lambda query: search_qdrant(query=query, collection="Kaiburr"),
                description="This tool enables the querying of a the Kaiburr vector store. A repository with information about Kaiburr.",
            ),
            Tool(
                name="translate_to_jargon",
                func=lambda query: jargonify(query=query),
                description="This tool uses the OpenAI model to translate the user input into corporate jargon.",
            ),
        ]

        return [tool for tool in tools_available if tool.name in tools_enabled]
