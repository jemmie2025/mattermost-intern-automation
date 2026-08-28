#!/usr/bin/env python3
"""Fast, deterministic repository checks for local use and CI."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label}")
        ERRORS.append(label)


def required_files() -> None:
    required = [
        "README.md",
        "Dockerfile",
        "compose.yaml",
        ".env.example",
        ".gitignore",
        "SECURITY.md",
        ".github/workflows/ci.yml",
        "app/main.py",
        "config/faqs.yaml",
        "docs/ARCHITECTURE.md",
        "docs/SUBMISSION_SUMMARY.md",
        "docs/MAINTENANCE_GUIDE.md",
        "docs/GITHUB_PUBLISH.md",
        "docs/LIVE_ACCESS_CHECKLIST.md",
        "docs/jira-import.csv",
        "n8n/README.md",
        "n8n/workflows/intern-automation-schedules.json",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    check(not missing, "required submission files are present")
    if missing:
        print("      Missing: " + ", ".join(missing))


def validate_faq() -> None:
    payload = yaml.safe_load((ROOT / "config/faqs.yaml").read_text(encoding="utf-8"))
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    topics = [entry.get("topic") for entry in entries if isinstance(entry, dict)]
    complete = all(
        isinstance(entry, dict)
        and entry.get("topic")
        and entry.get("title")
        and entry.get("answer")
        and isinstance(entry.get("keywords"), list)
        for entry in entries
    )
    check(len(entries) >= 3 and complete, "FAQ schema contains complete approved entries")
    check(len(topics) == len(set(topics)), "FAQ topics are unique")


def validate_compose() -> None:
    payload = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    services = payload.get("services", {}) if isinstance(payload, dict) else {}
    bot = services.get("bot", {})
    check(set(services) == {"bot", "postgres"}, "Compose declares bot and PostgreSQL only")
    check(bot.get("read_only") is True, "bot container filesystem is read-only")
    check("ALL" in bot.get("cap_drop", []), "bot container drops Linux capabilities")
    check(
        "no-new-privileges:true" in bot.get("security_opt", []),
        "bot container blocks privilege escalation",
    )


def validate_jira() -> None:
    with (ROOT / "docs/jira-import.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    epics = sum(row.get("Issue Type") == "Epic" for row in rows)
    stories = sum(row.get("Issue Type") == "Story" for row in rows)
    check(epics == 1 and stories == 12, "Jira import contains one epic and 12 stories")


def validate_pinned_actions() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    references = re.findall(r"^\s*uses:\s*[^@\s]+@([^\s#]+)", workflow, re.MULTILINE)
    check(bool(references), "GitHub Actions references are present")
    check(
        all(re.fullmatch(r"[0-9a-f]{40}", reference) for reference in references),
        "GitHub Actions references are pinned to 40-character SHAs",
    )


def validate_n8n_workflow() -> None:
    workflow_path = ROOT / "n8n/workflows/intern-automation-schedules.json"
    payload = json.loads(workflow_path.read_text(encoding="utf-8"))
    nodes = payload.get("nodes", [])
    schedules = [
        node for node in nodes if node.get("type") == "n8n-nodes-base.scheduleTrigger"
    ]
    requests = [
        node for node in nodes if node.get("type") == "n8n-nodes-base.httpRequest"
    ]
    serialized = workflow_path.read_text(encoding="utf-8")
    check(len(schedules) == 4, "n8n workflow declares four schedule triggers")
    check(len(requests) == 4, "n8n workflow declares four authenticated API calls")
    check(payload.get("active") is False, "n8n workflow imports inactive")
    check(
        "REPLACE_WITH_BOT_API_URL" in serialized,
        "n8n workflow contains an explicit API URL placeholder",
    )


def scan_secrets() -> None:
    patterns = [
        re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"/hooks/[a-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
    ]
    excluded_parts = {".git", ".venv", ".pytest_cache", "data", "__pycache__"}
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or excluded_parts.intersection(path.parts):
            continue
        if path.name == ".env" or path.suffix in {".db", ".pyc", ".zip"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(content) for pattern in patterns):
            findings.append(str(path.relative_to(ROOT)))
    check(not findings, "no high-confidence secrets detected")
    if findings:
        print("      Review: " + ", ".join(findings))


def validate_gitignore() -> None:
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    check(".env" in ignored, ".env is excluded from Git")


def main() -> int:
    print("Task #5247 preflight")
    required_files()
    validate_faq()
    validate_compose()
    validate_jira()
    validate_pinned_actions()
    validate_n8n_workflow()
    scan_secrets()
    validate_gitignore()
    if ERRORS:
        print(f"\nPreflight FAILED: {len(ERRORS)} check(s)")
        return 1
    print("\nPreflight PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
