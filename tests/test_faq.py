from tests.conftest import slash_payload


def test_faq_slash_command_and_topic_menu(client):
    match = client.post(
        "/mattermost/commands/faq",
        data=slash_payload(token="test-faq", text="vpn"),
    )
    assert match.status_code == 200
    assert "VPN Setup" in match.json()["text"]

    menu = client.post(
        "/mattermost/commands/faq",
        data=slash_payload(token="test-faq", text=""),
    )
    assert menu.status_code == 200
    assert "Available FAQ topics" in menu.json()["text"]
    assert "`vpn`" in menu.json()["text"]


def test_faq_keyword_webhook(client):
    response = client.post(
        "/mattermost/webhooks/faq-keyword",
        json={
            "token": "test-webhook",
            "text": "vpn setup",
            "trigger_word": "vpn",
            "user_id": "intern-1",
        },
    )
    assert response.status_code == 200
    assert response.json()["response_type"] == "comment"
    assert "VPN Setup" in response.json()["text"]


def test_unknown_faq_has_safe_fallback(client):
    response = client.post(
        "/mattermost/commands/faq",
        data=slash_payload(token="test-faq", text="private payroll password"),
    )
    assert response.status_code == 200
    assert "No approved FAQ matched" in response.json()["text"]

