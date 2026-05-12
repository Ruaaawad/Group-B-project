"""Shared constants for record definitions."""

CLIENT = "client"
AIRLINE = "airline"
FLIGHT = "flight"

RECORD_TYPES = (CLIENT, AIRLINE, FLIGHT)

FIELD_LABELS = {
    CLIENT: [
        ("ID", "ID"),
        ("Type", "Type"),
        ("Name", "Name"),
        ("Address Line 1", "Address Line 1"),
        ("Address Line 2", "Address Line 2"),
        ("Address Line 3", "Address Line 3"),
        ("City", "City"),
        ("State", "State"),
        ("Zip Code", "Zip Code"),
        ("Country", "Country"),
        ("Phone Number", "Phone Number"),
    ],
    AIRLINE: [
        ("ID", "ID"),
        ("Type", "Type"),
        ("Company Name", "Company Name"),
    ],
    FLIGHT: [
        ("ID", "ID"),
        ("Type", "Type"),
        ("Client_ID", "Client ID"),
        ("Airline_ID", "Airline ID"),
        ("Date", "Date (YYYY-MM-DD HH:MM)"),
        ("Start City", "Start City"),
        ("End City", "End City"),
    ],
}

DISPLAY_NAMES = {
    CLIENT: "Client",
    AIRLINE: "Airline",
    FLIGHT: "Flight",
}

