# tests/test_sessions.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from typing import Any, Dict, List, Union

client: TestClient = TestClient(app)


def test_get_sessions_returns_list() -> None:
    response = client.get("/sessions")
    assert response.status_code == 200

    data: Union[List[Dict[str, Any]], Any] = response.json()
    assert isinstance(data, list)
    for item in data:
        assert isinstance(item, dict)
        assert "id" in item
        assert "name" in item
        assert item["status"] in ["completed", "running", "failed", "pending"]
        assert "lastRun" in item


def test_get_session_by_id() -> None:
    all_sessions: List[Dict[str, Any]] = client.get("/sessions").json()
    if not all_sessions:
        pytest.skip("No sessions found to fetch")
    session_id: str = all_sessions[0]["id"]

    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    session: Dict[str, Any] = response.json()
    assert session["id"] == session_id
    assert "config" in session
    assert "logs" in session


def test_get_session_invalid_id() -> None:
    response = client.get("/sessions/does-not-exist")
    assert response.status_code == 404
