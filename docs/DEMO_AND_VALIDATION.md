# PoC Demo and Validation

## Proven Locally

```text
16 tests passed
Coverage including branches: 87.56%
Local end-to-end API smoke test: PASSED
Ruff lint and 16-check repository preflight: PASSED
FAQ YAML, Compose YAML, Jira CSV, compileall and pip check: PASSED
```

Verified cases include authentication failure, check-out before check-in, duplicates,
check-in/out, task creation/update, digest generation, FAQ slash/keyword matching, safe
fallback, mentor authorization, n8n machine authentication, exports, configuration safety,
and health checks.

## Stakeholder Demo — 10 Minutes

| Step | Action | Expected proof |
|---:|---|---|
| 1 | Open `/health/ready` | Database ready; Mattermost configured |
| 2 | Manually run n8n check-in node | One reminder appears in the test channel |
| 3 | Run `/checkout` first | Safely rejected |
| 4 | Run `/checkin Starting PoC demo` | Correct date and local time |
| 5 | Repeat `/checkin` | Duplicate rejected |
| 6 | Run `/task Built PoC \| None \| Complete review` | Worklog confirmed |
| 7 | Run `/faq vpn` | Approved VPN answer |
| 8 | Post `vpn setup` in test channel | Same approved keyword response |
| 9 | Run `/checkout Demo complete` | Correct check-out recorded |
| 10 | Run n8n digest and attempt export as intern | Digest posts; export returns 403 |

## Evidence to Capture

- [ ] Redacted Mattermost version/edition
- [ ] Health and bot identity checks
- [ ] n8n manual execution with credentials and URLs redacted
- [ ] Check-in, duplicate rejection, and check-out
- [ ] Worklog and restricted mentor digest
- [ ] FAQ slash and keyword responses
- [ ] Redacted CSV with correct ID/timestamps
- [ ] Unauthorized export rejection
- [ ] Technical-lead approval

Never capture tokens, webhook URLs, private hostnames, unrelated users, or sensitive worklog text.

## Definition-of-Done Status

| Item | Status |
|---|:---:|
| Research, architecture, PoC, tests, guide, backlog | ✅ Complete |
| Live company Mattermost demonstration | ⏳ Access required |
| Exact infrastructure compatibility confirmation | ⏳ Access required |
| Confluence review and Jira import | ⏳ Permission required |
