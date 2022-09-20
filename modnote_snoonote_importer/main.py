"""Import SnooNotes into Mod Notes"""

from argparse import ArgumentParser

import logging
import praw
import praw.exceptions
import praw.models


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
    args = parser.parse_args()

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
