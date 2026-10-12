"""Tests that run without credentials or network access.

A FakeClient stands in for Salesforce: it records the SOQL it receives and
returns canned records. Run with:  python -m unittest discover tests
"""

import unittest

from ewb_sync.errors import InvalidRecordIdError
from ewb_sync.models import VolunteerOpportunity
from ewb_sync.repository import VolunteerOpportunityRepository

SAMPLE_RECORD = {
    "attributes": {"type": "Volunteer_Opportunity__c"},
    "Id": "a2HUN00000Lw05E2AR",
    "Name": "Navajo Nation, AZ - Livestock Water Storage Project",
}


class FakeClient:
    def __init__(self, records: list[dict]):
        self.records = records
        self.queries: list[str] = []

    def query(self, soql: str) -> list[dict]:
        self.queries.append(soql)
        return self.records


class GetByIdTests(unittest.TestCase):
    def test_returns_name_of_matching_opportunity(self):
        repository = VolunteerOpportunityRepository(FakeClient([SAMPLE_RECORD]))
        opportunity = repository.get_by_id("a2HUN00000Lw05E2AR")
        self.assertEqual(opportunity.name, SAMPLE_RECORD["Name"])

    def test_builds_expected_query(self):
        client = FakeClient([SAMPLE_RECORD])
        VolunteerOpportunityRepository(client).get_by_id("a2HUN00000Lw05E2AR")
        self.assertEqual(
            client.queries[0],
            "SELECT Id, Name FROM Volunteer_Opportunity__c "
            "WHERE Id = 'a2HUN00000Lw05E2AR' LIMIT 1",
        )

    def test_returns_none_when_not_found(self):
        repository = VolunteerOpportunityRepository(FakeClient([]))
        self.assertIsNone(repository.get_by_id("a2HUN00000Lw05E2AR"))

    def test_rejects_invalid_id_before_querying(self):
        client = FakeClient([])
        repository = VolunteerOpportunityRepository(client)
        for bad_id in ["", "short", "x' OR Name != '", "a2HUN00000Lw05E2ARX"]:
            with self.assertRaises(InvalidRecordIdError):
                repository.get_by_id(bad_id)
        self.assertEqual(client.queries, [])


class ListRecentTests(unittest.TestCase):
    def test_returns_all_records_as_models(self):
        repository = VolunteerOpportunityRepository(FakeClient([SAMPLE_RECORD, SAMPLE_RECORD]))
        opportunities = repository.list_recent(limit=2)
        self.assertEqual(len(opportunities), 2)
        self.assertIsInstance(opportunities[0], VolunteerOpportunity)

    def test_rejects_non_positive_limit(self):
        with self.assertRaises(ValueError):
            VolunteerOpportunityRepository(FakeClient([])).list_recent(limit=0)


if __name__ == "__main__":
    unittest.main()
