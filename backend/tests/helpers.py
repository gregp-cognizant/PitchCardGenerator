from pathlib import Path
import json


def cleanup_chat_history_files(guid):
    """Delete chat history file by guid"""
    chat_history_dir = Path(
        f"/app/.data/chat/memory/"
    )  # ToDo: Might not be safe to rely on file path, only works in container. Someday we move this to a DB
    chat_history_file = chat_history_dir / f"{guid}.json"
    chat_history_metadata_file = chat_history_dir / f"{guid}.metadata.json"

    # Delete the chat history files
    chat_history_file.unlink()
    chat_history_metadata_file.unlink()


def cleanup_scrape_data_files(file_path=None):
    """Delete scrape data files by file path"""
    app_dir = Path("/app/backend/")
    if file_path == None:
        scrape_data_dir = "src/scraper/scraped_data/"
        for scrape_file in scrape_data_dir.iterdir():
            scrape_file.unlink()
    else:
        Path(file_path).unlink()


def create_agent_for_testing(agent_name, config_file_data):
    agent_dir = Path(f"/app/backend/src/template/{agent_name}")
    agent_dir.mkdir(parents=True, exist_ok=True)
    config_file = agent_dir / "config.json"
    json.dump(config_file_data, config_file.open("w"))


def cleanup_testing_agent(agent_name):
    agent_dir = Path(f"/app/backend/src/template/{agent_name}")
    config_file = agent_dir / "config.json"
    config_file.unlink()
    agent_dir.rmdir()
