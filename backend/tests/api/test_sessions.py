# tests/test_sessions.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from shared_types.session import SessionStatus

client = TestClient(app)


def test_get_sessions_returns_list():
    response = client.get("/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "id" in item
        assert "name" in item
        assert item["status"] in SessionStatus
        assert "lastRun" in item


def test_get_session_by_id():
    all_sessions = client.get("/sessions").json()
    if not all_sessions:
        pytest.skip("No sessions found to fetch")
    session_id = all_sessions[0]["id"]

    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    session = response.json()
    assert session["id"] == session_id
    assert "config" in session
    assert "logs" in session


def test_get_session_invalid_id():
    response = client.get("/sessions/does-not-exist")
    assert response.status_code == 404


def test_session_has_expected_log_fields():
    all_sessions = client.get("/sessions").json()
    if not all_sessions:
        pytest.skip("No sessions to validate logs")
    session_id = all_sessions[0]["id"]
    detail = client.get(f"/sessions/{session_id}").json()
    for log in detail.get("logs", []):
        assert "timestamp" in log
        assert "type" in log
        assert "source" in log
        assert "details" in log
        assert isinstance(log["details"], dict)


def test_session_with_empty_logs():
    all_sessions = client.get("/sessions").json()
    if not all_sessions:
        pytest.skip("No sessions found")
    session_id = all_sessions[0]["id"]
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    session = response.json()
    logs = session.get("logs", [])
    assert isinstance(logs, list)


def test_session_with_empty_config():
    all_sessions = client.get("/sessions").json()
    if not all_sessions:
        pytest.skip("No sessions found")
    session_id = all_sessions[0]["id"]
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    session = response.json()
    config = session.get("config", {})
    assert isinstance(config, dict)
