"""Tests for record management behavior."""

import unittest

from src.conf.constants import AIRLINE, CLIENT, FLIGHT
from src.record.manager import RecordManager
from src.record.validation import ValidationError


class RecordManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = RecordManager()
        self.client = self.manager.create_record(
            CLIENT,
            {
                "Name": "Alice Example",
                "Address Line 1": "1 Street",
                "Address Line 2": "",
                "Address Line 3": "",
                "City": "London",
                "State": "London",
                "Zip Code": "E1 1AA",
                "Country": "UK",
                "Phone Number": "01234",
            },
        )
        self.airline = self.manager.create_record(
            AIRLINE, {"Company Name": "Sky Travel"}
        )

    def test_create_flight_requires_existing_relationships(self) -> None:
        with self.assertRaises(ValidationError):
            self.manager.create_record(
                FLIGHT,
                {
                    "Client_ID": 999,
                    "Airline_ID": self.airline["ID"],
                    "Date": "2026-05-06 10:30",
                    "Start City": "Madrid",
                    "End City": "Berlin",
                },
            )

    def test_create_update_search_and_delete_flight(self) -> None:
        flight = self.manager.create_record(
            FLIGHT,
            {
                "Client_ID": self.client["ID"],
                "Airline_ID": self.airline["ID"],
                "Date": "2026-05-06 10:30",
                "Start City": "Madrid",
                "End City": "Berlin",
            },
        )
        updated = self.manager.update_record(
            FLIGHT,
            flight["ID"],
            {
                "Client_ID": self.client["ID"],
                "Airline_ID": self.airline["ID"],
                "Date": "2026-05-07 09:15",
                "Start City": "Madrid",
                "End City": "Rome",
            },
        )
        results = self.manager.search_records(FLIGHT, "rome")

        self.assertEqual(updated["End City"], "Rome")
        self.assertEqual(len(results), 1)

        self.manager.delete_record(FLIGHT, flight["ID"])
        self.assertEqual(self.manager.get_records(FLIGHT), [])

    def test_delete_client_with_linked_flights_is_blocked(self) -> None:
        self.manager.create_record(
            FLIGHT,
            {
                "Client_ID": self.client["ID"],
                "Airline_ID": self.airline["ID"],
                "Date": "2026-05-06 10:30",
                "Start City": "Madrid",
                "End City": "Berlin",
            },
        )

        with self.assertRaises(ValidationError):
            self.manager.delete_record(CLIENT, self.client["ID"])

    def test_get_records_filters_by_type(self) -> None:
        self.manager.create_record(
            FLIGHT,
            {
                "Client_ID": self.client["ID"],
                "Airline_ID": self.airline["ID"],
                "Date": "2026-05-06 10:30",
                "Start City": "Madrid",
                "End City": "Berlin",
            },
        )

        client_records = self.manager.get_records(CLIENT)
        airline_records = self.manager.get_records(AIRLINE)
        flight_records = self.manager.get_records(FLIGHT)

        self.assertEqual(len(client_records), 1)
        self.assertEqual(len(airline_records), 1)
        self.assertEqual(len(flight_records), 1)
        self.assertEqual(client_records[0]["Type"], CLIENT)
        self.assertEqual(airline_records[0]["Type"], AIRLINE)
        self.assertEqual(flight_records[0]["Type"], FLIGHT)


if __name__ == "__main__":
    unittest.main()
