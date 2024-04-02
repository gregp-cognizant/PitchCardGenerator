# test_app.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from langchain_community.llms.fake import FakeListLLM
from pathlib import Path
import json
import uuid

# Helpers
from helpers import (
    cleanup_chat_history_files,
    cleanup_scrape_data_files,
    create_agent_for_testing,
    cleanup_testing_agent,
)

# Import code to test
from src.main import app

client = TestClient(app)

################
### Fixtures ###
################


### Mock the Azure LLM ###
@pytest.fixture
def mock_azure_chat(monkeypatch):
    # We must mock the text in the format of a LangChain agent, otherwise LangChain won't know to exit the loop
    # While LangChain agent is looping over its thoughts it looks for the string "Final Answer: " to know when to exit
    mock_llm_response = "Mocked response\nFinal Answer: Mocked final response"
    with patch(
        "src.services.azure_llm_service.AzureChatOpenAI",
        return_value=FakeListLLM(responses=[mock_llm_response]),
    ) as mock:
        yield mock


@pytest.fixture
def mock_env(monkeypatch):
    def _mock_env(env_vars):
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

    return _mock_env


### Test the FastAPI application ###
def test_fast_api__open_api_docs_json_exists():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "openapi" in response.json()


def test_fast_api__open_api_docs_exists():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


### Test the chat endpoint ###
def test_chat_endpoint_no_rag_valid_input(mock_azure_chat, mock_env):
    # Mock environment variables
    mock_env({"SERPAPI_API_KEY": "some_value"})

    # Act
    guid = str(uuid.uuid4())
    response = client.post(
        "/chat/", json={"user_input": "What is your name?", "chat_history_guid": guid}
    )
    guid = response.json()["chat_history_guid"]

    # Assert
    # Checks for Chat response
    mock_azure_chat.assert_called_once()
    assert response.status_code == 200
    assert response.json()["response"] == "Mocked final response"
    assert response.json()["chat_history_guid"] == guid

    # Cleanup by deleting the chat history files
    cleanup_chat_history_files(guid)


def test_chat_history_created(mock_azure_chat, mock_env):
    # Mock environment variables
    mock_env({"SERPAPI_API_KEY": "some_value"})

    # Act
    response = client.post(
        "/chat/",
        json={
            "user_input": "What is your name?"
        },  # If no chat_history_guid is passed, one is generated
    )
    guid = response.json()["chat_history_guid"]

    # Assert
    chat_history_dir = Path(
        f"/app/.data/chat/memory/"
    )  # ToDo: Need to move this to a proper DB at some point
    chat_history_file = chat_history_dir / f"{guid}.json"
    chat_history_metadata_file = chat_history_dir / f"{guid}.metadata.json"

    # Check that the chat history file exists
    # mock_azure_chat.assert_called_once()
    assert chat_history_file.exists()
    assert chat_history_metadata_file.exists()

    # Cleanup by deleting the chat history files
    cleanup_chat_history_files(guid)


# Validate the default agent has the correct tools and name, matching whats in the config `backend/src/template/default/config.json`
def test_chat_default_agent_has_default_values(mock_azure_chat, mock_env):
    mock_env({"SERPAPI_API_KEY": "some_value"})
    # ToDo: Should we
    # Act
    response = client.post(
        "/chat/",
        json={"user_input": "What is your name?"},
    )

    # Assert

    # Validate we are using the mock instead of expensive Azure OpenAI
    assert response.json()["response"] == "Mocked final response"

    assert response.status_code == 200
    assert response.json()["agent_name"] == "AgentFramework"
    assert response.json()["agent_tools"] == ["search_techdocs", "translate_to_jargon"]


