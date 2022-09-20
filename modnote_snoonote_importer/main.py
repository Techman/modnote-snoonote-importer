"""Import SnooNotes into Mod Notes"""

from argparse import ArgumentParser


def main() -> None:
    """Main function"""

    # Parse arguments
    parser = ArgumentParser(description="Import SnooNotes into Reddit Mod Notes")
    parser.add_argument(
        "--app_id",
        type=str,
        required=True,
        help="Reddit app_id for the application created for use in this script",
    )
    parser.add_argument(
        "--app_secret",
        type=str,
        required=True,
        help="Reddit secret for the application created for use in this script",
    )
    args = parser.parse_args()
