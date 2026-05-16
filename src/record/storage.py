"""Storage helpers for JSON-backed record persistence.

This module only validates the persistence container shape. Record-specific
field rules belong in the validation and manager modules.
"""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path


class JSONStorage:
    """Persist record dictionaries to a JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        """Initialise storage with the JSON file location.

        Args:
            file_path: Location of the JSON file used for loading and saving
                records.

        Returns:
            None.
        """
        self.file_path = Path(file_path)

    def load_records(self) -> list[dict]:
        """Load record data from the configured JSON file.

        Returns:
            A list of record dictionaries. If the configured file does not
            exist, an empty list is returned so the application can start with
            no records.

        Raises:
            ValueError: If the file contains invalid JSON or the decoded data
                is not a list of dictionaries.
            OSError: If the file exists but cannot be read by the operating
                system.
        """
        if not self.file_path.exists():
            # Start cleanly when no persisted data file exists yet.
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except JSONDecodeError as error:
            message = "Stored record data is not valid JSON."
            raise ValueError(message) from error

        return self._validate_records(data)

    def save_records(self, records: list[dict]) -> None:
        """Write record data to the configured JSON file.

        Args:
            records: The complete record collection to persist. The value must
                be a list, and each item in the list must be a dictionary.

        Returns:
            None.

        Raises:
            ValueError: If records is not a list of dictionaries.
            TypeError: If any dictionary value cannot be serialised by JSON.
            OSError: If the parent directory or file cannot be written.
        """
        validated_records = self._validate_records(records)
        # Create the folder automatically so saving works on first run.
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(validated_records, handle, indent=2)

    @staticmethod
    def _validate_records(records: object) -> list[dict]:
        """Validate that stored data has the required list-of-dicts shape.

        Args:
            records: Decoded or caller-provided record data to validate.

        Returns:
            The same record list once its container shape has been verified.

        Raises:
            ValueError: If the data is not a list or if any list item is not a
                dictionary.
        """
        if not isinstance(records, list):
            raise ValueError("Record data must be a list of dictionaries.")

        for index, record in enumerate(records):
            if not isinstance(record, dict):
                message = (
                    f"Record data item at index {index} must be a dictionary."
                )
                raise ValueError(message)

        return records
