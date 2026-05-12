"""Tests for record validation."""

import unittest

from src.conf.constants import AIRLINE, CLIENT, FLIGHT
from src.record.validation import ValidationError, normalise_record


class ValidationTests(unittest.TestCase):
    def test_client_validation_returns_clean_dictionary(self) -> None:
        record = normalise_record(
            CLIENT,
            {
                "Name": "Alice Example",
                "Address Line 1": "1 Street",
                "Address Line 2": "",
                "Address Line 3": "",
                "City": "London",
                "State": "Greater London",
                "Zip Code": "E1 1AA",
                "Country": "UK",
                "Phone Number": "0123456789",
            },
        )
        self.assertEqual(record["Type"], CLIENT)
        self.assertEqual(record["Name"], "Alice Example")

    def test_airline_requires_company_name(self) -> None:
        with self.assertRaises(ValidationError):
            normalise_record(AIRLINE, {"Company Name": ""})

    def test_flight_requires_iso_datetime(self) -> None:
        with self.assertRaises(ValidationError):
            normalise_record(
                FLIGHT,
                {
                    "Client_ID": "1",
                    "Airline_ID": "1",
                    "Date": "06/05/2026",
                    "Start City": "Rome",
                    "End City": "Paris",
                },
            )


if __name__ == "__main__":
    unittest.main()
