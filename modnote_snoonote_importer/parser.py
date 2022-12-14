"""Parse SnooNotes"""

# https://praw.readthedocs.io/en/stable/code_overview/other/subreddit_mod_notes.html
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

import dateutil.parser
import praw
import praw.exceptions
import praw.models
import prawcore.exceptions

REDDIT_MOD_NOTE_LABELS: dict[str, str] = {
    "ABUSE_WARNING": "Abuse Warning",
    "BAN": "Ban",
    "BOT_BAN": "Shadow Ban",
    "HELPFUL_USER": "Helpful User",
    "PERMA_BAN": "Permanent Ban",
    "SOLID_CONTRIBUTOR": "Solid Contributor",
    "SPAM_WARNING": "Spam Warning",
    "SPAM_WATCH": "Spam Watch",
}

# A map between SnooNote labels and their Mod Note counterparts
SNOONOTE_TO_MOD_NOTE_LABELS: dict[str, Optional[str]] = {
    "Abuse Warning": "ABUSE_WARNING",
    "Ban": "BAN",
    "Bot Ban": "BOT_BAN",
    "Good Contributor": "SOLID_CONTRIBUTOR",
    "Good User": "SOLID_CONTRIBUTOR",
    "None": None,
    "Perma Ban": "PERMA_BAN",
    "Shadow Ban": "BOT_BAN",
    "Spam Ban": "BAN",
    "Spam Perma": "PERMA_BAN",
    "Spam Warn": "SPAM_WARNING",
    "Spam Warning": "SPAM_WARNING",
    "Spam Watch": "SPAM_WATCH",
}


@dataclass
class SnooNoteType:
    """Dataclass representing a SnooNote Note Type"""

    note_type_id: int
    sub_name: str
    display_name: str

    # Less useful stuff
    color_code: str
    display_order: int
    bold: bool
    italic: bool
    icon_string: Optional[str]
    disabled: bool


@dataclass
class SnooNote:
    """Dataclass representing a SnooNote Note"""

    note_id: int
    note_type_id: int
    sub_name: str
    submitter: str
    message: str
    applies_to_username: str
    url: str
    timestamp: datetime
    parent_subreddit: Optional[str]


def determine_submission_or_comment(
    *, reddit: praw.Reddit, url: str
) -> Union[praw.models.Submission, praw.models.Comment, None]:
    """Determine if a given URL belongs to a submission or comment, and return the corresponding object

    Arguments:
        url -- URL of a Reddit submission or comment

    Returns:
        Submission or Comment if valid, otherwise None
    """
    # Try a comment first, if the URL is specific enough
    try:
        item = reddit.comment(url=url)
        return item
    except praw.exceptions.InvalidURL:
        pass

    # Try submission
    try:
        item = reddit.submission(url=url)
        return item
    except praw.exceptions.InvalidURL:
        pass

    # Edge cases
    # https://reddit.com/r/DestinyTheGame/sgg692
    # https://reddit.com/r/DestinyTheGame/t86oo2/.../hzop7xf
    #
    # If it is not a comment, a ClientException is raised
    # If it is not a submission, a NotFound is raised
    try:
        item = reddit.comment(id=url.rsplit(sep="/", maxsplit=1)[1])
        if item.subreddit:
            return item
        raise praw.exceptions.InvalidURL(url=url)
    except ValueError:
        pass
    except praw.exceptions.InvalidURL:
        pass
    except praw.exceptions.ClientException:
        pass
    try:
        item = reddit.submission(id=url.rsplit(sep="/", maxsplit=1)[1])
        if item.subreddit:
            return item
        raise praw.exceptions.InvalidURL(url=url, message="Raised because if item.subreddit check failed")
    except (ValueError, prawcore.exceptions.NotFound, praw.exceptions.InvalidURL):
        # If we make it here, URL conversion did not work
        log = logging.getLogger("determine_submission_or_comment")
        log.exception("Unable to determine URL %r", url)
        return None


