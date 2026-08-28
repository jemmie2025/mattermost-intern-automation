# Mattermost Intern Automation — Task #5247

A production-oriented PoC for attendance, daily worklogs, mentor digests, and approved onboarding FAQs on self-hosted Mattermost.

## Proof at a Glance

| Result | Evidence |
|---|---|
| Three required modules implemented | Check-in/out, worklog/digest, FAQ slash + keyword |
| Automated verification | **16 tests passed** |
| Test depth | **87.56% coverage including branches** |
| Runtime proof | End-to-end local API smoke test passed |
| Orchestration | Inactive-by-default n8n schedule template with machine authentication |
| Deployment | Non-root FastAPI container + PostgreSQL Compose stack |
| CI/security | SHA-pinned GitHub Actions, Ruff, preflight and dependency checks |
| Production planning | Architecture, runbook, demo plan, and 12 Jira-ready stories |

## What It Does

| Module | User experience | Control |
|---|---|---|
| Attendance | `/checkin [note]`, `/checkout [note]` | UTC timestamps, Lagos business date, duplicate/order protection |
| Worklog | `/task completed \| blockers \| next plan` | One updateable daily record and scheduled mentor digest |
| FAQ | `/faq vpn` or `vpn setup` | Approved YAML answers only; safe fallback for unknown questions |

## Selected Design

**n8n orchestration + Python/FastAPI policy service + dedicated Mattermost bot + REST API v4 + slash commands + PostgreSQL.**

n8n owns schedules; FastAPI owns validation, authorization, data, exports, audit events,
and Mattermost API calls. This avoids placing business rules or bot tokens inside workflows.
The Apps Framework was rejected because its official repository is deprecated; a server
plugin is unnecessarily privileged for this scope.

## Verify Locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/python scripts/preflight.py
.venv/bin/pytest --cov=app --cov-report=term-missing
```

Expected result:

```text
16 passed
Total coverage: 87.56%
```

Run the API smoke test:

```bash
mkdir -p data
SCHEDULER_ENABLED=false \
DATABASE_URL=sqlite+pysqlite:///./data/intern_bot.db \
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8080

# In another terminal
bash scripts/smoke_test.sh
```

## Docker

```bash
cp .env.example .env
# Replace placeholders with approved TEST values only.
docker compose config
docker compose up --build -d
curl --fail http://127.0.0.1:8080/health/ready
```

Never commit `.env`, bot tokens, webhook URLs, passwords, internal hostnames, or production data.

## Reviewer Route

1. Read [Submission Summary](docs/SUBMISSION_SUMMARY.md).
2. Review [Architecture](docs/ARCHITECTURE.md).
3. Run the tests and [Demo Plan](docs/DEMO_AND_VALIDATION.md).
4. Use the [Maintenance Guide](docs/MAINTENANCE_GUIDE.md).
5. Import the [Jira Backlog](docs/jira-import.csv).
6. Complete the [Live Access Checklist](docs/LIVE_ACCESS_CHECKLIST.md).
7. Follow the [Private GitHub Publication Guide](docs/GITHUB_PUBLISH.md).
8. Import the inactive [n8n schedule template](n8n/README.md).

## Honest Completion Status

The design, code, tests, documentation, and backlog are complete. Final Definition of Done still requires company access for:

- exact Mattermost 11.10 patch version and edition confirmation;
- live test-channel connection and stakeholder demonstration;
- n8n credential selection and manual execution proof;
- Confluence publication/review;
- Jira import.

No production administrator credentials are required.
