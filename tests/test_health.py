def test_liveness_and_readiness(client):
    live = client.get("/health/live")
    ready = client.get("/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json()["database"] == "ok"
    assert ready.json()["mattermost_configured"] is False

