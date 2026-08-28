# Mattermost Intern Bot — Maintenance Guide

## User Commands

| Action | Command |
|---|---|
| Start work | `/checkin [optional note]` |
| End work | `/checkout [optional note]` |
| Daily worklog | `/task completed \| blockers or None \| next plan` |
| FAQ menu | `/faq` |
| FAQ answer | `/faq vpn` |

Confirmations are ephemeral. Mentor summaries go only to the restricted mentor channel.

## Update an FAQ

Edit `config/faqs.yaml`, preserving indentation:

```yaml
- topic: timesheets
  title: Timesheet Submission
  keywords:
    - submit timesheet
    - timesheet deadline
  answer: >-
    Submit the approved form before the published deadline.
```

Then an authorized maintainer calls:

```text
POST /admin/faqs/reload
```

Test `/faq timesheets` in the test channel. Never put passwords, VPN profiles, tokens, private URLs, or personal data in an FAQ.

## Export Records

Use an approved workstation and destination:

```bash
export BOT_ADMIN_KEY='retrieve-from-secret-store'
export MENTOR_ID='your-mattermost-user-id'

curl --fail \
  -H "X-Admin-Key: ${BOT_ADMIN_KEY}" \
  -H "X-Mattermost-User-ID: ${MENTOR_ID}" \
  "https://bot.example.internal/admin/exports/attendance?start_date=2026-08-01&end_date=2026-08-31" \
  -o attendance-2026-08.csv

unset BOT_ADMIN_KEY MENTOR_ID
```

Use `/admin/exports/worklogs` for worklogs. All exports are date-scoped and audited.

## Schedule

```text
BUSINESS_TIMEZONE=Africa/Lagos
CHECKIN_TIME=08:30
WORKLOG_TIME=16:30
CHECKOUT_TIME=17:00
DIGEST_TIME=17:15
```

n8n is the live scheduler. Import and configure `n8n/workflows/intern-automation-schedules.json`
using `n8n/README.md`. Keep `SCHEDULER_ENABLED=false` on the bot. Change schedules only
through an approved n8n workflow revision and test each changed node manually before activation.

## Fast Troubleshooting

| Problem | Check |
|---|---|
| Command verification failed | Correct endpoint-to-command token mapping |
| Reminder missing | n8n execution, workflow timezone, API response, channel ID, bot membership |
| Duplicate reminder | Confirm bot `SCHEDULER_ENABLED=false` and only one n8n workflow is active |
| FAQ no match | Topic/keyword spelling and YAML validation |
| Export returns 403 | Admin key and mentor user allowlist; never bypass |
| Mattermost returns 401 | Bot token status/rotation |
| Mattermost returns 403 | Bot channel membership and permission |
| Readiness fails | PostgreSQL health and credentials |

Health checks:

```bash
curl --fail https://bot.example.internal/health/live
curl --fail https://bot.example.internal/health/ready
```

## Operating Rules

- Never commit `.env` or send secrets through chat, Jira, Confluence, email, screenshots, or logs.
- Rotate any exposed credential immediately.
- Back up PostgreSQL, encrypt backups, and test restoration.
- Apply the HR-approved retention and correction policy; never silently alter attendance.
- For rollback, disable commands/webhook and stop the bot. Do not delete the database volume.
