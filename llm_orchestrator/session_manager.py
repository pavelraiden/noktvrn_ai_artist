"""
Session Manager Module

This module provides session management functionality for the orchestrator,
allowing tracking and persistence of orchestration sessions.
"""

import os
import json
import uuid
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path

from .orchestrator import OrchestrationResult, OrchestrationStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("session_manager")


class SessionStatus(Enum):
    """Status of a session."""

    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class Session:
    """
    Represents an orchestration session.

    Attributes:
        id: Unique identifier for the session
        status: Current status of the session
        created_at: When the session was created
        updated_at: When the session was last updated
        expires_at: When the session expires
        metadata: Additional metadata for the session
        orchestrations: Map of orchestration IDs to results
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        ttl_seconds: int = 3600,  # 1 hour default TTL
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new session.

        Args:
            session_id: Unique identifier for the session (generated if None)
            ttl_seconds: Time-to-live in seconds
            metadata: Additional metadata for the session
        """
        self.id = session_id or str(uuid.uuid4())
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
        self.metadata = metadata or {}
        self.orchestrations: Dict[str, OrchestrationResult] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the session to a dictionary."""
        return {
            "id": self.id,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
            "orchestrations": {
                orch_id: orch.to_dict() for orch_id, orch in self.orchestrations.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create a session from a dictionary."""
        session = cls(session_id=data["id"], metadata=data.get("metadata", {}))
        session.status = SessionStatus(data["status"])
        session.created_at = data["created_at"]
        session.updated_at = data["updated_at"]
        session.expires_at = data["expires_at"]

        # Load orchestrations
        for orch_id, orch_data in data.get("orchestrations", {}).items():
            session.orchestrations[orch_id] = OrchestrationResult.from_dict(orch_data)

        return session

    def add_orchestration(self, orchestration: OrchestrationResult) -> None:
        """
        Add an orchestration result to the session.

        Args:
            orchestration: The orchestration result to add
        """
        self.orchestrations[orchestration.id] = orchestration
        self.updated_at = datetime.now().isoformat()

    def get_orchestration(self, orchestration_id: str) -> Optional[OrchestrationResult]:
        """
        Get an orchestration result by ID.

        Args:
            orchestration_id: The ID of the orchestration to get

        Returns:
            The orchestration result, or None if not found
        """
        return self.orchestrations.get(orchestration_id)

    def update_orchestration(self, orchestration: OrchestrationResult) -> None:
        """
        Update an existing orchestration result.

        Args:
            orchestration: The updated orchestration result
        """
        if orchestration.id in self.orchestrations:
            self.orchestrations[orchestration.id] = orchestration
            self.updated_at = datetime.now().isoformat()

    def is_expired(self) -> bool:
        """
        Check if the session has expired.

        Returns:
            True if the session has expired, False otherwise
        """
        expires_at = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expires_at

    def extend_expiry(self, ttl_seconds: int) -> None:
        """
        Extend the session's expiry time.

        Args:
            ttl_seconds: Additional time-to-live in seconds
        """
        expires_at = datetime.fromisoformat(self.expires_at)
        new_expires_at = expires_at + timedelta(seconds=ttl_seconds)
        self.expires_at = new_expires_at.isoformat()
        self.updated_at = datetime.now().isoformat()

    def complete(self) -> None:
        """Mark the session as completed."""
        self.status = SessionStatus.COMPLETED
        self.updated_at = datetime.now().isoformat()

    def fail(self) -> None:
        """Mark the session as failed."""
        self.status = SessionStatus.FAILED
        self.updated_at = datetime.now().isoformat()

    def expire(self) -> None:
        """Mark the session as expired."""
        self.status = SessionStatus.EXPIRED
        self.updated_at = datetime.now().isoformat()


