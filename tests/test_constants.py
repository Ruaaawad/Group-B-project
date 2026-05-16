"""Tests for shared record constants and field definitions."""

import unittest

from src.conf.constants import (
    AIRLINE,
    CLIENT,
    FLIGHT,
    DISPLAY_NAMES,
    FIELD_LABELS,
    RECORD_TYPES,
)


class ConstantsTests(unittest.TestCase):
    """Unit tests for the record constants used by the application."""

    def test_record_types_include_required_types(self) -> None:
        """Check that all required record types are available.

        Returns:
            None.
        """
        self.assertEqual(RECORD_TYPES, (CLIENT, AIRLINE, FLIGHT))

    def test_each_record_type_has_display_name(self) -> None:
        """Check that every record type has a non-empty display name.

        Returns:
            None.
        """
        for record_type in RECORD_TYPES:
            self.assertIn(record_type, DISPLAY_NAMES)
            self.assertTrue(DISPLAY_NAMES[record_type])

    def test_client_fields_match_brief(self) -> None:
        """Check that client records expose the fields required by the brief.

        Returns:
            None.
        """
        fields = [field for field, _ in FIELD_LABELS[CLIENT]]

        self.assertEqual(
            fields,
            [
                "ID",
                "Type",
                "Name",
                "Address Line 1",
                "Address Line 2",
                "Address Line 3",
                "City",
                "State",
                "Zip Code",
                "Country",
                "Phone Number",
            ],
        )

    def test_airline_fields_match_brief(self) -> None:
        """Check that airline records expose the fields required by the brief.

        Returns:
            None.
        """
        fields = [field for field, _ in FIELD_LABELS[AIRLINE]]

        self.assertEqual(fields, ["ID", "Type", "Company Name"])

    def test_flight_fields_match_application_model(self) -> None:
        """Check that flight records expose journey and app-level ID fields.

        Returns:
            None.
        """
        fields = [field for field, _ in FIELD_LABELS[FLIGHT]]

        self.assertEqual(
            fields,
            [
                "ID",
                "Type",
                "Client_ID",
                "Airline_ID",
                "Date",
                "Start City",
                "End City",
            ],
        )


if __name__ == "__main__":
    unittest.main()
