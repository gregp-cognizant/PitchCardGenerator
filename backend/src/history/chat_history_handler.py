# /src/agent/agent_handler.py
# Utilities
from pathlib import Path
import logging
import json

# Custom modules
from src.utils.config import load_config
from src.logging.logger_config import configure_logger


class ChatHistoryHandler:
    """
    Class responsible for handling chat history.
    """

    def __init__(self):
        self._initialize()

    def _initialize(self):
        """Initialize all components required for the agent."""
        self._setup_config_and_env()
        configure_logger()

    def _setup_config_and_env(self):
        """Load configurations and setup environment variables."""
        self.CONFIG = load_config()

    def list_chat_histories(self):
        """
        List all chat histories.
        Chat histories are in .data/chat/memory, so we simply return all files in this dir with their extensions removed.
        """
        chat_history_dir = Path(f"/app/.data/chat/memory")

        # Check that dir exists, if not return empty list to be passed up to the API
        if not chat_history_dir.exists():
            logging.warn(
                f"Attempted to lookup chat history dir which doesn't exist: {chat_history_dir}"
            )
            return []

        chat_history_metadata_files = [
            file.name
            for file in chat_history_dir.iterdir()
            if ".metadata.json" in file.name
        ]
        # Loop through the metadata files to get the full content and return in list
        chat_history_metadata = []
        for file in chat_history_metadata_files:
            # Get full file contents and append to list
            metadata = json.loads(open(f"{chat_history_dir}/{file}").read())
            chat_history_metadata.append(metadata)

        # Order chat_history_metadata list so that most recent chats are first
        chat_history_metadata = sorted(
            chat_history_metadata, key=lambda k: k["date"], reverse=True
        )

        return chat_history_metadata

    def get_chat_history_from_guid(self, guid):
        """
        Get the full contents of a chat history from its GUID.
        """
        chat_history_dir = Path(f"/app/.data/chat/memory")
        chat_history_guid = guid
        chat_history_file = chat_history_dir / f"{chat_history_guid}.json"

        # Check file exists, if not return  to be passed up to the API
        if not chat_history_file.exists():
            logging.warning(
                f"Attempted to lookup chat history file which doesn't exist: {chat_history_file}"
            )
            return None

        with open(chat_history_file) as f:
            chat_history = f.read()
        return chat_history
