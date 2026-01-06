"""
Session management for tracking active voice agent sessions.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from ..utils.logger import logger
from ..utils.exceptions import SessionException


@dataclass
class Session:
    """Represents an active voice agent session."""

    session_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    openai_ws: Optional[Any] = None
    client_ws: Optional[Any] = None
    conversation_items: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """
        Check if session has expired.

        Args:
            timeout_minutes: Timeout in minutes

        Returns:
            True if session has expired
        """
        delta = datetime.utcnow() - self.last_activity
        return delta > timedelta(minutes=timeout_minutes)

    async def cleanup(self):
        """Clean up session resources."""
        logger.info(f"Cleaning up session: {self.session_id}")

        # Close OpenAI WebSocket
        if self.openai_ws:
            try:
                await self.openai_ws.close()
            except Exception as e:
                logger.error(f"Error closing OpenAI WebSocket: {e}")

        # Clear conversation history
        self.conversation_items.clear()
        self.metadata.clear()

        logger.info(f"Session cleaned up: {self.session_id}")

    @property
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds()


class SessionManager:
    """
    Manages active voice agent sessions.
    """

    def __init__(self, timeout_minutes: int = 60):
        """
        Initialize session manager.

        Args:
            timeout_minutes: Session timeout in minutes
        """
        self._sessions: Dict[str, Session] = {}
        self._timeout_minutes = timeout_minutes
        self._cleanup_task: Optional[asyncio.Task] = None
        logger.info(f"Session manager initialized (timeout: {timeout_minutes} minutes)")

    def create_session(self, session_id: str) -> Session:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier

        Returns:
            Created session

        Raises:
            SessionException: If session already exists
        """
        if session_id in self._sessions:
            raise SessionException(f"Session '{session_id}' already exists")

        session = Session(session_id=session_id)
        self._sessions[session_id] = session
        logger.info(f"Created session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session.

        Args:
            session_id: Session identifier

        Returns:
            Session or None if not found
        """
        return self._sessions.get(session_id)

    async def remove_session(self, session_id: str) -> bool:
        """
        Remove and cleanup a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was removed
        """
        session = self._sessions.pop(session_id, None)
        if session:
            await session.cleanup()
            logger.info(f"Removed session: {session_id}")
            return True
        return False

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        expired = [
            session_id for session_id, session in self._sessions.items()
            if session.is_expired(self._timeout_minutes)
        ]

        for session_id in expired:
            logger.info(f"Session expired: {session_id}")
            await self.remove_session(session_id)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

    async def start_cleanup_loop(self, interval_seconds: int = 300):
        """
        Start background task for cleaning up expired sessions.

        Args:
            interval_seconds: Cleanup interval in seconds
        """
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(interval_seconds)
                    await self.cleanup_expired_sessions()
                except asyncio.CancelledError:
                    logger.info("Session cleanup loop cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {e}", exc_info=True)

        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info(f"Started session cleanup loop (interval: {interval_seconds}s)")

    async def stop_cleanup_loop(self):
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped session cleanup loop")

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        return len(self._sessions)

    @property
    def session_ids(self) -> list:
        """Get list of active session IDs."""
        return list(self._sessions.keys())


# Global session manager instance
session_manager = SessionManager()
