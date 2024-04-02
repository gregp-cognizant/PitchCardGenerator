# Utilities
import logging
import os
import shutil
import asyncio

# Primary Components
from llama_index import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.callbacks import CallbackManager
from src.utils.arize_phoenix import ArizePhoenix
from src.logging.logger_config import configure_logger

# Custom modules
from src.services.azure_llm_service import AzureLlmBuilder, LLmType
from src.loader.metadata_extraction import MetadataIngestionPipeline
from src.utils.config import load_config
from src.loader.file_hash_manager import (
    create_database,
    get_file_hash,
    calculate_file_hash,
    hash_and_store_processed_files,
)
from src.utils.qdrant import QdrantManager
from src.utils.covert_pptx_to_pdf import PPTXToPDFConverter

config = load_config()
logger_level = getattr(logging, config["Logging"]["level"].upper())
logging.basicConfig(
    level=logger_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DocumentLoader:
    def __init__(
        self,
        source_dir="src/scraper/scraped_data",
        collection_name="techdocs",
        move_after_processing=True,
        re_process_files=False,
        extensions_to_process=[".md", ".pdf", ".docx", ".txt", ".pptx"],
    ):
        self.source_dir = source_dir
        self.collection_name = collection_name
        self.move_after_processing = move_after_processing
        self.re_process_files = re_process_files
        self.extensions_to_process = extensions_to_process
        self.CONFIG = load_config()
        # (self.CONFIG)
        self.embed_model = AzureLlmBuilder().get_llm(LLmType.AZURE_EMBEDDINGS)
        self.qdrant = QdrantManager()
        self.phoenix_tracer = ArizePhoenix()
        self.hashes_db_name = f"{collection_name}_file_hashes.db"

        # Initialize DB for file hashes, used to check if a file has already been processed so it isn't needlessly re-processed
        create_database(self.hashes_db_name)

        if not self.qdrant.collection_exists(collection_name):
            self.qdrant.create_collection(collection_name, 1536)

    async def convert_pptx_files_to_pdf(self, pre_processed_files, hashes_db_name):
        pptx_files = [f for f in pre_processed_files if f.endswith(".pptx")]

        conversion_tasks = []
        converted_pdf_files = []  # Track converted files
        already_processed_files = []
        conversion_failures = []  # Track failed conversions

        for pptx_file in pptx_files:
            current_hash = calculate_file_hash(pptx_file)
            stored_hash = get_file_hash(hashes_db_name, pptx_file)
            hash_match = current_hash == stored_hash

            if hash_match and not self.re_process_files:
                logging.info(
                    f"Skipping file {pptx_file} because it has already been processed"
                )
                already_processed_files.append(pptx_file)
                continue

            pdf_file = pptx_file.replace(".pptx", ".pdf")
            convert_pptx_to_pdf = PPTXToPDFConverter(max_retries=5)
            task = asyncio.create_task(convert_pptx_to_pdf.convert(pptx_file, pdf_file))
            conversion_tasks.append(task)

        conversion_results = await asyncio.gather(
            *conversion_tasks, return_exceptions=True
        )

        for result, pptx_file in zip(conversion_results, pptx_files):
            if isinstance(result, Exception):
                logging.error(f"Conversion error for {pptx_file}: {result}")
                conversion_failures.append(pptx_file)
            else:
                success, converted_file_path = result
                if success:
                    logging.info(
                        f"Conversion successful for {pptx_file}, saved to {converted_file_path}"
                    )
                    pre_processed_files.remove(pptx_file)
                    converted_pdf_files.append(
                        {
                            "converted_file": converted_file_path,
                            "original_file": pptx_file,
                        }
                    )
                else:
                    logging.error(f"Conversion failed for {pptx_file}")
                    conversion_failures.append(pptx_file)

        return converted_pdf_files, already_processed_files, conversion_failures

    async def load_documents(self):
        try:
            # Prepare list of files that have already been processed to be returned later
            already_processed_files = []
            if self.re_process_files:
                already_processed_files.append("Re-processing all files")

            # Get list of documents from the source directory to later be compared against list of successfully processed files
            pre_processed_files = []
            for root, dirs, files in os.walk(self.source_dir):
                for file in files:
                    pre_processed_files.append(os.path.join(root, file))

            logging.info(f"pre_processed_files: {pre_processed_files}")

            service_context = ServiceContext.from_defaults(
                embed_model=self.embed_model,
                callback_manager=CallbackManager(
                    handlers=[self.phoenix_tracer.callback_handler]
                ),
            )

            # Create a new list from tested_extensions and remove ".pptx" from it.
            # By creating a new list, we ensure that tested_extensions remains unchanged for future use.
            required_exts = self.extensions_to_process.copy()

            # Processing of PPTX files fails, convert them to PDF first
            # Handle pptx files
            if ".pptx" in self.extensions_to_process:
                (
                    converted_pdf_files,
                    already_processed_files_from_conversion,
                    conversion_failures,
                ) = await self.convert_pptx_files_to_pdf(
                    pre_processed_files, self.hashes_db_name
                )
                already_processed_files.extend(already_processed_files_from_conversion)

                required_exts.remove(".pptx")

            documents = []

            try:
                documents = SimpleDirectoryReader(
                    input_dir=self.source_dir,
                    required_exts=required_exts,
                    recursive=True,
                ).load_data()
                logging.info("Embedding generation completed")

                vector_store = QdrantVectorStore(
                    client=self.qdrant.get_client(),
                    collection_name=self.collection_name,
                    prefer_grpc=True,
                )
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store
                )
                try:
                    pipeline = MetadataIngestionPipeline.build_pipeline()
                    nodes = await pipeline.arun(
                        documents=documents,
                        in_place=True,
                    )
                    index = VectorStoreIndex.from_vector_store(
                        vector_store,
                        storage_context=storage_context,
                        service_context=service_context,
                    )
                    index.insert_nodes(nodes=nodes)
                except KeyError as e:
                    logging.warn(f"Metadata Extraction failed: {e}")
                    index = VectorStoreIndex.from_documents(
                        documents,
                        storage_context=storage_context,
                        service_context=service_context,
                    )

            # Except SimpleDirectoryReader error when no files as okay
            except ValueError:
                logging.warn("No files found in directory to process")

            except Exception as e:
                logging.error(f"Error generating embeddings: {e}")
                # Print full stack trace
                logging.error(e)
                # Log error type so I can see it and write an except for it
                logging.error(type(e))
                raise e

            # List all documents which have been processed successfully to be returned later
            successfully_processed_files_set = {
                doc.metadata["file_path"] for doc in documents
            }
            successfully_processed_files = successfully_processed_files_set

            # Hash successfully processed files so they aren't re-processed in the future
            # NOTE: Only pptx converted to pdf actually have their hashes checked, other files always get re-processed
            # ToDo: Add functionality to check hashes of other files before processing
            if "converted_pdf_files" not in locals() or converted_pdf_files is None:
                converted_pdf_files = []

            hash_and_store_processed_files(
                successfully_processed_files_set,
                converted_pdf_files,
                self.hashes_db_name,
            )

            if ".pptx" in self.extensions_to_process:
                # Delete all converted PDF files which were converted from PPTX files, now that processing is done
                for pdf in converted_pdf_files:
                    try:
                        pdf_file = pdf["converted_file"]
                        os.remove(pdf_file)
                        logging.info(f"Deleting converted file: {pdf_file}")
                        # Also delete the containing directory if it is named converted_from_pptx and is empty
                        containing_dir = os.path.dirname(pdf_file)
                        if (
                            os.path.basename(containing_dir) == "converted_from_pptx"
                            and len(os.listdir(containing_dir)) == 0
                        ):
                            os.rmdir(containing_dir)
                            logging.info(
                                f"Deleted conversion directory: {containing_dir}"
                            )
                    except OSError as e:
                        logging.error(f"Error deleting file {pdf_file}: {e}")

            # Compare successfully processed files against files in the source directory and remove any already_processed_files to make a list of files that failed to process
            failed_to_process_files = list(
                set(pre_processed_files)
                - successfully_processed_files_set
                - set(already_processed_files)
            )

            # Move the files after successfully loading them to the vector index
            if self.move_after_processing:
                self.move_files_to_out()

            return (
                successfully_processed_files,
                failed_to_process_files,
                already_processed_files,
            )
        except Exception as e:
            # Print full stacktrace
            logging.error(e)
            logging.error(f"load_documents: Error - {str(e)}")
            raise e

    def move_files_to_out(self):
        out_dir = "src/scraper/out"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for filename in os.listdir(self.source_dir):
            file_path = os.path.join(self.source_dir, filename)
            if os.path.isfile(file_path):
                shutil.move(file_path, os.path.join(out_dir, filename))
