"""ewb_sync: read EWB-USA volunteer opportunities from Salesforce for RTX Benevity.

Module map (each file has one job):
    config.py      settings and credentials from environment variables
    errors.py      the exceptions this package raises
    http.py        raw HTTP calls (standard library only)
    auth.py        Salesforce OAuth login
    client.py      generic Salesforce SOQL client
    models.py      VolunteerOpportunity + which fields to fetch  <- add fields here
    repository.py  queries for volunteer opportunities
    cli.py         command-line interface
"""
