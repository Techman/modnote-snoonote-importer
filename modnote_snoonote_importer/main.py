"""Import SnooNotes into Mod Notes"""

import logging
import logging.config
from argparse import ArgumentParser

import praw
import praw.exceptions
import praw.models

from modnote_snoonote_importer.logger import setup_logger
from modnote_snoonote_importer.parser import SnooNoteParser

# Parse arguments
parser = ArgumentParser(description="Import SnooNotes into Reddit Mod Notes.")
parser.add_argument(
    "--app_id",
    type=str,
    required=True,
    help="Reddit app_id for the application created for use in this script.",
)
parser.add_argument(
    "--app_secret",
    type=str,
    required=True,
    help="Reddit secret for the application created for use in this script.",
)
parser.add_argument(
    "--username",
    type=str,
    required=True,
    help="Reddit account username. Imported notes will appear as this user.",
)
parser.add_argument(
    "--password",
    type=str,
    required=True,
    help="Reddit account password. Imported notes will appear as this user.",
)
parser.add_argument(
    "file",
    type=str,
    default="snoonotes.json",
    help="Path to the SnooNotes JSON export file.",
)
args = parser.parse_args()


def main() -> None:
    """Main function"""

    # Set up logging
    setup_logger()
    logger = logging.getLogger("root")
    logger.info("Starting SnooNote to Mod Note Importer")

    # Setup Reddit
    reddit: praw.models.Redditor = praw.Reddit(
        client_id=args.app_id,
        client_secret=args.app_secret,
        username=args.username,
        password=args.password,
        user_agent="python:modnote-snoonote-importer (by /u/Techman-)",
        # Timeout in seconds
        # https://praw.readthedocs.io/en/stable/getting_started/ratelimits.html
        # Seconds * Minutes * Hours
        timeout=60 * 60 * 5,
    )
    if reddit.read_only:
        logger.error("PRAW is in read-only mode. Probably a configuration or permissions issue.")
        return
    logger.info("Reddit set up and ready!")

    # Set up parser and parse data
    snoonote_parser = SnooNoteParser(reddit=reddit, data_file=args.file)
    snoonote_parser.parse()
    snoonote_parser.convert()
