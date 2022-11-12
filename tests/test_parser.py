"""Tests for the SnooNote parser"""

from datetime import datetime, timezone
from types import NoneType

import dateutil.parser
import praw
import praw.exceptions
import praw.models

from modnote_snoonote_importer.parser import (
    SnooNote,
    SnooNoteParser,
    SnooNoteType,
    determine_submission_or_comment,
    split_message_into_chunks,
)


def test_parser(reddit: praw.Reddit) -> None:
    """Test parsing of SnooNotes and Note Types"""
    parser = SnooNoteParser(reddit=reddit, data_file="tests/snoonotes.json")
    parser.parse()

    # Only one note should have been parsed
    assert len(parser.notes) == 1

    # Check that the note values match what is in the file
    assert parser.notes[0] is not None
    note = parser.notes[0]
    assert isinstance(note, SnooNote)
    assert note.note_id == 1
    assert note.note_type_id == 12
    assert note.sub_name == "Techman"
    assert note.submitter == "Techman-"
    assert note.message == "Test message"
    assert note.applies_to_username == "Techman-"
    assert note.url == "https://www.reddit.com/r/Techman/comments/quln8b/hello_world/"
    assert note.timestamp == dateutil.parser.parse(timestr="2022-09-24T18:46:14.15Z")

    # There should be 9 note types
    assert len(parser.note_types) == 10

    # Check that the "Good User" type is correct
    assert parser.note_type_map is not None
    assert 12 in parser.note_type_map
    note_type = parser.note_type_map[12]
    assert isinstance(note_type, SnooNoteType)
    assert note_type.note_type_id == 12
    assert note_type.sub_name == "Techman"
    assert note_type.display_name == "Good User"
    assert note_type.color_code == "008000"
    assert note_type.display_order == 1
    assert note_type.bold is False
    assert note_type.italic is False
    assert note_type.icon_string is None
    assert note_type.disabled is False


def test_split_message() -> None:
    """Test splitting long notes into smaller messages"""
    # https://loremipsum.io/
    # Note text
    lorem_ipsum = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore"
        " et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex"
        " ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat"
        " nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit"
        " anim id estlaborum."
    )
    # Coment header
    header = f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] [u/Techman-]"
    # Current length limit for Mod Notes as of time of this commit
    length_limit = 250
    for message in split_message_into_chunks(header=header, message=lorem_ipsum, max_size=length_limit):
        assert len(message) <= length_limit


def test_valid_submission_url(reddit: praw.Reddit):
    """Test valid submission URLs"""
    submission_url = "https://www.reddit.com/r/DestinyTheGame/comments/x3ejz2/this_week_at_bungie_9012022/"
    old_reddit_submission_url = "https://old.reddit.com/r/DestinyTheGame/comments/x3ejz2/this_week_at_bungie_9012022/"
    new_reddit_submission_url = "https://new.reddit.com/r/DestinyTheGame/comments/x3ejz2/this_week_at_bungie_9012022/"
    short_submission_url = "https://redd.it/x3ejz2"

    submission = determine_submission_or_comment(reddit=reddit, url=submission_url)
    assert isinstance(submission, praw.models.Submission)

    old_submission = determine_submission_or_comment(reddit=reddit, url=old_reddit_submission_url)
    assert isinstance(old_submission, praw.models.Submission)

    new_submission = determine_submission_or_comment(reddit=reddit, url=new_reddit_submission_url)
    assert isinstance(new_submission, praw.models.Submission)

    short_submission = determine_submission_or_comment(reddit=reddit, url=short_submission_url)
    assert isinstance(short_submission, praw.models.Submission)


def test_valid_comment_url(reddit: praw.Reddit):
    """Test valid comment URLs"""
    comment_url = "https://www.reddit.com/r/DestinyTheGame/comments/x3ejz2/this_week_at_bungie_9012022/imow4h4/"
    old_reddit_comment_url = (
        "https://old.reddit.com/r/DestinyTheGame/comments/x3ejz2/this_week_at_bungie_9012022/imow4h4/"
    )
    new_reddit_comment_url = (
        "https://new.reddit.com/r/DestinyTheGame/comments/x3ejz2/this_week_at_bungie_9012022/imow4h4/"
    )

    comment = determine_submission_or_comment(reddit=reddit, url=comment_url)
    assert isinstance(comment, praw.models.Comment)

    old_comment = determine_submission_or_comment(reddit=reddit, url=old_reddit_comment_url)
    assert isinstance(old_comment, praw.models.Comment)

    new_comment = determine_submission_or_comment(reddit=reddit, url=new_reddit_comment_url)
    assert isinstance(new_comment, praw.models.Comment)


def test_edge_case_url(reddit: praw.Reddit):
    """Test known edge case URLs

    These URLs are not valid when typed into a browser, but they can appear in SnooNote backups

    Our determination function tries to make sense of them, if possible
    """

    edge_submission_url = "https://reddit.com/r/DestinyTheGame/sgg692"
    edge_comment_url = "https://reddit.com/r/DestinyTheGame/t86oo2/.../hzop7xf"

    edge_submission = determine_submission_or_comment(reddit=reddit, url=edge_submission_url)
    assert isinstance(edge_submission, praw.models.Submission)

    edge_comment = determine_submission_or_comment(reddit=reddit, url=edge_comment_url)
    assert isinstance(edge_comment, praw.models.Comment)


def test_bad_url(reddit: praw.Reddit):
    """Test known to be bad URLs"""
    bad_url_1 = "https://reddit.com/r/DestinyTheGame/"

    bad_item_1 = determine_submission_or_comment(reddit=reddit, url=bad_url_1)
    assert isinstance(bad_item_1, NoneType)
