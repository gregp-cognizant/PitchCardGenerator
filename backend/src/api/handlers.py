# /src/api/handlers.py

# Internal Modules
from src.agent.agent_handler import AgentHandler, get_agent_handler
from src.scraper.scraper import run_web_scraper
from src.loader.document import DocumentLoader
from src.loader.web_document import WebDocumentLoader
from src.tools.doc_search import DocumentSearch
from src.history.chat_history_handler import ChatHistoryHandler
from src.api.models import (
    ChatInput,
    ChatHistoryInput,
    DocumentLoaderRequest,
    DocumentLoaderResponse,
    DocumentSearchRequest,
    ScrapeRequest,
    WebDocumentLoaderRequest,
    WebDocumentLoaderResponse,
)

# Primary Components
from fastapi import Depends, HTTPException

# Utilities
import logging
import json


# ===== CHAT HANDLER =====
def handle_chat(data: ChatInput, agent: AgentHandler = Depends(get_agent_handler)):
    """Handles chat interactions with AgentHandler.

    Args:
        data (ChatInput): The user input data
        agent (AgentHandler): The AgentHandler instance

    Returns:
        dict: Response from agent
    """

    response, chat_history_guid = agent.chat_with_agent(
        data.user_input, data.chat_agent, data.chat_history_guid
    )
    print("agent: ", agent.agent_name)
    return {
        "response": response,
        "chat_history_guid": chat_history_guid,
        "agent_name": agent.agent_name,
        "agent_tools": agent.agent_tools,
    }


# ===== CHAT HISTORY HANDLER =====
def handle_chat_history(data: ChatHistoryInput):
    """Handles chat interactions with AgentHandler.

    Args:
        data (ChatInput): The user input data
        agent (AgentHandler): The AgentHandler instance

    Returns:
        dict: Response from agent
    """
    guid = data
    if guid is None:
        chat_history_metadata_list = ChatHistoryHandler().list_chat_histories()
        return {"chat_history_metadata": chat_history_metadata_list}
    else:
        chat_history_contents = ChatHistoryHandler().get_chat_history_from_guid(guid)
        if chat_history_contents is None:
            raise HTTPException(
                status_code=404, detail="GUID not found, are you sure that exists?"
            )
        else:
            return {
                "chat_history_metadata": [guid],
                "chat_history_contents": json.loads(chat_history_contents),
            }


# ===== WEB DOCUMENT LOADER HANDLER =====
async def handle_web_doc_load(data: WebDocumentLoaderRequest):
    """
    Initiates the web document ingestion process on the provided URL.

    This asynchronous function logs the triggering of the scrape endpoint
    and runs the web scraper on the URL provided in the ScrapeRequest object.

    Args:
    data (ScrapeRequest): The data containing the URL to be scraped.

    Returns:
    Any: The result of the web scraping process.
    """
    logging.info("Load Web Doc endpoint triggered.")

    # Run the web document loader and return the result.
    loader = WebDocumentLoader(phoenix_tracer=None)
    result = loader.load_documents(url=data.url.strip())
    if result:
        message = "Web document loaded successfully"
    else:
        message = result
    return WebDocumentLoaderResponse(message=message)


# ===== WEB SCRAPER HANDLER =====
async def handle_scrape(data: ScrapeRequest):
    """
    Initiates the web scraping process on the provided URL.

    This asynchronous function logs the triggering of the scrape endpoint
    and runs the web scraper on the URL provided in the ScrapeRequest object.

    Args:
    data (ScrapeRequest): The data containing the URL to be scraped.

    Returns:
    Any: The result of the web scraping process.
    """
    logger = logging.getLogger("Scraper")
    logger.info("Scrape endpoint triggered.")

    # Run the web scraper and return the result.
    return run_web_scraper(data.url)


# ===== DOCUMENT LOADER HANDLER =====
async def handle_process_documents(
    data: DocumentLoaderRequest,
) -> DocumentLoaderResponse:
    """
    Processes documents from a specified source directory and loads them into a collection.

    This function initiates a DocumentLoader with the specified source directory and
    collection name from the DocumentLoaderRequest object. It then loads the documents
    from the source directory into the specified collection. If there are any errors during
    the process, it raises an HTTPException.

    Args:
    data (DocumentLoaderRequest): The data containing the source directory and the
                                  collection name to which the documents should be loaded.

    Returns:
    DocumentLoaderResponse: A response object containing the status of the document
                            loading process and an optional message.

    Raises:
    HTTPException: If there are any errors during the document loading process.
    """
    try:
        processor = DocumentLoader(
            source_dir=data.source_dir,
            collection_name=data.collection_name,
            move_after_processing=data.move_after_processing,
            re_process_files=data.re_process_files,
            extensions_to_process=data.extensions_to_process,
        )
        (
            successfully_processed_files,
            failed_to_process_files,
            already_processed_files,
        ) = (
            await processor.load_documents()
        )  # This should block until processing is complete
        return DocumentLoaderResponse(
            status="success",
            message="Documents processed successfully",
            successfully_processed_files=successfully_processed_files,
            failed_to_process_files=failed_to_process_files,
            already_processed_files=already_processed_files,
        )
    except Exception as e:
        logging.error(f"Error processing documents: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== DOCUMENT SEARCHER HANDLER =====
def handle_document_search(data: DocumentSearchRequest) -> str:
    """Handles document search request and returns the raw response.

    This function receives a DocumentSearchRequest containing the collection
    name and user query input. It instantiates a DocumentSearch object and
    calls search_documents() to perform the actual search.

    The search_documents() method is returning a raw string response rather
    than a list of results. So this handler simply returns the raw string.

    No iteration or post-processing is done on the result string. The client
    must handle the raw response appropriately.

    Args:
        data (DocumentSearchRequest): The request data containing the collection and query.

    Returns:
        str: The raw response string from the DocumentSearch.

    Raises:
        HTTPException: If any exception occurs during the search process. The
                       message will contain the underlying error details.

    Usage:

        ```
        request_data = DocumentSearchRequest(
            collection_name="mydocs",
            user_input="hello world"
        )

        response_string = handle_document_search(request_data)

        print(response_string)
        ```
    """
    try:
        document_search = DocumentSearch(
            collection_name=data.collection_name, user_input=data.user_input
        )

        results = document_search.search_documents()
        logging.debug(f"Raw results: {results}")

        return str(results)

    except Exception as e:
        logging.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
