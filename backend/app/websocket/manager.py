"""
WebSocket connection manager for client connections.
"""
from typing import Dict
from fastapi import WebSocket
from ..utils.logger import logger
from ..utils.exceptions import WebSocketException


class ConnectionManager:
    """
    Manages active WebSocket connections from clients.
    """

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        logger.info("Connection manager initialized")

    async def connect(self, websocket: WebSocket, session_id: str):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket connection
            session_id: Unique session identifier

        Raises:
            WebSocketException: If session already has a connection
        """
        if session_id in self.active_connections:
            raise WebSocketException(f"Session '{session_id}' already has an active connection")

        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"Client connected: {session_id}")

    async def disconnect(self, session_id: str):
        """
        Disconnect and remove a WebSocket connection.

        Args:
            session_id: Session identifier
        """
        websocket = self.active_connections.pop(session_id, None)
        if websocket:
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket for session {session_id}: {e}")

            logger.info(f"Client disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """
        Send a JSON message to a specific client.

        Args:
            session_id: Session identifier
            message: Message dictionary to send

        Raises:
            WebSocketException: If session not found
        """
        websocket = self.active_connections.get(session_id)
        if not websocket:
            raise WebSocketException(f"No active connection for session '{session_id}'")

        try:
            await websocket.send_json(message)
            logger.debug(f"Sent message to {session_id}: {message.get('type')}")

        except Exception as e:
            logger.error(f"Failed to send message to {session_id}: {e}")
            raise WebSocketException(f"Send failed: {e}")

    async def send_text(self, session_id: str, text: str):
        """
        Send a text message to a specific client.

        Args:
            session_id: Session identifier
            text: Text message to send
        """
        websocket = self.active_connections.get(session_id)
        if websocket:
            try:
                await websocket.send_text(text)
            except Exception as e:
                logger.error(f"Failed to send text to {session_id}: {e}")

    def is_connected(self, session_id: str) -> bool:
        """
        Check if a session has an active connection.

        Args:
            session_id: Session identifier

        Returns:
            True if connection exists
        """
        return session_id in self.active_connections

    @property
    def connection_count(self) -> int:
        """Get count of active connections."""
        return len(self.active_connections)


# Global connection manager instance
connection_manager = ConnectionManager()
