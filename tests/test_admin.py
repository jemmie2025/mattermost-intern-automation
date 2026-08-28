from datetime import datetime
from zoneinfo import ZoneInfo

from tests.conftest import slash_payload


def _admin_headers() -> dict[str, str]:
    return {
        "X-Admin-Key": "test-admin-key",
        "X-Mattermost-User-ID": "mentor-1",
    }


def test_attendance_export_is_mentor_restricted(client):
    client.post(
        "/mattermost/commands/checkin",
        data=slash_payload(token="test-checkin"),
    )
    today = datetime.now(ZoneInfo("Africa/Lagos")).date().isoformat()
    endpoint = f"/admin/exports/attendance?start_date={today}&end_date={today}"

    unauthorized = client.get(endpoint)
    assert unauthorized.status_code == 403

    wrong_user = client.get(
        endpoint,
        headers={
            "X-Admin-Key": "test-admin-key",
            "X-Mattermost-User-ID": "intern-1",
        },
    )
    assert wrong_user.status_code == 403

    authorized = client.get(endpoint, headers=_admin_headers())
    assert authorized.status_code == 200
    assert "text/csv" in authorized.headers["content-type"]
    assert "mattermost_user_id" in authorized.text
    assert "intern-1" in authorized.text


def test_faq_reload_requires_mentor_authorization(client):
    response = client.post("/admin/faqs/reload", headers=_admin_headers())
    assert response.status_code == 200
    assert response.json()["active_entries"] >= 3


def test_worklog_export_digest_and_connection_checks(client, monkeypatch):
    client.post(
        "/mattermost/commands/task",
        data=slash_payload(
            token="test-task",
            text="Finished architecture | None | Run stakeholder demo",
        ),
    )
    today = datetime.now(ZoneInfo("Africa/Lagos")).date().isoformat()
    export = client.get(
        f"/admin/exports/worklogs?start_date={today}&end_date={today}",
        headers=_admin_headers(),
    )
    assert export.status_code == 200
    assert "Finished architecture" in export.text

    monkeypatch.setattr(
        client.app.state.mattermost_client,
        "post_message",
        lambda channel_id, message: {"id": "post-123"},
    )
    digest = client.post(
        f"/admin/digests/{today}",
        headers=_admin_headers(),
    )
    assert digest.status_code == 200
    assert digest.json() == {"status": "published", "post_id": "post-123"}

    monkeypatch.setattr(
        client.app.state.mattermost_client,
        "connection_check",
        lambda: {"id": "bot-123", "username": "intern-automation"},
    )
    connection = client.get(
        "/admin/mattermost-connection", headers=_admin_headers()
    )
    assert connection.status_code == 200
    assert connection.json()["bot_username"] == "intern-automation"


def test_invalid_export_date_range(client):
    response = client.get(
        "/admin/exports/attendance?start_date=2026-08-02&end_date=2026-08-01",
        headers=_admin_headers(),
    )
    assert response.status_code == 422
