"""Parse SnooNotes"""

# https://praw.readthedocs.io/en/stable/code_overview/other/subreddit_mod_notes.html
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    "Bot Ban": "BOT_BAN",
    "Good Contributor": "SOLID_CONTRIBUTOR",
    "Good User": "SOLID_CONTRIBUTOR",
    "Perma Ban": "PERMA_BAN",
    "Spam Ban": "BAN",
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
    parent_subreddit: Optional[str]


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

    def _parse_timestamp_str(self, *, time_str: str) -> datetime:
        """Parse datetime strings from SnooNotes

        Arguments:
            time_str -- The date+time string

        Returns:
            Python datetime object
        """
        # https://docs.python.org/3/library/datetime.html?highlight=time#strftime-and-strptime-format-codes

        # There are unfortunately a few versions of time strings that can be found in notes, so I try to handle all
        # known cases
        # Case 1: 2021-05-26T05:14:31.073Z
        try:
            time = datetime.strptime(
                time_str.replace("Z", "UTC"), "%Y-%m-%dT%H:%M:%S.%f%Z"
            )
            return time
        except ValueError:
            pass

        # Case 2: 2016-01-22T06:28:10Z
        try:
            time = datetime.strptime(
                time_str.replace("Z", "UTC"), "%Y-%m-%dT%H:%M:%S%Z"
            )
            return time
        except ValueError:
            pass

        # Base case: try ISO date string
        try:
            time = datetime.fromisoformat(time_str)
            return time
        except ValueError as e:
            self._log.exception("Base case failed")
            raise e

    def parse(self):
        """Parse the SnooNote export"""
        # Open the SnooNote file
        try:
            with open(self._file_path, "rt", encoding="utf8") as file:
                json_output = json.load(file)

                # Parse out the note types
                for item in json_output.get("NoteTypes", []):
                    self._note_types.append(
                        SnooNoteType(
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
                    )
                self._log.info(
                    "Parsed %s note types", len(json_output.get("NoteTypes", []))
                )

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
                        timestamp=self._parse_timestamp_str(time_str=item["Timestamp"]),
                        parent_subreddit=item["ParentSubreddit"],
                    )
                    if len(note.message) > 250:
                        self._log.warning(
                            "Note %s has message length greater than 250; will be split into multiple notes on import",
                            note.note_id,
                        )
                    self._notes.append(note)
                self._log.info("Parsed %s notes", len(json_output.get("Notes", [])))
        except OSError:
            self._log.exception("Unable to open/read the export file.")
            return

        # If we made it here, we parsed the file!
        self._log.debug("Successfully parsed the export file")
