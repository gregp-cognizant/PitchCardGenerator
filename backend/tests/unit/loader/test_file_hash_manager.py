# test_file_hash_manager.py

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from src.loader.file_hash_manager import (
    create_database,
    insert_or_update_file_hash,
    get_file_hash,
    calculate_file_hash,
    hash_and_store_processed_files,
)


@pytest.fixture(scope="module")
def db_name():
    db_test_name = "test_file_hashes.db"
    create_database(db_test_name)
    yield db_test_name
    if os.path.exists(db_test_name):
        os.remove(db_test_name)


def test_calculate_file_hash():
    # Test calculate_file_hash function
    test_file_path = "test.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file.")
    expected_hash = calculate_file_hash(test_file_path)
    assert calculate_file_hash(test_file_path) == expected_hash
    os.remove(test_file_path)


def test_insert_and_get_file_hash(db_name):
    # Test insert_or_update_file_hash and get_file_hash functions
    test_file_path = "test.txt"
    test_file_hash = "12345"
    insert_or_update_file_hash(db_name, test_file_path, test_file_hash)
    assert get_file_hash(db_name, test_file_path) == test_file_hash


def test_hash_and_store_processed_files(db_name):
    # Create file for testing
    test_file_path = "test.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file.")

    # Test hash_and_store_processed_files function
    processed_files = [test_file_path]
    hash_and_store_processed_files(processed_files, [], db_name)

    assert get_file_hash(db_name, test_file_path) == calculate_file_hash(test_file_path)

    os.remove(test_file_path)
