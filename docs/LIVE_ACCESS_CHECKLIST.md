# Live Access Checklist

Only these company-controlled items remain before the stakeholder demo.

| Required confirmation | Minimum access/evidence |
|---|---|
| Mattermost platform | v11.10 confirmed; capture exact patch, edition and topology |
| Test boundary | Intern test channel and restricted mentor channel |
| Bot identity | Dedicated bot securely provisioned and added only to required channels |
| Integrations | Four slash commands and one outgoing FAQ webhook enabled |
| Network | HTTPS callback reachable with approved CA validation |
| Schedule | Business timezone, working days and reminder/digest times |
| Authorization | Approved mentor/admin Mattermost user IDs or group source |
| Repository | Designated private GitHub repository |
| Publication | Confluence edit/review and Jira import permission |
| n8n | Company environment confirmed; configure restricted credential and manual-node proof |

Do not request or accept production administrator passwords. A Mattermost administrator can
provision the bot and integrations while granting the intern only test-channel access.

Do not place the shared n8n login, bot token, automation key, or invitation URL in GitHub,
Redmine, Confluence, screenshots, workflow JSON, or chat messages.

## Final Live Commands

```text
/checkin Starting PoC validation
/task Completed PoC | None | Complete stakeholder review
/faq vpn
/checkout PoC validation complete
```

Capture only redacted evidence listed in `docs/DEMO_AND_VALIDATION.md`.
