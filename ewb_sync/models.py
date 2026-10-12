"""Data models: the Python shape of a Salesforce volunteer opportunity.

THIS IS THE FILE TO EDIT WHEN YOU ADD A FIELD.
Add one line to FIELD_MAP and one attribute to VolunteerOpportunity.
The query in repository.py picks up new fields automatically.
Field API names come from the EWB-USA Salesforce Data Dictionary.
"""

from dataclasses import dataclass

# Salesforce object that holds volunteer opportunities.
SALESFORCE_OBJECT = "Volunteer_Opportunity__c"

# Python attribute name  ->  Salesforce field API name.
FIELD_MAP: dict[str, str] = {
    "id": "Id",
    "name": "Name",
    # Next fields to add (uncomment here AND add the attribute below):
    # "active": "Active__c",
    # "description_html": "Description__c",
    # "last_modified": "LastModifiedDate",
}


@dataclass(frozen=True)
class VolunteerOpportunity:
    """One volunteer opportunity from Salesforce."""

    id: str    # Salesforce record Id; use it to match records with Benevity
    name: str  # Opportunity title; becomes the Benevity opportunity title

    @classmethod
    def from_salesforce(cls, record: dict) -> "VolunteerOpportunity":
        """Build a VolunteerOpportunity from one raw Salesforce record."""
        values = {attribute: record.get(api_name) for attribute, api_name in FIELD_MAP.items()}
        return cls(**values)
