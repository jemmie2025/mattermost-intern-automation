from sqlalchemy import func, select

from app.models import AttendanceRecord
from tests.conftest import slash_payload


def test_checkin_checkout_and_duplicate_protection(client):
    no_checkin = client.post(
        "/mattermost/commands/checkout",
        data=slash_payload(token="test-checkout"),
    )
    assert no_checkin.status_code == 200
    assert "Check in first" in no_checkin.json()["text"]

    checkin = client.post(
        "/mattermost/commands/checkin",
        data=slash_payload(token="test-checkin", text="Starting API research"),
    )
    assert checkin.status_code == 200
    assert "Check-in recorded" in checkin.json()["text"]

    duplicate = client.post(
        "/mattermost/commands/checkin",
        data=slash_payload(token="test-checkin"),
    )
    assert duplicate.status_code == 200
    assert "already recorded" in duplicate.json()["text"]

    checkout = client.post(
        "/mattermost/commands/checkout",
        data=slash_payload(token="test-checkout", text="Worklog submitted"),
    )
    assert checkout.status_code == 200
    assert "Check-out recorded" in checkout.json()["text"]

    with client.app.state.database.session_factory() as db:
        count = db.scalar(select(func.count()).select_from(AttendanceRecord))
    assert count == 2


def test_invalid_command_token_is_rejected(client):
    response = client.post(
        "/mattermost/commands/checkin",
        data=slash_payload(token="wrong-token"),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Request verification failed"