def test_medical_billing_chat_agent_has_one_tool(mock_azure_chat):
    # Act
    response = client.post(
        "/chat/",
        json={
            "user_input": "What is your name?",
            "chat_agent": "medical_billing_agent",
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["agent_name"] == "medical_billing_agent"
    assert response.json()["agent_tools"] == ["search_techdocs"]


def test_chat_agent_with_no_tools_is_valid(mock_azure_chat):
    # Arrange - Make an agent with no tools by creating new dir in `backend/src/template/` and adding a config.json with no tools
    agent_name = "no_tools_agent"
    config_file_data = {
        "agent_tools_names": [],
    }

    # ToDo: Properly create and then cleanup the agent so we don't have to keep test agent in repo
    # Problem is, when new agent is created fastapi needs to be restarted, was banging my head trying to get that to work.
    # create_agent_for_testing(agent_name, config_file_data)

    # Act
    response = client.post(
        "/chat/",
        json={
            "user_input": "What is your name?",
            "chat_agent": agent_name,
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["agent_name"] == agent_name
    assert response.json()["agent_tools"] == []


### /chat/history tests ###
def test_chat_history_get():
    guid = str(uuid.uuid4())

    # ToDo: Break this out into a helper function to reduce duplication
    # Create mock chat history files
    chat_history_dir = Path(f"/app/.data/chat/memory/")
    chat_history_file = chat_history_dir / f"{guid}.json"
    chat_history_metadata_file = chat_history_dir / f"{guid}.metadata.json"

    chat_history_file_contents = [
        {
            "type": "human",
            "data": {
                "content": "Hi",
                "additional_kwargs": {},
                "type": "human",
                "example": False,
            },
        },
        {
            "type": "ai",
            "data": {
                "content": "Hello there",
                "additional_kwargs": {},
                "type": "ai",
                "example": False,
            },
        },
    ]
    chat_history_metadata_file_contents = {
        "date": "2024-01-12T01:41:25Z",
        "chat_agent": "AgentFramework",
        "chat_history_guid": "4e965859-125e-4238-8546-a9773d52b6a1",
    }

    # Use json.dump to write the contents to the files
    json.dump(chat_history_file_contents, chat_history_file.open("w"))
    json.dump(chat_history_metadata_file_contents, chat_history_metadata_file.open("w"))

    # Act
    response = client.get(f"/chat/history/?chat_history_guid={guid}")
    print(response.json())
    chat_history_response = response.json()["chat_history_contents"]

    # Assert
    assert response.status_code == 200
    assert chat_history_response == chat_history_file_contents

    # Cleanup by deleting the chat history files
    cleanup_chat_history_files(guid)


def test_chat_history_get_non_existent():
    guid = str(uuid.uuid4())

    # Act
    response = client.get(f"/chat/history/?chat_history_guid={guid}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "GUID not found, are you sure that exists?"


def test_chat_history_list():
    guid = str(uuid.uuid4())

    # ToDo: Break this out into a helper function to reduce duplication
    # Create mock chat history files
    chat_history_dir = Path(f"/app/.data/chat/memory/")
    chat_history_file = chat_history_dir / f"{guid}.json"
    chat_history_metadata_file = chat_history_dir / f"{guid}.metadata.json"

    chat_history_file_contents = [
        {
            "type": "human",
            "data": {
                "content": "Hi",
                "additional_kwargs": {},
                "type": "human",
                "example": False,
            },
        },
        {
            "type": "ai",
            "data": {
                "content": "Hello there",
                "additional_kwargs": {},
                "type": "ai",
                "example": False,
            },
        },
    ]
    chat_history_metadata_file_contents = {
        "date": "2024-01-12T01:41:25Z",
        "chat_agent": "AgentFramework",
        "chat_history_guid": "4e965859-125e-4238-8546-a9773d52b6a1",
    }

    # Use json.dump to write the contents to the files
    json.dump(chat_history_file_contents, chat_history_file.open("w"))
    json.dump(chat_history_metadata_file_contents, chat_history_metadata_file.open("w"))

    # Act
    response = client.get(f"/chat/history/")
    print(response.json())

    # Assert
    # Checks for Chat response
    assert response.status_code == 200
    assert "chat_history_contents" in response.json()

    # Cleanup by deleting the chat history files
    cleanup_chat_history_files(guid)


### /scrape/ tests ###
def test_scrape_post():
    response = client.post(
        "/scrape/",
        json={"url": "https://python.langchain.com/docs/use_cases/question_answering/"},
    )
    print(response.json())
    assert response.status_code == 200
    assert "message" in response.json()
    assert "full_file_path" in response.json()
    assert response.json()["message"] == "Scraping completed successfully"
    cleanup_scrape_data_files(response.json()["full_file_path"])


### /load-web-document/ tests ###
def test_web_doc_load_post():
    response = client.post(
        "/load-web-document/",
        json={"url": "https://python.langchain.com/docs/use_cases/question_answering/"},
    )
    print(response.json())
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Web document loaded successfully"


### /process-documents/ tests ###
def test_process_documents_post():
    response = client.post(
        "/process-documents/",
        json={
            "source_dir": "src/template/default",
            "collection_name": "techdocs",
            "move_after_processing": False,
            "re_process_files": False,
            "extensions_to_process": [
                ".md",
                ".txt",
            ],
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    assert "successfully_processed_files" in response.json()
    assert "failed_to_process_files" in response.json()
    assert "already_processed_files" in response.json()
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Documents processed successfully"
