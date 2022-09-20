"""Import SnooNotes into Mod Notes"""

import logging
from argparse import ArgumentParser

import praw
import praw.exceptions
import praw.models

from modnote_snoonote_importer.parser import SnooNoteParser


def main() -> None:
    """Main function"""

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("root")

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

    # Test to make sure the file exists
    try:
        with open(args.file, "rt", encoding="utf8") as _:
            pass
    except OSError:
        logger.exception("SnooNotes file not found or unable to be opened.")
        return

    # Setup Reddit
    reddit: praw.models.Redditor = praw.Reddit(
        client_id=args.app_id,
        client_secret=args.app_secret,
        username=args.username,
        password=args.password,
        user_agent="modnote-snoonote-importer by /u/Techman-",
    )
    if reddit.read_only:
        logger.error(
            "PRAW is in read-only mode. Probably a configuration or permissions issue."
        )
        raise praw.exceptions.ReadOnlyException
    else:
        logger.info("Reddit set up and ready!")

    # Set up parser and parse data
    parser = SnooNoteParser(data_file=args.file)
    parser.parse()
