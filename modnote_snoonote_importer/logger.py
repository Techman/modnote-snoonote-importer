"""Logging functions"""

import json
import logging
import logging.config


def setup_logger() -> None:
    """Set up logging functions"""
    try:
        with open("logging.json", "rt", encoding="utf8") as file:
            logging.config.dictConfig(json.load(file))
    except OSError:
        logging.basicConfig(level=logging.INFO)
