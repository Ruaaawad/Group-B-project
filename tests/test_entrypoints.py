"""Tests for application entry points."""

import runpy
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class EntryPointTests(unittest.TestCase):
    """Unit tests for modules that start the application."""

    def test_app_entrypoint_calls_launch_app(self) -> None:
        """Check that the top-level script delegates to the GUI launcher.

        Returns:
            None.
        """
        with patch("src.gui.application.launch_app") as launch_app:
            runpy.run_path(str(PROJECT_ROOT / "app.py"), run_name="__main__")

        launch_app.assert_called_once_with()

    def test_package_entrypoint_calls_launch_app(self) -> None:
        """Check that the package entry point delegates to the GUI launcher.

        Returns:
            None.
        """
        with patch("src.gui.application.launch_app") as launch_app:
            runpy.run_module("src.main", run_name="__main__")

        launch_app.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
