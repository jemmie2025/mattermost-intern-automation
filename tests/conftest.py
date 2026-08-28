from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture()
def settings() -> Settings:
    project_root = Path(__file__).resolve().parents[1]
    return Settings(
        app_env="test",
        database_url="sqlite+pysqlite:///:memory:",
        faq_path=project_root / "config" / "faqs.yaml",
        scheduler_enabled=False,
        attendance_channel_id="attendance-test",
        mentor_channel_id="mentor-test",
        checkin_token="test-checkin",
        checkout_token="test-checkout",
        task_token="test-task",
        faq_token="test-faq",
        outgoing_webhook_token="test-webhook",
        action_token="test-action",
        admin_api_key="test-admin-key",
        automation_api_key="test-automation-key",
        mentor_user_ids=("mentor-1",),
    )


@pytest.fixture()
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def slash_payload(
    *, token: str, text: str = "", user_id: str = "intern-1", username: str = "jemimah"
) -> dict[str, str]:
    return {
        "token": token,
        "team_id": "team-test",
        "team_domain": "interns",
        "channel_id": "channel-test",
        "channel_name": "intern-bot-test",
        "user_id": user_id,
        "user_name": username,
        "text": text,
    }
