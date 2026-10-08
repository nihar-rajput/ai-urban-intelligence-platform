import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.websocket_manager import ws_manager


def test_websocket_alert_stream():
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws/alerts") as websocket:
        # Test heartbeat
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert "pong" in data
