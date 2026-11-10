"""
WebSocket Connection Manager and Real-time Event Streaming for SwarmDroid
Communicates live swarm events, agent thinking states, and 3D companion cues to Android client.
"""

from typing import List, Dict, Any
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger("swarmdroid.websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Android client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Android client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcasts a structured JSON event to all connected Android clients."""
        payload = json.dumps({
            "type": event_type,
            "data": data
        })
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                self.disconnect(connection)


# Global WebSocket connection manager
ws_manager = ConnectionManager()
