"""Settings for connecting to the EWB-USA Salesforce sandbox.

Everything that might change between environments lives here, so the rest
of the code never hard-codes a URL or reads an environment variable itself.
Secrets come from environment variables only; they are never written in code.
"""

import os
from dataclasses import dataclass

from ewb_sync.errors import ConfigError

# Defaults from the EWB-USA "Salesforce API Access" doc.
DEFAULT_LOGIN_URL = "https://ewb-usa--benevity.sandbox.my.salesforce.com"
DEFAULT_API_VERSION = "v65.0"

# Environment variable names, kept in one place so they're easy to find.
ENV_CLIENT_ID = "SF_CLIENT_ID"
ENV_CLIENT_SECRET = "SF_CLIENT_SECRET"
ENV_LOGIN_URL = "SF_LOGIN_URL"
ENV_API_VERSION = "SF_API_VERSION"


@dataclass(frozen=True)
class Settings:
    """Everything needed to talk to Salesforce."""

    client_id: str
    client_secret: str
    login_url: str = DEFAULT_LOGIN_URL
    api_version: str = DEFAULT_API_VERSION

    @property
    def token_url(self) -> str:
        return f"{self.login_url}/services/oauth2/token"


def load_settings() -> Settings:
    """Build Settings from environment variables.

    Raises ConfigError if the consumer key or secret is missing.
    """
    client_id = os.environ.get(ENV_CLIENT_ID, "").strip()
    client_secret = os.environ.get(ENV_CLIENT_SECRET, "").strip()

    missing = [
        name
        for name, value in [(ENV_CLIENT_ID, client_id), (ENV_CLIENT_SECRET, client_secret)]
        if not value
    ]
    if missing:
        raise ConfigError(
            "Missing environment variable(s): " + ", ".join(missing)
            + ". Set them to the Consumer Key and Consumer Secret from EWB-USA."
        )

    return Settings(
        client_id=client_id,
        client_secret=client_secret,
        login_url=os.environ.get(ENV_LOGIN_URL, DEFAULT_LOGIN_URL).rstrip("/"),
        api_version=os.environ.get(ENV_API_VERSION, DEFAULT_API_VERSION),
    )