def split_message_into_chunks(*, header: str, message: str, max_size: int):
    """Split a message into multiple smaller strings, all with the header prepended

    Arguments:
        header -- Header string
        message -- Message string
        max_size -- Maximum size of each chunk

    Yields:
        Chunks of the message, with max length <= max_size
    """
    chunk_len = max_size - len(header)

    copy = message
    while len(copy):

        chunk = header + copy[:chunk_len].strip()
        copy = copy[chunk_len:]
        yield chunk


class SnooNoteParser:
    """SnooNote Parser and container of parsed data"""

    def __init__(self, *, reddit: praw.Reddit, data_file: str):
        """Init"""
        # Logging
        self._log: logging.Logger = logging.getLogger("parser")
        self._log.info("Initializing parser with data file %r", data_file)

        # Containers to store data
        self._note_type_map: dict[int, SnooNoteType] = {}
        self._note_types: list[SnooNoteType] = []
        self._notes: list[SnooNote] = []

        # Reddit
        self._reddit = reddit

        # SnooNote data file
        self._file_path: str = data_file

    @property
    def note_type_map(self) -> dict[int, SnooNoteType]:
        """Get a map of note types, with the ID as key"""
        return self._note_type_map

    @property
    def note_types(self) -> list[SnooNoteType]:
        """Get parsed note types"""
        return self._note_types

    @property
    def notes(self) -> list[SnooNote]:
        """Get parsed notes"""
        return self._notes

    def parse(self):
        """Parse the SnooNote export"""
        # Open the SnooNote file
        try:
            with open(self._file_path, "rt", encoding="utf8") as file:
                json_output = json.load(file)

                # Parse out the note types
                for item in json_output.get("NoteTypes", []):
                    note_type = SnooNoteType(
                        note_type_id=item["NoteTypeID"],
                        sub_name=item["SubName"],
                        display_name=item["DisplayName"],
                        color_code=item["ColorCode"],
                        display_order=item["DisplayOrder"],
                        bold=item["Bold"],
                        italic=item["Italic"],
                        icon_string=item["IconString"],
                        disabled=item["Disabled"],
                    )
                    # If we have not mapped this note type to a Mod Note label
                    if note_type.display_name not in SNOONOTE_TO_MOD_NOTE_LABELS:
                        self._log.error(
                            "Note type %r is not in the SnooNote to Mod Note map. Please file an issue.",
                            note_type.display_name,
                        )
                        raise ValueError(
                            f"Note type {note_type.display_name!r} is not defined in the SnooNote to "
                            "Mod Note map. Please file an issue."
                        )
                    self._note_type_map[note_type.note_type_id] = note_type
                    self._note_types.append(note_type)
                self._log.info("Parsed %s note types", len(json_output.get("NoteTypes", [])))

                # Parse out the notes
                for item in json_output.get("Notes", []):
                    note = SnooNote(
                        note_id=item["NoteID"],
                        note_type_id=item["NoteTypeID"],
                        sub_name=item["SubName"],
                        submitter=item["Submitter"],
                        message=item["Message"],
                        applies_to_username=item["AppliesToUsername"],
                        url=item["Url"],
                        timestamp=dateutil.parser.isoparse(item["Timestamp"]),
                        parent_subreddit=item["ParentSubreddit"],
                    )
                    if note.applies_to_username.lower() == "[deleted]":
                        self._log.warning("Found a SnooNote for [deleted], skipping")
                        continue
                    self._notes.append(note)
                self._log.info("Parsed %s notes", len(json_output.get("Notes", [])))
        except OSError:
            self._log.exception("SnooNotes file not found or unable to be opened.")
            return

        # If we made it here, we parsed the file!
        self._log.debug("Successfully parsed the export file")

    def _post_to_reddit(
        self,
        *,
        snoo_note: SnooNote,
        label: Union[str, None],
        note: str,
        redditor: str,
        subreddit: str,
        thing: Optional[Union[praw.models.Submission, praw.models.Comment, str]],
    ) -> bool:
        """Post a Mod Note to Reddit

        Note: This function is not rate-limited, as PRAW can handle this. Limits can be changed by Reddit.

        Arguments:
            snoo_note -- SnooNote to be converted (used for logging errors)
            label -- Reddit Mod Note label
            note -- Actual note text
            redditor -- Reddit username of the note target
            subreddit -- Subreddit the note is being added to
            thing -- Submission, Comment, str of PRAW Fullname (see docs), or None

        Returns:
            True if note was posted, False otherwise
        """
        try:
            self._reddit.notes.create(label=label, note=note, redditor=redditor, subreddit=subreddit, thing=thing)
            self._log.info("Created Mod Note for Redditor %r", snoo_note.applies_to_username)
            return True
        except praw.exceptions.RedditAPIException as e:
            # User does not exist
            if e.error_type == "USER_DOESNT_EXIST":
                self._log.error("Unable to convert SnooNote %r (USER_DOESNT_EXIST)", snoo_note.note_id)
            # Submission/Comment not valid - try to repost note without the thing argument
            elif e.error_type == "NO_THING_ID":
                self._log.error(
                    "Received NO_THING_ID for SnooNote %r - trying without 'thing' param", snoo_note.note_id
                )
                self._post_to_reddit(
                    snoo_note=snoo_note, label=label, note=note, redditor=redditor, subreddit=subreddit, thing=None
                )
            else:
                self._log.exception(
                    "Unable to create Mod Note %s",
                    {"label": label, "note": note, "redditor": redditor, "subreddit": subreddit, "thing": thing},
                )
                self._log.error("Unable to convert SnooNote %r", snoo_note.note_id)
            return False

    def convert(self):
        """Convert parsed SnooNotes into Mod Notes

        Note: depending on how many notes were imported, this can take a _LONG_ time
        """
        self._log.info("Starting conversion of %s notes", len(self.notes))

        # Constant
        MOD_NOTE_MESSAGE_LENGTH = 250  # pylint: disable=invalid-name

        for i, snoo_note in enumerate(self.notes):
            self._log.info(
                "[%s] Converting note %r, created by mod %r for Redditor %r",
                i,
                snoo_note.note_id,
                snoo_note.submitter,
                snoo_note.applies_to_username,
            )
            time = snoo_note.timestamp.isoformat(timespec="seconds")
            author = snoo_note.submitter
            header = f"[{time}] [u/{author}]\n"
            full_message = header + snoo_note.message

            # Figure out if the "thing" field is relevant. It can be a Submission or Comment, but it MUST be
            # related to the subreddit the note is being made on
            thing = determine_submission_or_comment(reddit=self._reddit, url=snoo_note.url)

            # Check message length
            if len(full_message) > MOD_NOTE_MESSAGE_LENGTH:
                # Break up the message
                for message in split_message_into_chunks(
                    header=header, message=snoo_note.message, max_size=MOD_NOTE_MESSAGE_LENGTH
                ):
                    self._log.debug("Creating segmented Mod Note for SnooNote %r", snoo_note.note_id)

                    # Attempt to post to Reddit
                    self._post_to_reddit(
                        snoo_note=snoo_note,
                        label=SNOONOTE_TO_MOD_NOTE_LABELS[self.note_type_map[snoo_note.note_type_id].display_name],
                        note=message,
                        redditor=snoo_note.applies_to_username,
                        subreddit=snoo_note.sub_name,
                        thing=thing,
                    )

            else:
                # Only a single Mod Note needs to be created
                self._log.debug("Creating single Mod Note for SnooNote %r", snoo_note.note_id)

                # Attempt to post to Reddit
                self._post_to_reddit(
                    snoo_note=snoo_note,
                    label=SNOONOTE_TO_MOD_NOTE_LABELS[self.note_type_map[snoo_note.note_type_id].display_name],
                    note=full_message,
                    redditor=snoo_note.applies_to_username,
                    subreddit=snoo_note.sub_name,
                    thing=thing,
                )
