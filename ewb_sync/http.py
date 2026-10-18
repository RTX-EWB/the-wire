"""Tiny JSON-over-HTTP helpers built on the standard library.

Keeping raw HTTP here means auth.py and client.py read like plain logic,
and swapping in a library such as `requests` later only touches this file.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

REQUEST_TIMEOUT_SECONDS = 30


class HttpError(Exception):
    """An HTTP call returned an error status or couldn't connect."""

    def __init__(self, status: int | None, body: str):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")


def post_form(url: str, form: dict[str, str]) -> dict:
    """POST form-encoded data and return the JSON response."""
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(form).encode(),
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return _send(request)


def get_json(url: str, params: dict[str, str], bearer_token: str) -> dict:
    """GET a URL with query parameters and a bearer token; return the JSON response."""
    full_url = f"{url}?{urllib.parse.urlencode(params)}" if params else url
    request = urllib.request.Request(
        full_url,
        headers={"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"},
    )
    return _send(request)


def _send(request: urllib.request.Request) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise HttpError(error.code, error.read().decode(errors="replace")) from error
    except urllib.error.URLError as error:
        raise HttpError(None, f"Could not connect: {error.reason}") from error
