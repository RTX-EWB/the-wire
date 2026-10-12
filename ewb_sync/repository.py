"""Reads volunteer opportunities from Salesforce.

This is the only module that writes SOQL. The rest of the code asks for
opportunities in plain terms ("get this one", "list recent ones") and gets
VolunteerOpportunity objects back.
"""

import re

from ewb_sync.client import SalesforceClient
from ewb_sync.errors import InvalidRecordIdError
from ewb_sync.models import FIELD_MAP, SALESFORCE_OBJECT, VolunteerOpportunity

# Salesforce record Ids are 15 or 18 letters/digits. Checking this before an
# Id goes into a query also keeps arbitrary text out of the SOQL string.
_RECORD_ID_PATTERN = re.compile(r"[A-Za-z0-9]{15}([A-Za-z0-9]{3})?")


class VolunteerOpportunityRepository:
    def __init__(self, client: SalesforceClient):
        self._client = client

    def get_by_id(self, record_id: str) -> VolunteerOpportunity | None:
        """Return one opportunity by Salesforce Id, or None if it doesn't exist."""
        _require_valid_record_id(record_id)
        records = self._client.query(
            f"{_select_clause()} WHERE Id = '{record_id}' LIMIT 1"
        )
        return VolunteerOpportunity.from_salesforce(records[0]) if records else None

    def list_recent(self, limit: int = 10) -> list[VolunteerOpportunity]:
        """Return the most recently modified opportunities, newest first."""
        if limit < 1:
            raise ValueError("limit must be at least 1")
        records = self._client.query(
            f"{_select_clause()} ORDER BY LastModifiedDate DESC LIMIT {int(limit)}"
        )
        return [VolunteerOpportunity.from_salesforce(record) for record in records]


def _select_clause() -> str:
    """'SELECT <every field in FIELD_MAP> FROM Volunteer_Opportunity__c'."""
    fields = ", ".join(FIELD_MAP.values())
    return f"SELECT {fields} FROM {SALESFORCE_OBJECT}"


def _require_valid_record_id(record_id: str) -> None:
    if not _RECORD_ID_PATTERN.fullmatch(record_id):
        raise InvalidRecordIdError(
            f"'{record_id}' is not a Salesforce record Id (expected 15 or 18 letters/digits)."
        )
