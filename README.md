# ewb_sync

Pulls EWB-USA volunteer opportunities from their Salesforce sandbox so they can
be brought into RTX's Benevity. Today it retrieves each opportunity's **name**;
more fields are easy to add (see [Adding a field](#adding-a-field)).

---

## 1. What you need

- **Python 3.10 or newer.** Check with `python3 --version` (Windows: `py --version`).
- **Salesforce credentials:** a Consumer Key and Consumer Secret from EWB-USA,
  delivered through a secure channel. Ask the project lead if you don't have them.

That's it. The code uses only the Python standard library, so there are no
packages to install.

## 2. Get the code

Clone the repo (or unzip the folder) and move into it:

```bash
cd the-wire
```

All commands below are run from this folder.

## 3. Create a virtual environment (recommended)

Not strictly needed today, but it keeps things clean once dependencies get added.

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Your prompt should now start with `(.venv)`. Run `deactivate` to leave it.

## 4. Add your credentials

Copy the example file and fill in the two values:

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

```ini
SF_CLIENT_ID=<Consumer Key>
SF_CLIENT_SECRET=<Consumer Secret>
```

`.env` is in `.gitignore`. **Never commit it, paste it in chat, or put secrets in code.**

Load it into your terminal session (do this in every new terminal):

**macOS / Linux**
```bash
set -a; source .env; set +a
```

**Windows (PowerShell)**
```powershell
Get-Content .env | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    Set-Item "env:$($name.Trim())" $value.Trim()
}
```

## 5. Check that everything works

**Run the tests.** These use a fake Salesforce, so they pass even without credentials:

```bash
python3 -m unittest discover tests
```

You should see `OK`.

**Talk to the real sandbox:**

```bash
python3 -m ewb_sync list
```

You should see record Ids and names, for example:

```
a2HUN00000Lw05E2AR  Navajo Nation, AZ - Livestock Water Storage Project
```

On Windows, use `py` instead of `python3` in every command.

## 6. Play around

**Command line**

```bash
python3 -m ewb_sync list                      # 10 most recently modified opportunities
python3 -m ewb_sync list --limit 25           # more of them
python3 -m ewb_sync name a2HUN00000Lw05E2AR   # just the name of one opportunity
python3 -m ewb_sync --help
```

**Python shell.** Start `python3` in this folder (with `.env` loaded), then:

```python
from ewb_sync.cli import connect

repo = connect()                       # logs in to Salesforce
opps = repo.list_recent(5)
for opp in opps:
    print(opp.id, opp.name)

repo.get_by_id(opps[0].id)             # fetch one by Id
```

**Raw SOQL**, for exploring fields before adding them to the code:

```python
from ewb_sync.auth import authenticate
from ewb_sync.client import SalesforceClient
from ewb_sync.config import load_settings

settings = load_settings()
client = SalesforceClient(authenticate(settings), settings.api_version)
client.query("SELECT Id, Name, Active__c FROM Volunteer_Opportunity__c LIMIT 5")
```

The integration user is **read-only**, so you can't break anything in
Salesforce. If you need test opportunities, ask EWB-USA (Yoshi Akutsu,
yoshi.akutsu@ewb-usa.org) to create them in the sandbox.

## 7. How the code is organized

A request flows top to bottom. Each file has one job:

| File | Job |
|---|---|
| `ewb_sync/cli.py` | Parses commands, wires everything together, prints results |
| `ewb_sync/repository.py` | The only place SOQL is written; returns model objects |
| `ewb_sync/models.py` | `VolunteerOpportunity` and which fields to fetch |
| `ewb_sync/client.py` | Runs any SOQL query, following result pages |
| `ewb_sync/auth.py` | OAuth client-credentials login |
| `ewb_sync/http.py` | Raw HTTP calls |
| `ewb_sync/config.py` | Reads settings and credentials from environment variables |
| `ewb_sync/errors.py` | The package's named exceptions |
| `tests/` | Unit tests with a fake Salesforce |

## Adding a field

Everything happens in `ewb_sync/models.py`:

1. Add a line to `FIELD_MAP`, for example `"active": "Active__c",`
2. Add the matching attribute to `VolunteerOpportunity`, for example `active: bool`

The query picks it up automatically. Field API names are in the EWB-USA
Salesforce Data Dictionary (object `Volunteer_Opportunity__c`). Good next
candidates: `Active__c`, `Description__c` (HTML), `LastModifiedDate`.

Run the tests again after any change.

## Troubleshooting

| Problem | Likely cause / fix |
|---|---|
| `Missing environment variable(s): SF_CLIENT_ID...` | `.env` isn't loaded in this terminal. Repeat the load step in section 4. |
| `Salesforce login failed (HTTP 400): invalid_client...` | Key or secret is wrong, has extra spaces, or was rotated. Re-copy them. |
| `Salesforce request failed (HTTP 400): INVALID_FIELD...` | A field name in `FIELD_MAP` is misspelled or the integration user can't see it. Check the data dictionary. |
| `Could not connect` or SSL certificate errors | Usually a corporate proxy. Try off VPN or set `HTTPS_PROXY`; for certificate errors, point `SSL_CERT_FILE` at your company's CA bundle. |
| `SyntaxError` on startup | Python is older than 3.10. Check `python3 --version`. |
| `No module named ewb_sync` | You're not in the `the-wire` folder. |

## Optional settings

Set these in `.env` only if you need to override the defaults:

| Variable | Default |
|---|---|
| `SF_LOGIN_URL` | `https://ewb-usa--benevity.sandbox.my.salesforce.com` |
| `SF_API_VERSION` | `v65.0` |
