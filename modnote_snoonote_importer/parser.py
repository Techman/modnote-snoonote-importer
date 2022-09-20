"""Parse SnooNotes"""

# https://praw.readthedocs.io/en/stable/code_overview/other/subreddit_mod_notes.html
from dataclasses import dataclass
from datetime import datetime
import logging

REDDIT_MOD_NOTE_LABELS: dict[str, str] = {
    "ABUSE_WARNING": "Abuse Warning",
    "BAN": "Ban",
    "BOT_BAN": "Bot Ban",
    "HELPFUL_USER": "Helpful User",
    "PERMA_BAN": "Permanent Ban",
    "SOLID_CONTRIBUTOR": "Solid Contributor",
    "SPAM_WARNING": "Spam Warning",
    "SPAM_WATCH": "Spam Watch",
}

# A map between SnooNote labels and their Mod Note counterparts
SNOONOTE_TO_MOD_NOTE_LABELS: dict[str, str] = {
    "Abuse Warning": "ABUSE_WARNING",
    "Ban": "BAN",
    "Good User": "SOLID_CONTRIBUTOR",
    "Perma Ban": "PERMA_BAN",
    # "Shadow Ban": "",
    "Spam Ban": "BOT_BAN",
    "Spam Perma": "PERMA_BAN",
    "Spam Warn": "SPAM_WARNING",
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
    icon_string: str
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
    parent_subreddit: str


class SnooNoteParser:
    """SnooNote Parser and container of parsed data"""

    def __init__(self, *, data_file: str):
        """Init"""
        # Logging
        self._log: logging.Logger = logging.getLogger("parser")

        # Lists to store data
        self._note_types: list[SnooNoteType] = []
        self._notes: list[SnooNote] = []

        # SnooNote data file
        self._file_path: str = data_file

    @property
    def note_types(self) -> list[SnooNoteType]:
        """Get parsed note types"""
        return self._note_types

    @property
    def notes(self) -> list[SnooNote]:
        """Get parsed notes"""
        return self._notes
