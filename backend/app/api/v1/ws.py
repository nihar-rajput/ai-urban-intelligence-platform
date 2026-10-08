from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.websocket_manager import ws_manager
from backend.app.core.logging import logger

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket feed for live incident alerts and fleet telemetry updates.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; accept any heartbeat pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
