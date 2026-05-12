"""Business logic for record management."""

from __future__ import annotations

from copy import deepcopy

from src.conf.constants import AIRLINE, CLIENT, FLIGHT
from src.record.validation import ValidationError, normalise_record


class RecordManager:
    """Manage CRUD operations against a list of record dictionaries."""

    def __init__(self, records: list[dict] | None = None) -> None:
        """Initialise the manager with an optional existing record list."""
        self.records: list[dict] = deepcopy(records) if records else []

    def get_records(self, record_type: str | None = None) -> list[dict]:
        """Return all records or only records matching the requested type."""
        if record_type is None:
            return deepcopy(self.records)
        return [deepcopy(record) for record in self.records if record.get("Type") == record_type]

    def create_record(self, record_type: str, payload: dict[str, object]) -> dict:
        """Validate and store a new record of the requested type."""
        # Validate and clean the raw form data before storing it.
        record = normalise_record(record_type, payload)
        # IDs are assigned separately for each record type.
        record["ID"] = self._next_id(record_type)
        # Flight records must reference an existing client and airline.
        self._validate_relationships(record)
        self.records.append(record)
        return deepcopy(record)

    def update_record(self, record_type: str, record_id: int, payload: dict[str, object]) -> dict:
        """Replace an existing record with validated updated data."""
        index = self._find_index(record_type, record_id)
        updated = normalise_record(record_type, payload)
        # Keep the original ID so the same record is updated rather than replaced with a new one.
        updated["ID"] = record_id
        self._validate_relationships(updated)
        self.records[index] = updated
        return deepcopy(updated)

    def delete_record(self, record_type: str, record_id: int) -> None:
        """Delete a record when doing so does not break linked flight data."""
        index = self._find_index(record_type, record_id)
        # Prevent orphaned flight records by blocking deletion of linked clients or airlines.
        if record_type == CLIENT and any(
            item.get("Type") == FLIGHT and item.get("Client_ID") == record_id for item in self.records
        ):
            raise ValidationError("Delete related flight records before removing this client.")
        if record_type == AIRLINE and any(
            item.get("Type") == FLIGHT and item.get("Airline_ID") == record_id for item in self.records
        ):
            raise ValidationError("Delete related flight records before removing this airline.")
        del self.records[index]

    def get_record(self, record_type: str, record_id: int) -> dict:
        """Return one record identified by its type and ID."""
        index = self._find_index(record_type, record_id)
        return deepcopy(self.records[index])

    def search_records(self, record_type: str, search_term: str, field_name: str | None = None) -> list[dict]:
        """Return records whose field values contain the search term."""
        matches = []
        term = search_term.strip().lower()
        for record in self.records:
            if record.get("Type") != record_type:
                continue

            if not term:
                matches.append(deepcopy(record))
                continue

            fields = [field_name] if field_name else record.keys()
            for field in fields:
                value = str(record.get(field, "")).lower()
                if term in value:
                    matches.append(deepcopy(record))
                    break
        return matches

    def _find_index(self, record_type: str, record_id: int) -> int:
        """Locate the list index for a record of the requested type and ID."""
        for index, record in enumerate(self.records):
            if record.get("Type") == record_type and record.get("ID") == record_id:
                return index
        raise ValidationError(f"{record_type.title()} record with ID {record_id} was not found.")

    def _next_id(self, record_type: str) -> int:
        """Generate the next available ID for the given record type."""
        # Record IDs start at 1 and increase within each record category.
        ids = [int(record["ID"]) for record in self.records if record.get("Type") == record_type and "ID" in record]
        return max(ids, default=0) + 1

    def _validate_relationships(self, record: dict[str, object]) -> None:
        """Ensure flight records refer to valid existing client and airline records."""
        if record["Type"] != FLIGHT:
            return

        # Flights can only be stored when both linked records already exist.
        client_exists = any(
            item.get("Type") == CLIENT and item.get("ID") == record["Client_ID"] for item in self.records
        )
        airline_exists = any(
            item.get("Type") == AIRLINE and item.get("ID") == record["Airline_ID"] for item in self.records
        )
        if not client_exists:
            raise ValidationError("Client ID does not match an existing client record.")
        if not airline_exists:
            raise ValidationError("Airline ID does not match an existing airline record.")
