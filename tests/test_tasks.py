from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from app.models import TaskLog
from tests.conftest import slash_payload


def test_task_submission_update_and_digest(client):
    invalid = client.post(
        "/mattermost/commands/task",
        data=slash_payload(token="test-task", text="Only completed work"),
    )
    assert invalid.status_code == 200
    assert "Use `/task" in invalid.json()["text"]

    submitted = client.post(
        "/mattermost/commands/task",
        data=slash_payload(
            token="test-task",
            text="Researched Mattermost APIs | None | Build the PoC",
        ),
    )
    assert submitted.status_code == 200
    assert "worklog submitted" in submitted.json()["text"]

    updated = client.post(
        "/mattermost/commands/task",
        data=slash_payload(
            token="test-task",
            text="Researched and documented APIs | Waiting for test access | Run integration test",
        ),
    )
    assert updated.status_code == 200
    assert "worklog updated" in updated.json()["text"]

    with client.app.state.database.session_factory() as db:
        count = db.scalar(select(func.count()).select_from(TaskLog))
        today = datetime.now(ZoneInfo("Africa/Lagos")).date()
        digest = client.app.state.task_service.render_digest(db, today)
    assert count == 1
    assert "@jemimah" in digest
    assert "Waiting for test access" in digest

