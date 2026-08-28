# Private GitHub Publication

Use the company repository if Friendy provides one. Otherwise create a private repository only
after approval.

## Pre-push Gate

```bash
ruff check .
python scripts/preflight.py
pytest --cov=app --cov-report=term-missing
git status --short
```

Confirm `.env`, tokens, internal URLs, passwords, database files and screenshots are absent.

## New Private Repository

```bash
git init -b main
git add .
git commit -m "Build Mattermost intern automation PoC"
gh auth status
gh repo create mattermost-intern-automation --private --source=. --remote=origin --push
```

## Existing Company Repository

```bash
git init -b main
git add .
git commit -m "Build Mattermost intern automation PoC"
git remote add origin <APPROVED_PRIVATE_REPOSITORY_URL>
git push -u origin main
```

After pushing, confirm both GitHub Actions jobs are green before submitting the link.

