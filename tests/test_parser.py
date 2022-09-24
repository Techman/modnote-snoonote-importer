"""Tests for the SnooNote parser"""

from types import NoneType

import praw
import praw.exceptions
import praw.models

from modnote_snoonote_importer.parser import determine_submission_or_comment


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