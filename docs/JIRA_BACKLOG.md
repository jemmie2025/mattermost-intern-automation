# Production Backlog — Mattermost Intern Automation

**Epic:** Securely productionize attendance, daily worklogs, mentor digests, and approved FAQ automation.

| ID | Story | Points | Done when |
|---|---|---:|---|
| MB-01 | Confirm Mattermost readiness | 2 | v11.10 patch, edition, topology, integration settings, test channels and owners recorded without secrets |
| MB-02 | Approve data governance | 3 | HR/security approve fields, visibility, retention, deletion, correction, backup and export rules |
| MB-03 | Provision bot and integrations | 3 | Least-privilege bot, four commands, FAQ webhook, channels and secret rotation owner configured |
| MB-04 | Establish repository and CI gates | 5 | Reviews, tests, lint, secret/dependency/image scans, SBOM and immutable image enabled |
| MB-05 | Add production database migrations | 5 | Alembic upgrade/rollback, indexes and concurrent uniqueness tests pass |
| MB-06 | Productionize attendance and n8n reminders | 8 | Approved timezone, late/duplicate/correction rules, authenticated n8n scheduling and pause control pass |
| MB-07 | Productionize worklogs and n8n digest | 5 | Validation, correction, restricted idempotent n8n digest and missing-submission behavior pass |
| MB-08 | Productionize FAQ lifecycle | 5 | Validate, approve, reload, audit and roll back FAQ content; safe fallback proven |
| MB-09 | Implement mentor RBAC and exports | 5 | Approved group authorization, 403 negative tests, minimized audited exports pass |
| MB-10 | Harden deployment and operations | 8 | TLS, non-root container, private DB, limits, logs, metrics, alerts, backup/restore and retention pass |
| MB-11 | Complete staging UAT/security review | 8 | All roles, workflows, failures and supported-version E2E tests approved with redacted evidence |
| MB-12 | Pilot, rollback and handover | 5 | Pilot metrics, rollback trigger, runbooks, ownership and post-implementation review approved |

**Total estimate:** 62 points. Re-estimate after MB-01 and MB-02 because platform and policy decisions can change scope.

## Delivery Order

1. **Gate:** MB-01–03
2. **Build:** MB-04–09
3. **Production controls:** MB-10
4. **Validate and release:** MB-11–12
