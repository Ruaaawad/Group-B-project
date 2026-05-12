"""Tests for JSON storage."""

import shutil
import unittest
from pathlib import Path

from src.record.storage import JSONStorage


WORKSPACE_TEMP = Path(__file__).resolve().parents[1] / ".test_tmp"


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        WORKSPACE_TEMP.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        if WORKSPACE_TEMP.exists():
            shutil.rmtree(WORKSPACE_TEMP)

    def test_load_records_returns_empty_list_when_file_missing(self) -> None:
        storage = JSONStorage(WORKSPACE_TEMP / "missing.json")
        self.assertEqual(storage.load_records(), [])

    def test_save_then_load_round_trip(self) -> None:
        file_path = WORKSPACE_TEMP / "records.json"
        storage = JSONStorage(file_path)
        records = [{"ID": 1, "Type": "client", "Name": "Alice"}]
        storage.save_records(records)
        self.assertEqual(storage.load_records(), records)


if __name__ == "__main__":
    unittest.main()
