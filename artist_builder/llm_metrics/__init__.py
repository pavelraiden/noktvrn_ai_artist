"""
LLM Metrics Package Initialization

This module initializes the LLM metrics package and provides
a unified interface for LLM efficiency tracking and analysis.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .llm_efficiency_metrics import (
    LLMEfficiencyTracker,
    LLMMetricsDatabase,
    LLMMetricsError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.llm_metrics")


class LLMMetrics:
    """
    Main interface for the LLM metrics system.
    Provides a unified API for tracking and analyzing LLM efficiency.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM metrics system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.tracker = LLMEfficiencyTracker(self.config.get("tracker_config"))
        self.db = self.tracker.db  # Share the same database instance

        logger.info("Initialized LLM metrics system")

    def track_llm_interaction(
        self,
        module: str,
        operation: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        success: bool,
        cost: Optional[float] = None,
        artist_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track an LLM interaction.

        Args:
            module: The module that initiated the interaction
            operation: The specific operation performed
            model: The LLM model used
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            latency_ms: Latency in milliseconds
            success: Whether the interaction was successful
            cost: Optional cost of the interaction (calculated if not provided)
            artist_id: Optional ID of the artist being processed
            metadata: Optional additional metadata

        Returns:
            Dictionary of recorded metrics
        """
        return self.tracker.track_interaction(
            module=module,
            operation=operation,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            success=success,
            cost=cost,
            artist_id=artist_id,
            metadata=metadata,
        )

    def start_tracking(
        self,
        module: str,
        operation: str,
        artist_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start tracking an LLM interaction.

        Args:
            module: The module initiating the interaction
            operation: The specific operation being performed
            artist_id: Optional ID of the artist being processed
            metadata: Optional additional metadata

        Returns:
            Tracking ID for the interaction
        """
        return self.tracker.start_tracking(
            module=module, operation=operation, artist_id=artist_id, metadata=metadata
        )

    def end_tracking(
        self,
        tracking_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        success: bool,
        cost: Optional[float] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        End tracking an LLM interaction and record metrics.

        Args:
            tracking_id: The tracking ID returned by start_tracking
            model: The LLM model used
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            success: Whether the interaction was successful
            cost: Optional cost of the interaction (calculated if not provided)
            additional_metadata: Optional additional metadata to merge

        Returns:
            Dictionary of recorded metrics
        """
        return self.tracker.end_tracking(
            tracking_id=tracking_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            success=success,
            cost=cost,
            additional_metadata=additional_metadata,
        )

    def record_optimization(
        self,
        module: str,
        operation: str,
        optimization_type: str,
        before_value: Optional[float] = None,
        after_value: Optional[float] = None,
        applied: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record an LLM optimization.

        Args:
            module: The module being optimized
            operation: The specific operation being optimized
            optimization_type: Type of optimization (e.g., 'prompt_reduction', 'caching')
            before_value: Value before optimization
            after_value: Value after optimization
            applied: Whether the optimization was applied
            metadata: Optional additional metadata

        Returns:
            ID of the recorded optimization
        """
        return self.tracker.record_optimization(
            module=module,
            operation=operation,
            optimization_type=optimization_type,
            before_value=before_value,
            after_value=after_value,
            applied=applied,
            metadata=metadata,
        )

    def get_efficiency_report(
        self,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        artist_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an efficiency report for a time period.

        Args:
            start_time: Optional start time for the report
            end_time: Optional end time for the report
            module: Optional filter by module
            operation: Optional filter by operation
            artist_id: Optional filter by artist ID

        Returns:
            Dictionary containing the efficiency report
        """
        return self.tracker.get_efficiency_report(
            start_time=start_time,
            end_time=end_time,
            module=module,
            operation=operation,
            artist_id=artist_id,
        )

    def get_artist_efficiency_metrics(
        self,
        artist_id: str,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Get efficiency metrics for a specific artist.

        Args:
            artist_id: ID of the artist
            start_time: Optional start time for the metrics
            end_time: Optional end time for the metrics

        Returns:
            Dictionary containing artist-specific efficiency metrics
        """
        return self.tracker.get_artist_efficiency_metrics(
            artist_id=artist_id, start_time=start_time, end_time=end_time
        )

    def get_interactions(
        self,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        artist_id: Optional[str] = None,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get LLM interactions from the database.

        Args:
            module: Optional filter by module
            operation: Optional filter by operation
            artist_id: Optional filter by artist ID
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            limit: Maximum number of results to return

        Returns:
            List of interaction records
        """
        return self.db.get_interactions(
            module=module,
            operation=operation,
            artist_id=artist_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    def get_optimizations(
        self,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        optimization_type: Optional[str] = None,
        applied: Optional[bool] = None,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get optimizations from the database.

        Args:
            module: Optional filter by module
            operation: Optional filter by operation
            optimization_type: Optional filter by optimization type
            applied: Optional filter by whether the optimization was applied
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            limit: Maximum number of results to return

        Returns:
            List of optimization records
        """
        return self.db.get_optimizations(
            module=module,
            operation=operation,
            optimization_type=optimization_type,
            applied=applied,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    def calculate_aggregate_metrics(
        self,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
        time_period: str = "daily",
    ) -> Dict[str, Any]:
        """
        Calculate aggregate metrics for a time period.

        Args:
            start_time: Start time of the period
            end_time: End time of the period
            time_period: Time period type (e.g., 'daily', 'weekly', 'monthly')

        Returns:
            Dictionary of calculated metrics
        """
        return self.db.calculate_aggregate_metrics(
            start_time=start_time, end_time=end_time, time_period=time_period
        )
