"""Settings for connecting to the EWB-USA Salesforce sandbox.

Everything that might change between environments lives here, so the rest
of the code never hard-codes a URL or reads an environment variable itself.
Secrets come from environment variables only; they are never written in code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ewb_sync.errors import ConfigError

# The .env file is looked for in the folder you run the command from.
DOTENV_FILENAME = ".env"

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


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines from a .env file into the environment.

    Works the same on Windows, macOS, and Linux, so nobody has to "source"
    the file first. Variables already set in the shell win over the file.
    Blank lines and lines starting with # are ignored.
    """
    if not path.is_file():
        return
    # utf-8-sig quietly drops the invisible marker Windows Notepad adds to files.
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def load_settings() -> Settings:
    """Build Settings from the .env file and environment variables.

    Raises ConfigError if the consumer key or secret is missing.
    """
    dotenv_path = Path.cwd() / DOTENV_FILENAME
    load_dotenv(dotenv_path)

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
            + ". Put them in "
            + (str(dotenv_path) if dotenv_path.is_file() else f"a {DOTENV_FILENAME} file (none found at {dotenv_path})")
            + " or set them in your shell. Use the Consumer Key and Consumer Secret from EWB-USA."
        )

    return Settings(
        client_id=client_id,
        client_secret=client_secret,
        login_url=os.environ.get(ENV_LOGIN_URL, DEFAULT_LOGIN_URL).rstrip("/"),
        api_version=os.environ.get(ENV_API_VERSION, DEFAULT_API_VERSION),
    )
