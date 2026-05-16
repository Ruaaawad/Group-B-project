"""Business logic for record management."""

from __future__ import annotations

from copy import deepcopy

from src.conf.constants import AIRLINE, CLIENT, FLIGHT
from src.record.validation import ValidationError, normalise_record


class RecordManager:
    """Manage CRUD operations against a list of record dictionaries."""

    def __init__(self, records: list[dict] | None = None) -> None:
        """Initialise the manager with an optional existing record list.

        Args:
            records: Existing record dictionaries loaded from storage. If no
                records are provided, the manager starts with an empty list.

        Returns:
            None.
        """
        self.records: list[dict] = deepcopy(records) if records else []

    def get_records(self, record_type: str | None = None) -> list[dict]:
        """Return stored records.

        Args:
            record_type: Optional record type used to filter results. When
                omitted, all stored records are returned.

        Returns:
            A copied list of matching record dictionaries.
        """
        if record_type is None:
            return deepcopy(self.records)
        return [
            deepcopy(record)
            for record in self.records
            if record.get("Type") == record_type
        ]

    def create_record(
        self, record_type: str, payload: dict[str, object]
    ) -> dict:
        """Validate and store a new record of the requested type.

        Args:
            record_type: Type of record to create.
            payload: Raw field values collected from the caller or GUI.

        Returns:
            A copy of the created record, including its assigned ID.

        Raises:
            ValidationError: If field validation fails or a flight references
                a missing client or airline.
        """
        record = normalise_record(record_type, payload)
        # IDs are assigned separately for each record type.
        record["ID"] = self._next_id(record_type)
        self._validate_relationships(record)
        self.records.append(record)
        return deepcopy(record)

    def update_record(
        self,
        record_type: str,
        record_id: int,
        payload: dict[str, object],
    ) -> dict:
        """Replace an existing record with validated updated data.

        Args:
            record_type: Type of record to update.
            record_id: ID of the existing record.
            payload: Raw replacement field values.

        Returns:
            A copy of the updated record.

        Raises:
            ValidationError: If the record is missing, field validation fails,
                or a flight references a missing client or airline.
        """
        index = self._find_index(record_type, record_id)
        updated = normalise_record(record_type, payload)
        # Keep the existing ID so update does not create a new record.
        updated["ID"] = record_id
        self._validate_relationships(updated)
        self.records[index] = updated
        return deepcopy(updated)

    def delete_record(self, record_type: str, record_id: int) -> None:
        """Delete a record when linked flight data will remain valid.

        Args:
            record_type: Type of record to delete.
            record_id: ID of the existing record.

        Returns:
            None.

        Raises:
            ValidationError: If the record is missing or deletion would leave
                a flight linked to a deleted client or airline.
        """
        index = self._find_index(record_type, record_id)
        if record_type == CLIENT and any(
            item.get("Type") == FLIGHT
            and item.get("Client_ID") == record_id
            for item in self.records
        ):
            raise ValidationError(
                "Delete related flight records before removing this client."
            )
        if record_type == AIRLINE and any(
            item.get("Type") == FLIGHT
            and item.get("Airline_ID") == record_id
            for item in self.records
        ):
            raise ValidationError(
                "Delete related flight records before removing this airline."
            )
        del self.records[index]

    def get_record(self, record_type: str, record_id: int) -> dict:
        """Return one record identified by its type and ID.

        Args:
            record_type: Type of record to find.
            record_id: ID of the existing record.

        Returns:
            A copy of the matching record.

        Raises:
            ValidationError: If the record cannot be found.
        """
        index = self._find_index(record_type, record_id)
        return deepcopy(self.records[index])

    def search_records(
        self,
        record_type: str,
        search_term: str,
        field_name: str | None = None,
    ) -> list[dict]:
        """Return records whose field values contain the search term.

        Args:
            record_type: Type of record to search.
            search_term: Text to match against record values.
            field_name: Optional single field to search. When omitted, all
                fields are searched.

        Returns:
            A copied list of matching record dictionaries.
        """
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
            if (
                record.get("Type") == record_type
                and record.get("ID") == record_id
            ):
                return index
        raise ValidationError(
            f"{record_type.title()} record with ID {record_id} was not found."
        )

    def _next_id(self, record_type: str) -> int:
        """Generate the next available ID for the given record type."""
        # Record IDs start at 1 and increase within each record category.
        ids = [
            int(record["ID"])
            for record in self.records
            if record.get("Type") == record_type and "ID" in record
        ]
        return max(ids, default=0) + 1

    def _validate_relationships(self, record: dict[str, object]) -> None:
        """Ensure flights refer to existing client and airline records."""
        if record["Type"] != FLIGHT:
            return

        client_exists = any(
            item.get("Type") == CLIENT
            and item.get("ID") == record["Client_ID"]
            for item in self.records
        )
        airline_exists = any(
            item.get("Type") == AIRLINE
            and item.get("ID") == record["Airline_ID"]
            for item in self.records
        )
        if not client_exists:
            raise ValidationError(
                "Client ID does not match an existing client record."
            )
        if not airline_exists:
            raise ValidationError(
                "Airline ID does not match an existing airline record."
            )
