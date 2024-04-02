# /src/tools/doc_search.py
# Utilities
import logging
import traceback
import langchain
import llama_index

# Primary Components
import openai
from openai import OpenAIError

from llama_index import StorageContext, VectorStoreIndex, ServiceContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from src.utils.qdrant import QdrantManager
from src.utils.arize_phoenix import ArizePhoenix

from llama_index.indices.vector_store.retrievers import (
    VectorIndexAutoRetriever,
)
from llama_index.vector_stores.types import MetadataInfo, VectorStoreInfo
from llama_index.schema import QueryBundle
from llama_index.postprocessor import RankGPTRerank
from llama_index.callbacks import CallbackManager

# Custom modules
from src.utils.config import load_config
from src.services.azure_llm_service import AzureLlmBuilder, LLmType
from src.core.errors import DocumentSearchError


# Set up logging
openai.debug = True
langchain.debug = True
langchain.verbose = True
llama_index.debug = True
llama_index.verbose = True


class DocumentSearch:
    """
    Class to perform document searches using a vector store index.

    Attributes:
    - collection_name (str): Name of the collection to be queried.
    - query (str): User input query for searching documents.
    - CONFIG (dict): Loaded configuration settings.
    - client (QdrantClient): Client to interact with the Qdrant service.
    """

    def __init__(self, phoenix_tracer: ArizePhoenix = None):
        """
        Initializes with collection name and user input.

        Parameters:
        - collection_name (str): Name of the collection to be queried.
        - user_input (str): User input query for searching documents.
        """
        self.CONFIG = load_config()
        self.text_summary_llm = AzureLlmBuilder().get_llm(LLmType.AZURE_OPENAI_GPT4)
        self.embedding_llm = AzureLlmBuilder().get_llm(LLmType.AZURE_EMBEDDINGS)
        self.phoenix_tracer = phoenix_tracer

        if self.phoenix_tracer is None:
            callback_manager = None
        else:
            callback_manager = CallbackManager(
                handlers=[self.phoenix_tracer.callback_handler]
            )

        self.service_context = ServiceContext.from_defaults(
            llm=self.text_summary_llm,
            embed_model=self.embedding_llm,
            chunk_size_limit=1024,
            callback_manager=callback_manager,  # For tracing and logging
        )
        self.qdrant = QdrantManager()

    def setup_index(self, collection_name) -> VectorStoreIndex:
        """
        Sets up and returns the vector store index for the collection.

        Returns:
        - VectorStoreIndex: The set up vector store index.

        Raises:
        - Exception: Propagates any exceptions that occur during the index setup.
        """
        try:
            logging.debug(
                f"setup_index: Setting up index for collection - {collection_name}"
            )
            vector_store = QdrantVectorStore(
                client=self.qdrant.get_client(),
                collection_name=collection_name,
                prefer_grpc=True,
            )
            collection_storage_context = StorageContext.from_defaults(
                vector_store=vector_store
            )
            return VectorStoreIndex.from_vector_store(
                storage_context=collection_storage_context,
                vector_store=vector_store,
                service_context=self.service_context,
            )

        except Exception as e:
            logging.error(f"setup_index: Error - {str(e)}")
            raise e

    def search_documents(self, collection_name: str, query: str):
        """
        Searches the documents in the collection using the user input query.

        Args:
            collection_name (str): The name of the collection to be queried.
            user_input (str): The user input query for searching documents.

        Raises:
            e: _description_

        Returns:
            Any: The response from the query engine.
        """

        try:
            logging.debug(
                f"search_documents: Searching documents in collection - {collection_name}"
            )
            index = self.setup_index(collection_name=collection_name)
            query_bundle = QueryBundle(query)
            vector_store_info = VectorStoreInfo(
                content_info="Technical Documentation and Loaded Web Documents",
                metadata_info=[
                    MetadataInfo(
                        name="creation_date",
                        type="str",
                        description=("File Creation Date in YYYY-MM-DD format"),
                    ),
                    MetadataInfo(
                        name="doc_id",
                        type="str",
                        description=("Document ID in Vector Store"),
                    ),
                    MetadataInfo(
                        name="excerpt_keywords",
                        type="str",
                        description=("List of keywords"),
                    ),
                    MetadataInfo(
                        name="file_name",
                        type="str",
                        description=("File Name"),
                    ),
                    MetadataInfo(
                        name="file_path",
                        type="str",
                        description=("Full File Path"),
                    ),
                    MetadataInfo(
                        name="file_size",
                        type="int",
                        description=("File Size in bytes"),
                    ),
                    MetadataInfo(
                        name="file_type",
                        type="str",
                        description=("File MIME Type"),
                    ),
                    MetadataInfo(
                        name="last_accessed_date",
                        type="str",
                        description=("File Last Accessed Date in YYYY-MM-DD format"),
                    ),
                    MetadataInfo(
                        name="last_modified_date",
                        type="str",
                        description=("File Last Modified Date in YYYY-MM-DD format"),
                    ),
                    MetadataInfo(
                        name="next_section_summary",
                        type="str",
                        description=("Summary of the next section of text"),
                    ),
                    MetadataInfo(
                        name="prev_section_summary",
                        type="str",
                        description=("Summary of the previous section of text"),
                    ),
                    MetadataInfo(
                        name="questions_this_excerpt_can_answer",
                        type="str",
                        description=(
                            "List of questions that can be answered by this section of text"
                        ),
                    ),
                    MetadataInfo(
                        name="section_summary",
                        type="str",
                        description=("Summary of the current section of text"),
                    ),
                    MetadataInfo(
                        name="url",
                        type="str",
                        description=("Reference source URL of text"),
                    ),
                ],
            )
            retriever = VectorIndexAutoRetriever(
                index,
                vector_store_info=vector_store_info,
                similarity_top_k=8,
                # verbose=True,
            )
            logging.debug(f"retriever set {retriever}")
            retrieved_nodes = retriever.retrieve(query_bundle)
            reranker = RankGPTRerank(
                llm=AzureLlmBuilder().get_llm(LLmType.LLAMA_AZURE_OPENAI_GPT4_32K),
                top_n=3,
                # verbose=True,
            )
            retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes, query_bundle)
            logging.debug(f"search_documents: Qdrant Response - {retrieved_nodes}")
            return retrieved_nodes

        except OpenAIError as e:
            logging.error(f"----------------------------------------")
            logging.error(f"search_documents: OpenAIError - {str(e)}")
            traceback.print_exc()
            raise OpenAIError(str(e))

        except Exception as e:
            logging.error(f"search_documents: Error - {str(e)}")
            traceback.print_exc()

            raise DocumentSearchError(str(e))
