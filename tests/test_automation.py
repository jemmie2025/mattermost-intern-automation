from datetime import datetime
from zoneinfo import ZoneInfo


def _automation_headers() -> dict[str, str]:
    return {"X-Automation-Key": "test-automation-key"}


def test_n8n_reminder_requires_machine_authentication(client, monkeypatch):
    unauthorized = client.post("/automation/reminders/checkin")
    assert unauthorized.status_code == 401

    monkeypatch.setattr(
        client.app.state.mattermost_client,
        "post_message",
        lambda channel_id, message: {"id": "reminder-123"},
    )
    response = client.post(
        "/automation/reminders/checkin", headers=_automation_headers()
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "published",
        "reminder_type": "checkin",
        "post_id": "reminder-123",
    }


def test_n8n_digest_uses_business_date(client, monkeypatch):
    monkeypatch.setattr(
        client.app.state.mattermost_client,
        "post_message",
        lambda channel_id, message: {"id": "digest-123"},
    )
    response = client.post(
        "/automation/digests/today", headers=_automation_headers()
    )
    assert response.status_code == 200
    expected_date = datetime.now(ZoneInfo("Africa/Lagos")).date().isoformat()
    assert response.json() == {
        "status": "published",
        "business_date": expected_date,
        "post_id": "digest-123",
    }
