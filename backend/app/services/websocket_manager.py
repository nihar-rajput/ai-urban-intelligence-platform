import json
from typing import List
from fastapi import WebSocket
from backend.app.core.logging import logger


class AlertWebSocketManager:
    """
    Manages active WebSocket connections from dashboard browser clients.
    Broadcasts real-time incident alerts and stream telemetry updates.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_alert(self, message: dict):
        """Broadcasts incident or telemetry payload to all active browser connections."""
        if not self.active_connections:
            return

        payload_str = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                logger.warning(f"Failed to send alert via WebSocket: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


ws_manager = AlertWebSocketManager()
