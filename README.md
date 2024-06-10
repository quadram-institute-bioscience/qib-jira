# Fetching records from QIB Cloud Jira to a local database
## Installation

`poetry` is required to install (more details https://python-poetry.org/docs/basic-usage/#using-poetry-run)

```
curl -sSL https://install.python-poetry.org | python3 -
```

```
git clone https://github.com/quadram-institute-bioscience/qib-jira
cd qib-jira
poetry run python qib-jira.py --help
```

## Usage

```bash
usage: qib-jira.py [-h] [--email EMAIL] [--token TOKEN] [--database DATABASE] [--project PROJECT] [--days DAYS] [--schedule SCHEDULE]
                   [--health-check HEALTH_CHECK]

Download records from Cloud JIRA to a local sqlite database

options:
  -h, --help            show this help message and exit
  --email EMAIL         JIRA Cloud Admin Email (default: None)
  --token TOKEN         JIRA Cloud API Token (default: None)
  --database DATABASE   Location of the database file (default: qib-jira.db)
  --project PROJECT     Project name (default: BSUP)
  --days DAYS           Number of days to query (default: 30)
  --schedule SCHEDULE   Run this script as a cron job every X minutes (default: None)
  --health-check HEALTH_CHECK
                        Provide a health check URL to perform a health check when you run this script as a scheduled job (Optional) (default: None)
```

Several parameters can be defined using a `.env` at the same location of the script `qib-jira.py`, like below:

```
JIRA_TOKEN="replace-me"
JIRA_EMAIL="replace-me"
HEALTH_CHECK_URL="replace-me"
```
**How to create JIRA api token?** See https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/

If the https://healthchecks.io/ URL is provided, the script will ping the service every time it completes successfully. If Healthchecks does not receive any ping, the service will report that the script failed to run. See [Dead man's switch](https://en.wikipedia.org/wiki/Dead_man%27s_switch).


## Examples

- Download all records within last 365 days

```
poetry run python qib-jira.py --database ./qib-jira.db --email thanh.le-viet[at]quadram[dot]ac[dot]uk --token my-token --days 365
```

If email, token were defined in `.env`, the command would be

```
poetry run python qib-jira.py --database ./qib-jira.db --days 365
```


- Download records within (default) last 30 days every 30 minutes

```
poetry run python qib-jira.py --database ./qib-jira.db --email thanh.le-viet[at]quadram[dot]ac[dot]uk --token my-token --schedule 30
```