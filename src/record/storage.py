"""Storage helpers for JSON-backed record persistence."""

from __future__ import annotations

import json
from pathlib import Path


class JSONStorage:
    """Persist records to a JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        """Store the file path used for reading and writing record data."""
        self.file_path = Path(file_path)

    def load_records(self) -> list[dict]:
        """Load records from disk, returning an empty list if no file exists."""
        if not self.file_path.exists():
            # Start with an empty record list when the data file has not been created yet.
            return []

        with self.file_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if not isinstance(data, list):
            raise ValueError("Stored record data must be a list.")
        return data

    def save_records(self, records: list[dict]) -> None:
        """Write the current record list to the configured JSON file."""
        # Create the folder automatically so saving works on first run.
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(records, handle, indent=2)
