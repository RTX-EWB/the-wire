"""OAuth 2.0 client-credentials login for Salesforce.

Salesforce returns an access token plus the instance URL to use for all
later API calls (it can differ from the login URL).
"""

from dataclasses import dataclass

from ewb_sync import http
from ewb_sync.config import Settings
from ewb_sync.errors import AuthenticationError


@dataclass(frozen=True)
class Session:
    """A logged-in Salesforce session."""

    access_token: str
    instance_url: str


def authenticate(settings: Settings) -> Session:
    """Exchange the consumer key and secret for an access token."""
    try:
        response = http.post_form(
            settings.token_url,
            {
                "grant_type": "client_credentials",
                "client_id": settings.client_id,
                "client_secret": settings.client_secret,
            },
        )
    except http.HttpError as error:
        raise AuthenticationError(
            f"Salesforce login failed (HTTP {error.status}): {error.body}"
        ) from error

    return Session(
        access_token=response["access_token"],
        instance_url=response["instance_url"].rstrip("/"),
    )
