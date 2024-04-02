import logging

from qdrant_client import QdrantClient
from src.utils.config import load_config
import time
from qdrant_client.http import models as qdrant_models


class QdrantManager:
    """
    Class to manage Qdrant clients and collections.

    """

    def __init__(self):
        self.CONFIG = load_config()
        self.QDRANT_URL = self.CONFIG["Qdrant"]["url"]
        if not self.QDRANT_URL:
            raise ValueError("QDRANT_URL is not set")
        self.client = QdrantClient(url=self.QDRANT_URL)
        self.check_qdrant()

    def get_client(self):
        return self.client

    def check_qdrant(self):
        """check_qdrant function checks if qdrant is available \n
        Returns:
            None
        """
        max_retries = 5
        retry_delay = 1
        for i in range(max_retries):
            try:
                self.client.get_collections()
                logging.info("Qdrant is available")
                return
            except Exception as e:
                logging.warning(f"Qdrant is not available: {e}")
                if i == max_retries - 1:
                    raise ValueError("Qdrant is not available")
                time.sleep(retry_delay * 2**i)

    def collection_exists(self, collection_name: str) -> bool:
        try:
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False

    def create_collection(self, collection_name: str, vector_size: int):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={"size": vector_size, "distance": "Cosine"},
        )

    def ensure_collection(self, collection_name: str, vector_size: int):
        if not self.collection_exists(collection_name):
            self.create_collection(collection_name, vector_size)

    def check_record_in_collection(
        self, collection_name: str, count_filter: qdrant_models.Filter = None
    ) -> bool:
        try:
            search = self.client.count(
                collection_name=collection_name,
                count_filter=count_filter,
            )
            if search.count > 0:
                return True
            else:
                return False
        except Exception as e:
            logging.error(e)
            return False

    def check_url_in_collection(self, collection_name: str, url: str) -> bool:
        return self.check_record_in_collection(
            collection_name=collection_name,
            count_filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="url", match=qdrant_models.MatchValue(value=url)
                    )
                ]
            ),
        )

    def check_file_in_collection(self, collection_name: str, file_path: str) -> bool:
        return self.check_record_in_collection(
            collection_name=collection_name,
            count_filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="file_path", match=qdrant_models.MatchValue(value=file_path)
                    )
                ]
            ),
        )
