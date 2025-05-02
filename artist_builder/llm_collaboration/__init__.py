"""
LLM Collaboration Package Initialization

This module initializes the LLM collaboration package and provides
a unified interface for advanced LLM collaboration and peer review.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

from .llm_collaboration import (
    LLMCollaborator,
    LLMCollaborationManager,
    LLMPeerReviewSystem,
    LLMCollaborationError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.llm_collaboration")


class LLMCollaboration:
    """
    Main interface for the LLM collaboration system.
    Provides a unified API for collaboration and peer review.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM collaboration system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.collaboration_manager = LLMCollaborationManager(
            self.config.get("collaboration_config")
        )
        self.peer_review_system = LLMPeerReviewSystem(
            collaboration_manager=self.collaboration_manager,
            config=self.config.get("peer_review_config"),
        )

        logger.info("Initialized LLM collaboration system")

    def create_collaboration_session(
        self,
        session_name: str,
        collaborator_ids: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new collaboration session.

        Args:
            session_name: Human-readable name for the session
            collaborator_ids: Optional list of specific collaborator IDs to include
            roles: Optional list of roles to include (will select one collaborator per role)
            context: Optional initial context for the session

        Returns:
            Session ID
        """
        return self.collaboration_manager.create_session(
            session_name=session_name,
            collaborator_ids=collaborator_ids,
            roles=roles,
            context=context,
        )

    def run_collaboration_round(
        self,
        session_id: str,
        prompt: str,
        round_type: str = "sequential",
        max_iterations: int = 3,
        callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Run a round of collaboration in a session.

        Args:
            session_id: ID of the session
            prompt: The initial prompt for the collaboration
            round_type: Type of collaboration round ('sequential', 'parallel', or 'debate')
            max_iterations: Maximum number of iterations for the round
            callback: Optional callback function for progress updates

        Returns:
            Dictionary containing the results of the collaboration round
        """
        return self.collaboration_manager.run_collaboration_round(
            session_id=session_id,
            prompt=prompt,
            round_type=round_type,
            max_iterations=max_iterations,
            callback=callback,
        )

    def create_review_session(
        self,
        content: str,
        content_type: str,
        artist_id: Optional[str] = None,
        reviewer_roles: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new peer review session.

        Args:
            content: The content to review
            content_type: Type of content (e.g., 'artist_profile', 'lyrics', 'prompt')
            artist_id: Optional ID of the artist associated with the content
            reviewer_roles: Optional list of reviewer roles to include
            context: Optional additional context for the review

        Returns:
            Review session ID
        """
        return self.peer_review_system.create_review_session(
            content=content,
            content_type=content_type,
            artist_id=artist_id,
            reviewer_roles=reviewer_roles,
            context=context,
        )

    def run_peer_review(
        self, review_session_id: str, callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run a complete peer review process (individual reviews + consensus).

        Args:
            review_session_id: ID of the review session
            callback: Optional callback function for progress updates

        Returns:
            Dictionary containing the review results
        """
        # Run individual reviews
        individual_reviews = self.peer_review_system.run_individual_reviews(
            review_session_id=review_session_id, callback=callback
        )

        # Generate consensus review
        consensus = self.peer_review_system.generate_consensus_review(
            review_session_id=review_session_id, callback=callback
        )

        # Get complete review session
        review_session = self.peer_review_system.get_review_session(review_session_id)

        return {
            "review_session_id": review_session_id,
            "content_type": review_session["content_type"],
            "individual_reviews": individual_reviews,
            "consensus": consensus,
            "status": review_session["status"],
        }

    def get_collaborator_performance(
        self, collaborator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for collaborators.

        Args:
            collaborator_id: Optional ID of a specific collaborator

        Returns:
            Dictionary of performance metrics
        """
        return self.collaboration_manager.get_collaborator_performance(collaborator_id)

    def get_review_sessions_for_artist(self, artist_id: str) -> List[Dict[str, Any]]:
        """
        Get all review sessions for an artist.

        Args:
            artist_id: ID of the artist

        Returns:
            List of review sessions
        """
        return self.peer_review_system.get_review_sessions_for_artist(artist_id)
