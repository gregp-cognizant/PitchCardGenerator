# Utilities
import logging
from datetime import datetime
import re

# Primary Components
from llama_index import (
    Document,
    StorageContext,
    VectorStoreIndex,
    ServiceContext,
)

from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from bs4 import BeautifulSoup as BeautifulSoup

from markdownify import markdownify as md

# from llama_index.text_splitter import CodeSplitter
from llama_index.node_parser import MarkdownNodeParser
from llama_index.callbacks import CallbackManager
from langchain_core.utils.html import extract_sub_links


from llama_index.vector_stores.qdrant import QdrantVectorStore


# Custom modules
from src.services.azure_llm_service import AzureLlmBuilder, LLmType
from src.loader.metadata_extraction import MetadataIngestionPipeline
from src.utils.config import load_config
from src.utils.qdrant import QdrantManager
from src.utils.arize_phoenix import ArizePhoenix


class WebDocumentLoader:
    def __init__(self, phoenix_tracer: ArizePhoenix = None, collection_name="techdocs"):
        self.collection_name = collection_name
        self.CONFIG = load_config()
        logger_level = getattr(logging, self.CONFIG["Logging"]["level"].upper())
        logging.basicConfig(
            level=logger_level, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.embed_model = AzureLlmBuilder().get_llm(LLmType.AZURE_EMBEDDINGS)
        self.qdrant = QdrantManager()
        self.phoenix_tracer = phoenix_tracer

        if not self.qdrant.collection_exists(collection_name):
            self.qdrant.create_collection(collection_name, 1536)

        self.vector_store = QdrantVectorStore(
            client=self.qdrant.get_client(),
            collection_name=self.collection_name,
            prefer_grpc=True,
        )
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

    def _html_markdown_extractor(html: str):
        strip_tags = ["script", "style"]
        filtered_html = html
        for tag in strip_tags:
            filtered_html = re.sub(
                rf"<{tag}.*?/{tag}>", "", filtered_html, flags=re.DOTALL
            )
        return md(filtered_html, strip=strip_tags)

    def _html_text_extractor(html: str):
        text = BeautifulSoup(html, "html.parser").text
        filtered_text = re.sub(r"[ \t]{3,}", " ", re.sub(r"\n{3,}", "\n\n\n", text))
        return filtered_text

    def _html_metadata_extractor(html: str, url: str) -> dict:
        """Extract metadata from raw html using BeautifulSoup."""
        logging.debug(f"Extracting metadata from: {url}")
        metadata = {"url": url}
        soup = BeautifulSoup(html, "html.parser")
        metadata["last_accessed_date"] = datetime.today().strftime("%Y-%m-%d")
        if title := soup.find("title"):
            metadata["title"] = title.get_text()
        if keywords := soup.find("meta", attrs={"name": "keywords"}):
            metadata["keywords"] = keywords.get("content", None)
        if description := soup.find("meta", attrs={"name": "description"}):
            metadata["description"] = description.get("content", None)
        if html_lang := soup.find("html"):
            metadata["language"] = html_lang.get("lang", None)
            # if links := soup.find_all("a", href=True):
            #     metadata["links"] = [
            #         f"[{link.text}]({link['href']})" for link in links if link["href"] not in ["", "#", "./"]
            #     ][0:20]
        # metadata["links"] = extract_sub_links(
        #     raw_html=html, url=url, prevent_outside=False
        # )
        return metadata

    def load_documents(
        self,
        url: str,
        # extractor=_html_text_extractor,
        extractor=_html_markdown_extractor,
        metadata_extractor=_html_metadata_extractor,
        max_depth: int = 1,
        timeout: int = 2,
        check_response_status: bool = True,
        max_documents: int = 5,
        re_process: bool = False,
        retry_failed_links: bool = False,
        retry_failed_embeddings: bool = True,
    ) -> list:
        try:
            if self.phoenix_tracer is None:
                callback_manager = None
            else:
                callback_manager = CallbackManager(
                    handlers=[self.phoenix_tracer.callback_handler]
                )

            service_context = ServiceContext.from_defaults(
                embed_model=self.embed_model,
                callback_manager=callback_manager,
            )

            try:
                if not re_process:
                    if self.qdrant.check_url_in_collection(
                        collection_name=self.collection_name, url=url
                    ):
                        logging.info(
                            f"Url({url}) in Collection({self.collection_name}). Reprocessing: {re_process}"
                        )
                        return True
                # md_text_splitter = CodeSplitter(
                #     language="markdown",
                #     chunk_lines=80,  # lines per chunk
                #     chunk_lines_overlap=20,  # lines overlap between chunks
                #     max_chars=3000,  # max chars per chunk
                # )
                # pipeline = MetadataIngestionPipeline.build_pipeline(text_splitter=md_text_splitter)
                pipeline = MetadataIngestionPipeline.build_pipeline(
                    text_splitter=MarkdownNodeParser()
                )
                index = VectorStoreIndex.from_vector_store(
                    self.vector_store,
                    storage_context=self.storage_context,
                    service_context=service_context,
                )
                loader = RecursiveUrlLoader(
                    url=url,
                    max_depth=max_depth,
                    extractor=extractor,
                    metadata_extractor=metadata_extractor,
                    timeout=timeout,
                    prevent_outside=False,
                    check_response_status=check_response_status,
                )
                documents = loader.load()
                llama_docs = [
                    Document.from_langchain_format(doc)
                    for doc in documents[0:max_documents]
                ]
                logging.debug("Web Documents: {llama_docs}")
                for doc in llama_docs:
                    logging.debug(f"loaded doc:{doc.metadata['url']} id:{doc.id_}")
                    try:
                        nodes = pipeline.run(
                            documents=[doc],
                            show_progress=True,
                            in_place=False,
                        )
                        logging.debug("Nodes: {nodes}")
                        index.insert_nodes(nodes=nodes)
                    except Exception as e:
                        logging.error(f"Error running MetadataIngestionPipeline: {e}")
                        logging.error(e)
                        logging.error(e.args[0])
                        logging.error(type(e))
                        logging.debug(doc)
                        pass
                logging.info("Embedding generation completed")
                return True
                # response = self.search_documents(url=url)
                # return response

            except Exception as e:
                logging.error(f"Error generating embeddings: {e}")
                # Print full stack trace
                logging.error(e)
                # Log error type so I can see it and write an except for it
                logging.error(type(e))
                raise e

        except Exception as e:
            # Print full stacktrace
            logging.error(e)
            logging.error(f"load_document: Error - {str(e)}")
            raise e