class SessionManager:
    """
    Manages orchestration sessions.

    This class provides functionality for creating, retrieving, updating,
    and persisting sessions.
    """

    def __init__(
        self,
        storage_dir: str = "/tmp/llm_orchestrator/sessions",
        default_ttl_seconds: int = 3600,  # 1 hour default TTL
        cleanup_interval_seconds: int = 300,  # 5 minutes default cleanup interval
    ):
        """
        Initialize a new session manager.

        Args:
            storage_dir: Directory for storing session data
            default_ttl_seconds: Default time-to-live for sessions in seconds
            cleanup_interval_seconds: Interval for cleaning up expired sessions
        """
        self.storage_dir = storage_dir
        self.default_ttl_seconds = default_ttl_seconds
        self.cleanup_interval_seconds = cleanup_interval_seconds
        self.active_sessions: Dict[str, Session] = {}

        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

        # Load existing sessions
        self._load_sessions()

        # Start cleanup task
        self._start_cleanup_task()

        logger.info(
            f"Initialized session manager with storage directory: {storage_dir}"
        )

    def create_session(
        self,
        session_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new session.

        Args:
            session_id: Unique identifier for the session (generated if None)
            ttl_seconds: Time-to-live in seconds (uses default if None)
            metadata: Additional metadata for the session

        Returns:
            The newly created session
        """
        # Use default TTL if not specified
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

        # Create the session
        session = Session(session_id=session_id, ttl_seconds=ttl, metadata=metadata)

        # Store the session
        self.active_sessions[session.id] = session
        self._save_session(session)

        logger.info(f"Created session: {session.id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: The ID of the session to get

        Returns:
            The session, or None if not found
        """
        # Check active sessions first
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]

            # Check if the session has expired
            if session.is_expired():
                session.expire()
                self._save_session(session)
                del self.active_sessions[session_id]
                logger.info(f"Session expired: {session_id}")
                return None

            return session

        # Try to load from storage
        session_path = os.path.join(self.storage_dir, f"{session_id}.json")
        if os.path.exists(session_path):
            try:
                with open(session_path, "r") as f:
                    session_data = json.load(f)

                session = Session.from_dict(session_data)

                # Check if the session has expired
                if session.is_expired():
                    session.expire()
                    self._save_session(session)
                    logger.info(f"Session expired: {session_id}")
                    return None

                # Add to active sessions
                self.active_sessions[session_id] = session
                return session

            except Exception as e:
                logger.error(f"Error loading session {session_id}: {str(e)}")

        return None

    def update_session(self, session: Session) -> None:
        """
        Update a session.

        Args:
            session: The updated session
        """
        # Update in active sessions
        self.active_sessions[session.id] = session

        # Save to storage
        self._save_session(session)

        logger.info(f"Updated session: {session.id}")

    def add_orchestration_to_session(
        self, session_id: str, orchestration: OrchestrationResult
    ) -> Optional[Session]:
        """
        Add an orchestration result to a session.

        Args:
            session_id: The ID of the session to add to
            orchestration: The orchestration result to add

        Returns:
            The updated session, or None if the session was not found
        """
        session = self.get_session(session_id)
        if session:
            session.add_orchestration(orchestration)
            self.update_session(session)
            return session

        return None

    def get_orchestration(
        self, session_id: str, orchestration_id: str
    ) -> Optional[OrchestrationResult]:
        """
        Get an orchestration result from a session.

        Args:
            session_id: The ID of the session
            orchestration_id: The ID of the orchestration

        Returns:
            The orchestration result, or None if not found
        """
        session = self.get_session(session_id)
        if session:
            return session.get_orchestration(orchestration_id)

        return None

    def update_orchestration(
        self, session_id: str, orchestration: OrchestrationResult
    ) -> Optional[Session]:
        """
        Update an orchestration result in a session.

        Args:
            session_id: The ID of the session
            orchestration: The updated orchestration result

        Returns:
            The updated session, or None if the session was not found
        """
        session = self.get_session(session_id)
        if session:
            session.update_orchestration(orchestration)
            self.update_session(session)
            return session

        return None

    def complete_session(self, session_id: str) -> Optional[Session]:
        """
        Mark a session as completed.

        Args:
            session_id: The ID of the session to complete

        Returns:
            The updated session, or None if the session was not found
        """
        session = self.get_session(session_id)
        if session:
            session.complete()
            self.update_session(session)
            return session

        return None

    def fail_session(self, session_id: str) -> Optional[Session]:
        """
        Mark a session as failed.

        Args:
            session_id: The ID of the session to fail

        Returns:
            The updated session, or None if the session was not found
        """
        session = self.get_session(session_id)
        if session:
            session.fail()
            self.update_session(session)
            return session

        return None

    def extend_session_expiry(
        self, session_id: str, ttl_seconds: int
    ) -> Optional[Session]:
        """
        Extend a session's expiry time.

        Args:
            session_id: The ID of the session to extend
            ttl_seconds: Additional time-to-live in seconds

        Returns:
            The updated session, or None if the session was not found
        """
        session = self.get_session(session_id)
        if session:
            session.extend_expiry(ttl_seconds)
            self.update_session(session)
            return session

        return None

    def list_sessions(
        self, status_filter: Optional[SessionStatus] = None
    ) -> List[Session]:
        """
        List all sessions, optionally filtered by status.

        Args:
            status_filter: Filter sessions by status

        Returns:
            List of sessions
        """
        # Refresh active sessions
        self._refresh_active_sessions()

        # Filter by status if specified
        if status_filter:
            return [
                session
                for session in self.active_sessions.values()
                if session.status == status_filter
            ]

        return list(self.active_sessions.values())

    def _save_session(self, session: Session) -> None:
        """
        Save a session to storage.

        Args:
            session: The session to save
        """
        session_path = os.path.join(self.storage_dir, f"{session.id}.json")
        try:
            with open(session_path, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session {session.id}: {str(e)}")

    def _load_sessions(self) -> None:
        """Load existing sessions from storage."""
        try:
            # Get all session files
            session_files = [
                f for f in os.listdir(self.storage_dir) if f.endswith(".json")
            ]

            # Load each session
            for session_file in session_files:
                try:
                    session_path = os.path.join(self.storage_dir, session_file)
                    with open(session_path, "r") as f:
                        session_data = json.load(f)

                    session = Session.from_dict(session_data)

                    # Only add active sessions
                    if (
                        session.status == SessionStatus.ACTIVE
                        and not session.is_expired()
                    ):
                        self.active_sessions[session.id] = session

                except Exception as e:
                    logger.error(f"Error loading session file {session_file}: {str(e)}")

            logger.info(f"Loaded {len(self.active_sessions)} active sessions")

        except Exception as e:
            logger.error(f"Error loading sessions: {str(e)}")

    def _refresh_active_sessions(self) -> None:
        """Refresh the active sessions, removing expired ones."""
        expired_sessions: Set[str] = set()

        # Check each active session
        for session_id, session in self.active_sessions.items():
            if session.is_expired():
                expired_sessions.add(session_id)
                session.expire()
                self._save_session(session)

        # Remove expired sessions
        for session_id in expired_sessions:
            del self.active_sessions[session_id]

        if expired_sessions:
            logger.info(f"Removed {len(expired_sessions)} expired sessions")

    def _start_cleanup_task(self) -> None:
        """Start the cleanup task for expired sessions."""
        # This would normally be an async task, but for simplicity
        # we'll just log that it would be started
        logger.info(
            f"Cleanup task would run every {self.cleanup_interval_seconds} seconds"
        )

    async def _cleanup_task(self) -> None:
        """Task for cleaning up expired sessions."""
        while True:
            try:
                # Refresh active sessions
                self._refresh_active_sessions()

                # Sleep until next cleanup
                await asyncio.sleep(self.cleanup_interval_seconds)

            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)  # Sleep for a minute on error


# Example usage
if __name__ == "__main__":
    # Create a session manager
    manager = SessionManager()

    # Create a session
    session = manager.create_session(metadata={"user_id": "test_user"})
    print(f"Created session: {session.id}")

    # Create an orchestration result
    orchestration = OrchestrationResult(str(uuid.uuid4()))
    orchestration.status = OrchestrationStatus.COMPLETED
    orchestration.content = "Test content"
    orchestration.confidence_score = 0.8

    # Add the orchestration to the session
    manager.add_orchestration_to_session(session.id, orchestration)
    print(f"Added orchestration {orchestration.id} to session {session.id}")

    # Get the session
    retrieved_session = manager.get_session(session.id)
    if retrieved_session:
        print(f"Retrieved session: {retrieved_session.id}")
        print(f"Session has {len(retrieved_session.orchestrations)} orchestrations")

    # Complete the session
    manager.complete_session(session.id)
    print(f"Completed session: {session.id}")
