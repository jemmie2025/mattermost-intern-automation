# Task #5247 — Intern Automation Bots for Self-Hosted Mattermost

Research, architecture, and proof of concept for attendance, worklogs, mentor reporting, onboarding FAQs, and Mattermost automation.

## Verified Results

| Area | Outcome |
|---|---|
| Application | Attendance, worklog/digest, and FAQ modules implemented |
| Local validation | 16 tests passed; reported coverage: 87.56%; API and container health checks passed |
| CI | GitHub Actions passed with SHA-pinned actions, Ruff, preflight, and dependency checks |
| Native Mattermost form | `/quiz` opens an interactive dialog directly inside Mattermost |
| Submission | n8n receives the form data, posts it through the bot, and returns a successful response |
| Reusability | Earlier sanitized custom-form template imported successfully |

## Architecture

The application uses FastAPI for policy logic, with PostgreSQL and the Mattermost API as integration targets.

The verified native form runs through two independent n8n webhook flows:

```text
/quiz → Open webhook → Mattermost dialog → Response
Submit → Submission webhook → Bot channel post → Response
```

Users complete the form inside Mattermost. This proof of concept records participant, quiz name, and an entered score; it does not calculate quiz scores.

## Evidence

### Native Form Inside Mattermost

![Native Mattermost quiz dialog](docs/evidence/task5247-quiz-form.png)

### Successful n8n Execution

![Submission workflow completed successfully](docs/evidence/task5247-n8n-success.png)

### CI Validation

![Successful CI pipeline](docs/evidence/task-5247-phase-2-ci-validation-passed.png)

<details>
<summary>Earlier integration and template evidence</summary>

### n8n → Mattermost

![Successful n8n to Mattermost workflow](docs/evidence/task-5247-n8n-mattermost-e2e-success.png)

### Dynamic Quiz Notification

![Dynamic quiz notification](docs/evidence/task-5247-dynamic-quiz-mattermost-success.png)

### Mock Custom-Form Execution

![Successful custom-form workflow](docs/evidence/task5247_n8n_success.png)

### Mock Custom-Form Notification

![Custom-form notification in Mattermost](docs/evidence/task5247_mattermost_success.png)

### Reusable Template Import

![Sanitized custom-form template imported successfully](docs/evidence/task5247_reusable_template_import.png)

</details>

## Local Verification

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/python scripts/preflight.py
.venv/bin/pytest --cov=app --cov-report=term-missing
```

Recorded result: **16 tests passed, 87.56% coverage**. Live n8n and Mattermost validation is documented separately above.

## Scope and Security

The native form and bot notification were validated in an isolated test channel. Earlier mock-form tests demonstrated notification delivery, not real-user provisioning.

Production rollout and user provisioning remain outside this validation. Workflow exports must be sanitized before committing; credentials belong in n8n’s credential store. Review screenshots for internal information before sharing.