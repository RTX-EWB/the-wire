"""Custom exceptions.

Each failure type gets its own class so the command line can print a clear
message instead of a stack trace, and so callers can catch exactly what
they care about.
"""


class EwbSyncError(Exception):
    """Base class for every error this package raises on purpose."""


class ConfigError(EwbSyncError):
    """Required settings (like credentials) are missing or invalid."""


class AuthenticationError(EwbSyncError):
    """Salesforce rejected the client credentials."""


class SalesforceApiError(EwbSyncError):
    """A Salesforce REST call failed."""


class InvalidRecordIdError(EwbSyncError):
    """A value that should be a Salesforce record Id isn't one."""
