# Security Policy

## Supported Scope

This repository is a proof of concept. Production release requires the controls in
`docs/JIRA_BACKLOG.md`, including approved identity groups, migrations, retention,
backup/restore, observability, image scanning, and staging security review.

## Report a Security Issue

Report suspected vulnerabilities privately to the project technical lead or the
organization's security channel. Do not open a public issue containing credentials,
internal URLs, personal data, exploit details, or screenshots from production.

## Credential Rules

- Never commit `.env`, bot tokens, webhook URLs, n8n credentials, database passwords,
  private keys, or PATs.
- Use a dedicated least-privilege Mattermost bot, never a human/system-admin account.
- Store secrets in the approved runtime secret mechanism.
- Give n8n only the dedicated automation key; never store the bot token in workflow JSON.
- Rotate any credential exposed in chat, logs, screenshots, Jira, Confluence, or Git.
- Use test credentials and isolated channels for PoC demonstration.

## Data Rules

- Use Mattermost user IDs as authoritative identities.
- Restrict attendance/worklog exports to approved mentors.
- Do not log worklog bodies or secrets.
- Apply the approved retention, correction, backup, and deletion policy before production.
