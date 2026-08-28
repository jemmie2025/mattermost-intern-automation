# n8n Orchestration

The company-provided n8n instance runs the weekday schedules. FastAPI remains the
policy and data boundary: it validates machine authentication, applies business
rules, stores records, audits activity, and calls Mattermost with the bot token.

## Safe Import

1. Import `workflows/intern-automation-schedules.json` into the approved n8n project.
2. Keep the workflow inactive while configuring it.
3. Replace `https://REPLACE_WITH_BOT_API_URL` with the approved HTTPS bot API URL.
4. Create an **HTTP Header Auth** credential:
   - Header name: `X-Automation-Key`
   - Header value: the secret stored as `AUTOMATION_API_KEY` on the bot service
5. Select that credential on all four HTTP Request nodes.
6. Confirm the workflow timezone is `Africa/Lagos`.
7. Execute each HTTP node manually against the isolated Mattermost test channel.
8. Activate the workflow only after the test posts and audit events are verified.

The imported workflow is intentionally inactive and contains no credentials,
tokens, internal URLs, user data, or channel IDs.

## Schedule

| Workflow action | Weekday time |
|---|---:|
| Check-in reminder | 08:30 |
| Worklog reminder | 16:30 |
| Check-out reminder | 17:00 |
| Mentor digest | 17:15 |

Set `SCHEDULER_ENABLED=false` on the bot when n8n is active. This prevents duplicate
posts. The internal APScheduler implementation remains available only as a local
fallback.

## Required Network Path

n8n must reach the bot API over approved HTTPS. Mattermost must also reach the bot
API slash-command and FAQ webhook endpoints. Never disable TLS verification to make
the connection work.
