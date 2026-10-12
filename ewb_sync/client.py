"""A minimal Salesforce REST client: run a SOQL query, get records back.

It knows nothing about volunteer opportunities; it only knows how to talk
to Salesforce. Object-specific logic lives in repository.py.
"""

from ewb_sync import http
from ewb_sync.auth import Session
from ewb_sync.errors import SalesforceApiError


class SalesforceClient:
    def __init__(self, session: Session, api_version: str):
        self._session = session
        self._api_version = api_version

    def query(self, soql: str) -> list[dict]:
        """Run a SOQL query and return every matching record.

        Salesforce returns large results in pages; this follows each
        `nextRecordsUrl` so callers always get the complete list.
        """
        url = f"{self._session.instance_url}/services/data/{self._api_version}/query"
        params = {"q": soql}
        records: list[dict] = []

        while True:
            page = self._get(url, params)
            records.extend(page.get("records", []))

            next_page = page.get("nextRecordsUrl")
            if not next_page:
                return records
            url = f"{self._session.instance_url}{next_page}"
            params = {}

    def _get(self, url: str, params: dict[str, str]) -> dict:
        try:
            return http.get_json(url, params, self._session.access_token)
        except http.HttpError as error:
            raise SalesforceApiError(
                f"Salesforce request failed (HTTP {error.status}): {error.body}"
            ) from error
