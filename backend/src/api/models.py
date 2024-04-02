# /src/api/models.py

# Utilities
from pydantic import BaseModel
from typing import Optional, Any
from typing import List
import uuid


# === Chat Models ===
class ChatInput(BaseModel):
    """
    Model representing the user input for chat interactions.

    Attributes:
    user_input (str): The input string from the user to the chat.
    chat_agent (str): Name of chat agent
    chat_history_guid (str): Unique identifier for the chat session. Default value is generated using uuid.uuid4(), user may specify an existing chat guid to resume a previous chat session.
    """

    user_input: str = "Your techdocs vector store has docs about RAG with LangChain, tell me about RAG, what is it?"  # Example chat which will normally hit qdrant
    chat_agent: str = "AgentFramework"
    chat_history_guid: str = str(uuid.uuid4())  # Unique identifier for the chat session


class ChatOutput(BaseModel):
    """
    Model representing the response from the chat agent.

    Attributes:
    response (str): The response string from the chat agent to the user.
    """

    response: str
    chat_history_guid: str
    agent_name: str
    agent_tools: List[str]


# === Chat History Models ===
class ChatHistoryInput(BaseModel):
    """
    Model representing the request to get a list of chat histories.

    Attributes:
    None
    """

    chat_history_guid: Optional[str]  # Unique identifier for the chat session


class ChatHistoryOutput(BaseModel):
    """
    Model representing the response to get a list of chat histories.

    Attributes:
    None
    """

    chat_history_metadata: Optional[List[Any]]
    # Chat history is a list of anything, so we can't define it here
    chat_history_contents: Optional[List[Any]] = None


# === Web Document Loader Models ===
class WebDocumentLoaderRequest(BaseModel):
    """
    Model representing the request to initiate web document loading.

    Attributes:
    url (str): The URL of the web page to be scraped.
    """

    url: str = "https://python.langchain.com/docs/use_cases/question_answering/"


class WebDocumentLoaderResponse(BaseModel):
    """
    Model representing the response from the web document loading process.

    Attributes:
    message (str): The status message indicating the success or failure
                   of the web document loading process.
    """

    message: str


# === Web Scraper Models ===
class ScrapeRequest(BaseModel):
    """
    Model representing the request to initiate web scraping.

    Attributes:
    url (str): The URL of the web page to be scraped.
    """

    url: str = "https://python.langchain.com/docs/use_cases/question_answering/"


class ScrapeResponse(BaseModel):
    """
    Model representing the response from the web scraping process.

    Attributes:
    message (str): The status message indicating the success or failure
                   of the scraping process.
    full_file_path (Optional[str]): The path to the scraped data in markdown on the file system, if the
                          scraping process is successful. None, if unsuccessful.
    """

    message: str
    full_file_path: Optional[
        str
    ]  # ToDo: This is not production ready, really more of an example. Scraped data really needs to be processed and stored somewhere not in a filesystem.


# === Document Loader Models ===


class DocumentLoaderResponse(BaseModel):
    """
    Model representing the response from the document loading process.

    Attributes:
    status (str): The status of the document loading process.
                  It will be 'success' if the documents are processed successfully.
    message (Optional[str]): Optional message field to convey any additional
                             information or details about the process.
    successfully_processed_files (List[str]): List of file names that were successfully processed.
    failed_to_process_files (List[str]): List of file names that failed to process.
    already_processed_files (List[str]): List of file names that were already processed, found file name match in Vector Store and Hash matched.
    """

    status: str
    message: Optional[str]
    successfully_processed_files: List[str] = []
    failed_to_process_files: List[str] = []
    already_processed_files: List[str] = []


class DocumentLoaderRequest(BaseModel):
    """
    Model representing the request to initiate document loading.

    Attributes:
    source_dir (str): The directory from where the documents are to be loaded.
                      Default is set to the directory where scraped data is stored.
    collection_name (str): The name of the collection to which the documents
                           should be loaded. Default is "techdocs".
    move_after_processing (bool): Whether to move the contents of the source directory
                                     after processing. Files are moved to ./src/scraper/out
                                     Default is True.
    re_process_files (bool): Whether to re-process files that have already been processed.
                                    If False, files will have their hash checked and if it matches the hash in the database, they will be skipped.
                                    Several edge cases where files will be re-processed even if this is False.
                                    Default is False.
    extensions_to_process (List[str]): List of file extensions that will be tested for processing.
    """

    source_dir: str = "src/scraper/scraped_data/"
    collection_name: str = "techdocs"
    move_after_processing: bool = True
    re_process_files: bool = False
    extensions_to_process: List[str] = [".md", ".pdf", ".docx", ".txt", ".pptx"]


# === Document Search Models ===


class DocumentSearchRequest(BaseModel):
    """
    Model representing the request to initiate document search.

    Attributes:
    collection_name (str): The name of the collection to be queried.
    user_input (str): The user input query for searching documents.
    """

    collection_name: str
    user_input: str
