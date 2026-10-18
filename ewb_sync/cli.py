"""Command-line entry point.

Wires the pieces together (settings -> login -> client -> repository),
then prints results. Contains no Salesforce logic of its own.

Usage:
    python -m ewb_sync name <RECORD_ID>     # name of one opportunity
    python -m ewb_sync list [--limit N]     # Id + name of recent opportunities
"""

from __future__ import annotations

import argparse
import sys

from ewb_sync.auth import authenticate
from ewb_sync.client import SalesforceClient
from ewb_sync.config import load_settings
from ewb_sync.errors import EwbSyncError
from ewb_sync.repository import VolunteerOpportunityRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ewb_sync",
        description="Read EWB-USA volunteer opportunities from Salesforce.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    name_cmd = commands.add_parser("name", help="Print the name of one opportunity.")
    name_cmd.add_argument("record_id", help="Salesforce record Id, e.g. a2HUN00000Lw05E2AR")

    list_cmd = commands.add_parser("list", help="List recently modified opportunities.")
    list_cmd.add_argument("--limit", type=int, default=10, help="How many to show (default 10).")

    return parser


def connect() -> VolunteerOpportunityRepository:
    """Log in to Salesforce and return a ready-to-use repository."""
    settings = load_settings()
    session = authenticate(settings)
    client = SalesforceClient(session, settings.api_version)
    return VolunteerOpportunityRepository(client)


def run_name(repository: VolunteerOpportunityRepository, record_id: str) -> int:
    opportunity = repository.get_by_id(record_id)
    if opportunity is None:
        print(f"No volunteer opportunity found with Id {record_id}.", file=sys.stderr)
        return 1
    print(opportunity.name)
    return 0


def run_list(repository: VolunteerOpportunityRepository, limit: int) -> int:
    opportunities = repository.list_recent(limit)
    if not opportunities:
        print("No volunteer opportunities found.")
        return 0
    for opportunity in opportunities:
        print(f"{opportunity.id}  {opportunity.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repository = connect()
        if args.command == "name":
            return run_name(repository, args.record_id)
        if args.command == "list":
            return run_list(repository, args.limit)
    except EwbSyncError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 2  # unreachable: argparse rejects unknown commands
