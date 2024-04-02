import logging
import yaml
import os

from src.utils.config import load_config


def configure_logger():
    # Load configuration using a utility function (assuming it's correctly implemented)
    config = load_config()

    # Get log level from configuration
    log_level_str = config["Logging"]["level"].upper()
    log_level = getattr(logging, log_level_str, None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {log_level_str}")

    # Configure logging with the specified log level and format
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )


configure_logger()
