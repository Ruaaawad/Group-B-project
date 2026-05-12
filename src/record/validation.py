"""Validation helpers for record payloads."""

from __future__ import annotations

from datetime import datetime

from src.conf.constants import AIRLINE, CLIENT, FLIGHT, RECORD_TYPES


class ValidationError(ValueError):
    """Raised when a record payload fails validation."""


def _clean_text(value: object, field_name: str, required: bool = True) -> str:
    """Return stripped text and enforce non-empty values when required."""
    text = "" if value is None else str(value).strip()
    if required and not text:
        raise ValidationError(f"{field_name} is required.")
    return text


def _clean_int(value: object, field_name: str) -> int:
    """Convert a value to an integer or raise a validation error."""
    text = _clean_text(value, field_name)
    try:
        return int(text)
    except ValueError as error:
        raise ValidationError(f"{field_name} must be an integer.") from error


def _clean_datetime(value: object) -> str:
    """Parse and normalise a date-time string for flight records."""
    text = _clean_text(value, "Date")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as error:
        raise ValidationError("Date must use YYYY-MM-DD HH:MM format.") from error
    return parsed.strftime("%Y-%m-%d %H:%M")


def normalise_record(record_type: str, payload: dict[str, object]) -> dict[str, object]:
    """Return a validated dictionary for the requested record type."""
    if record_type not in RECORD_TYPES:
        raise ValidationError("Unsupported record type.")

    if record_type == CLIENT:
        # Client records mainly require contact and address details.
        return {
            "Type": CLIENT,
            "Name": _clean_text(payload.get("Name"), "Name"),
            "Address Line 1": _clean_text(payload.get("Address Line 1"), "Address Line 1"),
            "Address Line 2": _clean_text(payload.get("Address Line 2"), "Address Line 2", required=False),
            "Address Line 3": _clean_text(payload.get("Address Line 3"), "Address Line 3", required=False),
            "City": _clean_text(payload.get("City"), "City"),
            "State": _clean_text(payload.get("State"), "State"),
            "Zip Code": _clean_text(payload.get("Zip Code"), "Zip Code"),
            "Country": _clean_text(payload.get("Country"), "Country"),
            "Phone Number": _clean_text(payload.get("Phone Number"), "Phone Number"),
        }

    if record_type == AIRLINE:
        return {
            "Type": AIRLINE,
            "Company Name": _clean_text(payload.get("Company Name"), "Company Name"),
        }

    # Flight records store links to a client and airline plus journey details.
    return {
        "Type": FLIGHT,
        "Client_ID": _clean_int(payload.get("Client_ID"), "Client ID"),
        "Airline_ID": _clean_int(payload.get("Airline_ID"), "Airline ID"),
        "Date": _clean_datetime(payload.get("Date")),
        "Start City": _clean_text(payload.get("Start City"), "Start City"),
        "End City": _clean_text(payload.get("End City"), "End City"),
    }
