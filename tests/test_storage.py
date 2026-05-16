"""Tests for JSON storage."""

import json
import tempfile
import unittest
from pathlib import Path

from src.record.storage import JSONStorage


class StorageTests(unittest.TestCase):
    """Unit tests for JSON-backed record persistence."""

    def setUp(self) -> None:
        """Create an isolated temporary folder for each test case.

        Returns:
            None.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.addCleanup(self.temp_dir.cleanup)

    def write_json(self, file_path: Path, value: object) -> None:
        """Write a JSON value directly to a test file.

        Args:
            file_path: Location of the test JSON file.
            value: JSON-serialisable value to write.

        Returns:
            None.
        """
        file_path.write_text(json.dumps(value), encoding="utf-8")

    def test_load_records_returns_empty_list_when_file_missing(self) -> None:
        storage = JSONStorage(self.temp_path / "missing.json")

        self.assertEqual(storage.load_records(), [])

    def test_save_then_load_round_trip(self) -> None:
        file_path = self.temp_path / "records.json"
        storage = JSONStorage(file_path)
        records = [{"ID": 1, "Type": "client", "Name": "Alice"}]

        storage.save_records(records)

        self.assertEqual(storage.load_records(), records)

    def test_save_records_creates_parent_directory(self) -> None:
        file_path = self.temp_path / "nested" / "data" / "records.json"
        storage = JSONStorage(file_path)
        records = [{"ID": 1, "Type": "airline", "Company Name": "Jetstar"}]

        storage.save_records(records)

        self.assertTrue(file_path.exists())
        self.assertEqual(storage.load_records(), records)

    def test_save_records_overwrites_existing_file(self) -> None:
        file_path = self.temp_path / "records.json"
        storage = JSONStorage(file_path)
        first_records = [{"ID": 1, "Type": "client", "Name": "Alice"}]
        second_records = [{"ID": 2, "Type": "client", "Name": "Bob"}]

        storage.save_records(first_records)
        storage.save_records(second_records)

        self.assertEqual(storage.load_records(), second_records)

    def test_load_records_rejects_invalid_json(self) -> None:
        file_path = self.temp_path / "records.json"
        file_path.write_text("{invalid json", encoding="utf-8")
        storage = JSONStorage(file_path)

        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            storage.load_records()

    def test_load_records_rejects_non_list_json(self) -> None:
        file_path = self.temp_path / "records.json"
        self.write_json(file_path, {"ID": 1, "Type": "client"})
        storage = JSONStorage(file_path)

        with self.assertRaisesRegex(ValueError, "list of dictionaries"):
            storage.load_records()

    def test_load_records_rejects_list_with_non_dictionary_item(self) -> None:
        file_path = self.temp_path / "records.json"
        self.write_json(file_path, [{"ID": 1, "Type": "client"}, "invalid"])
        storage = JSONStorage(file_path)

        with self.assertRaisesRegex(ValueError, "index 1"):
            storage.load_records()

    def test_save_records_rejects_non_list_data(self) -> None:
        storage = JSONStorage(self.temp_path / "records.json")

        with self.assertRaisesRegex(ValueError, "list of dictionaries"):
            storage.save_records(  # type: ignore[arg-type]
                {"ID": 1, "Type": "client"}
            )

    def test_save_records_rejects_list_with_non_dictionary_item(self) -> None:
        storage = JSONStorage(self.temp_path / "records.json")

        with self.assertRaisesRegex(ValueError, "index 1"):
            storage.save_records(  # type: ignore[list-item]
                [{"ID": 1, "Type": "client"}, "invalid"]
            )


if __name__ == "__main__":
    unittest.main()
