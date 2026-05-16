"""Smoke tests for the Tkinter application shell."""

import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import TclError

from src.gui.application import RecordManagementApp


class GuiApplicationTests(unittest.TestCase):
    """Unit tests for constructing the GUI without running the event loop."""

    def test_application_can_be_constructed_with_empty_storage(self) -> None:
        """Check that the GUI can be built against an empty JSON data file.

        Returns:
            None.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "records.json"

            try:
                root = tk.Tk()
            except TclError as error:
                self.skipTest(f"Tkinter display is not available: {error}")

            try:
                root.withdraw()
                app = RecordManagementApp(root, storage_path)

                self.assertEqual(app.manager.get_records(), [])
            finally:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
