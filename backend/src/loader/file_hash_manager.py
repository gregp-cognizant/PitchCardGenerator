# file_hash_manager.py
# At some point I expect we will replace this with a proper DB container in docker-compose. For now, this is a simple SQLite DB.
# Figure we will use another DB for storing prompt templates, chat history, etc at some point.

# Utilities
import logging

# Primary Components
import sqlite3
import hashlib
import os

# Custom modules
from src.utils.config import load_config

config = load_config()
logger_level = getattr(logging, config["Logging"]["level"].upper())
logging.basicConfig(
    level=logger_level, format="%(asctime)s - %(levelname)s - %(message)s"
)
db_path = "/app/backend/sqlite/"


def create_database(db_name):
    """
    Create a SQLite database with the specified name if it doesn't exist.
    The database will contain a table for storing file paths and their hashes.

    :param db_name: Name of the SQLite database file.
    """
    db_name = f"{db_path}{db_name}"

    if not os.path.exists(db_path):
        os.makedirs(db_path)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS file_hashes (file_path TEXT PRIMARY KEY, file_hash TEXT)"""
    )
    conn.commit()
    conn.close()


def insert_or_update_file_hash(db_name, file_path, file_hash):
    """
    Insert or update a file's hash in the database.

    :param db_name: Name of the SQLite database file.
    :param file_path: Path of the file.
    :param file_hash: Hash of the file content.
    """
    db_name = f"{db_path}{db_name}"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO file_hashes (file_path, file_hash) VALUES (?, ?)",
        (file_path, file_hash),
    )
    conn.commit()
    conn.close()


def get_file_hash(db_name, file_path):
    """
    Retrieve a file's hash from the database.

    :param db_name: Name of the SQLite database file.
    :param file_path: Path of the file.
    :return: The hash of the file if found, otherwise None.
    """
    try:
        db_name = f"{db_path}{db_name}"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT file_hash FROM file_hashes WHERE file_path = ?", (file_path,))
        row = c.fetchone()
    except Exception as e:
        logging.error(f"Error when querying the database: {e}")
    finally:
        conn.close()

    return row[0] if row else None


def calculate_file_hash(file_path):
    """
    Calculate the SHA256 hash of a file.

    :param file_path: Path of the file.
    :return: The SHA256 hash of the file content.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


# In file_hash_manager.py


def hash_and_store_processed_files(
    processed_files, converted_pdf_files, hashes_db_name
):
    for file in processed_files:
        try:
            file_to_hash = file

            # Handling for converted PPTX to PDFs
            if "converted_from_pptx" in file:
                file_to_hash = next(
                    pdf["original_file"]
                    for pdf in converted_pdf_files
                    if pdf["converted_file"] == file
                )

            current_hash = calculate_file_hash(file_to_hash)
            insert_or_update_file_hash(hashes_db_name, file_to_hash, current_hash)

        except Exception as e:
            logging.warning(f"Issue hashing and storing file {file}: {e}")
            logging.warning("File will be re-processed in the future")
