"""
LLM Efficiency Metrics Module

This module provides tools for measuring, tracking, and optimizing
the efficiency of LLM interactions in the artist creation process.
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import uuid
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.llm_metrics")


class LLMMetricsError(Exception):
    """Exception raised for errors in the LLM metrics system."""
    pass


class LLMMetricsDatabase:
    """
    Database for storing and retrieving LLM interaction metrics.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the LLM metrics database.
        
        Args:
            db_path: Optional path to the database file
        """
        if db_path is None:
            # Use default path in the project directory
            base_dir = Path(__file__).parent.parent.parent
            db_dir = base_dir / "data" / "metrics"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(db_dir / "llm_metrics.db")
        else:
            self.db_path = db_path
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Initialized LLM metrics database at {self.db_path}")

    def _initialize_database(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create interactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_interactions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                artist_id TEXT,
                module TEXT NOT NULL,
                operation TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                latency_ms INTEGER NOT NULL,
                success INTEGER NOT NULL,
                cost REAL NOT NULL,
                metadata TEXT
            )
            ''')
            
            # Create metrics table for aggregated metrics
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_metrics (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                time_period TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                value REAL NOT NULL,
                metadata TEXT
            )
            ''')
            
            # Create optimizations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_optimizations (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                module TEXT NOT NULL,
                operation TEXT NOT NULL,
                optimization_type TEXT NOT NULL,
                before_value REAL,
                after_value REAL,
                improvement_percent REAL,
                applied INTEGER NOT NULL,
                metadata TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise LLMMetricsError(f"Failed to initialize database: {str(e)}")

    def record_interaction(
        self,
        module: str,
        operation: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        success: bool,
        cost: float,
        artist_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an LLM interaction in the database.
        
        Args:
            module: The module that initiated the interaction
            operation: The specific operation performed
            model: The LLM model used
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            latency_ms: Latency in milliseconds
            success: Whether the interaction was successful
            cost: Estimated cost of the interaction
            artist_id: Optional ID of the artist being processed
            metadata: Optional additional metadata
            
        Returns:
            ID of the recorded interaction
        """
        try:
            interaction_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            total_tokens = prompt_tokens + completion_tokens
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                INSERT INTO llm_interactions (
                    id, timestamp, artist_id, module, operation, model,
                    prompt_tokens, completion_tokens, total_tokens,
                    latency_ms, success, cost, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    interaction_id, timestamp, artist_id, module, operation, model,
                    prompt_tokens, completion_tokens, total_tokens,
                    latency_ms, 1 if success else 0, cost,
                    json.dumps(metadata) if metadata else None
                )
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded LLM interaction {interaction_id} for {module}.{operation}")
            return interaction_id
            
        except Exception as e:
            logger.error(f"Error recording interaction: {str(e)}")
            raise LLMMetricsError(f"Failed to record interaction: {str(e)}")

    def record_metric(
        self,
        metric_type: str,
        time_period: str,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an aggregated metric in the database.
        
        Args:
            metric_type: Type of metric (e.g., 'token_efficiency', 'cost_per_artist')
            time_period: Time period covered (e.g., 'daily', 'weekly', 'monthly')
            start_time: Start time of the period
            end_time: End time of the period
            value: Metric value
            metadata: Optional additional metadata
            
        Returns:
            ID of the recorded metric
        """
        try:
            metric_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                INSERT INTO llm_metrics (
                    id, timestamp, metric_type, time_period,
                    start_time, end_time, value, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    metric_id, timestamp, metric_type, time_period,
                    start_time, end_time, value,
                    json.dumps(metadata) if metadata else None
                )
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded metric {metric_id} of type {metric_type}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Error recording metric: {str(e)}")
            raise LLMMetricsError(f"Failed to record metric: {str(e)}")

    def record_optimization(
        self,
        module: str,
        operation: str,
        optimization_type: str,
        before_value: Optional[float] = None,
        after_value: Optional[float] = None,
        applied: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an LLM optimization in the database.
        
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
        try:
            optimization_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Calculate improvement percentage if both values are provided
            improvement_percent = None
            if before_value is not None and after_value is not None and before_value > 0:
                improvement_percent = ((before_value - after_value) / before_value) * 100
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                INSERT INTO llm_optimizations (
                    id, timestamp, module, operation, optimization_type,
                    before_value, after_value, improvement_percent, applied, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    optimization_id, timestamp, module, operation, optimization_type,
                    before_value, after_value, improvement_percent, 1 if applied else 0,
                    json.dumps(metadata) if metadata else None
                )
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded optimization {optimization_id} of type {optimization_type}")
            return optimization_id
            
        except Exception as e:
            logger.error(f"Error recording optimization: {str(e)}")
            raise LLMMetricsError(f"Failed to record optimization: {str(e)}")

    def get_interactions(
        self,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        artist_id: Optional[str] = None,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        limit: int = 100
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
        try:
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            # Build query
            query = "SELECT * FROM llm_interactions WHERE 1=1"
            params = []
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            if operation:
                query += " AND operation = ?"
                params.append(operation)
            
            if artist_id:
                query += " AND artist_id = ?"
                params.append(artist_id)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                result = dict(row)
                
                # Parse metadata JSON if present
                if result["metadata"]:
                    result["metadata"] = json.loads(result["metadata"])
                
                # Convert success to boolean
                result["success"] = bool(result["success"])
                
                results.append(result)
            
            conn.close()
            
            logger.debug(f"Retrieved {len(results)} interactions")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving interactions: {str(e)}")
            raise LLMMetricsError(f"Failed to retrieve interactions: {str(e)}")

    def get_metrics(
        self,
        metric_type: Optional[str] = None,
        time_period: Optional[str] = None,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get metrics from the database.
        
        Args:
            metric_type: Optional filter by metric type
            time_period: Optional filter by time period
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            limit: Maximum number of results to return
            
        Returns:
            List of metric records
        """
        try:
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            # Build query
            query = "SELECT * FROM llm_metrics WHERE 1=1"
            params = []
            
            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)
            
            if time_period:
                query += " AND time_period = ?"
                params.append(time_period)
            
            if start_time:
                query += " AND start_time >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND end_time <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                result = dict(row)
                
                # Parse metadata JSON if present
                if result["metadata"]:
                    result["metadata"] = json.loads(result["metadata"])
                
                results.append(result)
            
            conn.close()
            
            logger.debug(f"Retrieved {len(results)} metrics")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to retrieve metrics: {str(e)}")

    def get_optimizations(
        self,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        optimization_type: Optional[str] = None,
        applied: Optional[bool] = None,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        limit: int = 100
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
        try:
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            # Build query
            query = "SELECT * FROM llm_optimizations WHERE 1=1"
            params = []
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            if operation:
                query += " AND operation = ?"
                params.append(operation)
            
            if optimization_type:
                query += " AND optimization_type = ?"
                params.append(optimization_type)
            
            if applied is not None:
                query += " AND applied = ?"
                params.append(1 if applied else 0)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                result = dict(row)
                
                # Parse metadata JSON if present
                if result["metadata"]:
                    result["metadata"] = json.loads(result["metadata"])
                
                # Convert applied to boolean
                result["applied"] = bool(result["applied"])
                
                results.append(result)
            
            conn.close()
            
            logger.debug(f"Retrieved {len(results)} optimizations")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving optimizations: {str(e)}")
            raise LLMMetricsError(f"Failed to retrieve optimizations: {str(e)}")

    def calculate_aggregate_metrics(
        self,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
        time_period: str = "daily"
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
        try:
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate total tokens
            cursor.execute(
                '''
                SELECT SUM(total_tokens) as total_tokens,
                       SUM(prompt_tokens) as prompt_tokens,
                       SUM(completion_tokens) as completion_tokens,
                       COUNT(*) as total_interactions,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_interactions,
                       SUM(cost) as total_cost,
                       AVG(latency_ms) as avg_latency
                FROM llm_interactions
                WHERE timestamp >= ? AND timestamp <= ?
                ''',
                (start_time, end_time)
            )
            
            row = cursor.fetchone()
            
            # Calculate metrics by module
            cursor.execute(
                '''
                SELECT module,
                       SUM(total_tokens) as total_tokens,
                       COUNT(*) as total_interactions,
                       SUM(cost) as total_cost
                FROM llm_interactions
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY module
                ''',
                (start_time, end_time)
            )
            
            module_metrics = {}
            for module_row in cursor.fetchall():
                module_metrics[module_row[0]] = {
                    "total_tokens": module_row[1],
                    "total_interactions": module_row[2],
                    "total_cost": module_row[3]
                }
            
            # Calculate metrics by operation
            cursor.execute(
                '''
                SELECT module, operation,
                       SUM(total_tokens) as total_tokens,
                       COUNT(*) as total_interactions,
                       SUM(cost) as total_cost
                FROM llm_interactions
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY module, operation
                ''',
                (start_time, end_time)
            )
            
            operation_metrics = {}
            for op_row in cursor.fetchall():
                key = f"{op_row[0]}.{op_row[1]}"
                operation_metrics[key] = {
                    "total_tokens": op_row[2],
                    "total_interactions": op_row[3],
                    "total_cost": op_row[4]
                }
            
            conn.close()
            
            # Calculate derived metrics
            total_tokens = row[0] or 0
            prompt_tokens = row[1] or 0
            completion_tokens = row[2] or 0
            total_interactions = row[3] or 0
            successful_interactions = row[4] or 0
            total_cost = row[5] or 0
            avg_latency = row[6] or 0
            
            success_rate = (successful_interactions / total_interactions) * 100 if total_interactions > 0 else 0
            avg_tokens_per_interaction = total_tokens / total_interactions if total_interactions > 0 else 0
            avg_cost_per_interaction = total_cost / total_interactions if total_interactions > 0 else 0
            avg_cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
            prompt_completion_ratio = prompt_tokens / completion_tokens if completion_tokens > 0 else 0
            
            # Prepare result
            result = {
                "time_period": time_period,
                "start_time": start_time,
                "end_time": end_time,
                "total_tokens": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_interactions": total_interactions,
                "successful_interactions": successful_interactions,
                "success_rate": success_rate,
                "total_cost": total_cost,
                "avg_latency_ms": avg_latency,
                "avg_tokens_per_interaction": avg_tokens_per_interaction,
                "avg_cost_per_interaction": avg_cost_per_interaction,
                "avg_cost_per_token": avg_cost_per_token,
                "prompt_completion_ratio": prompt_completion_ratio,
                "module_metrics": module_metrics,
                "operation_metrics": operation_metrics
            }
            
            logger.debug(f"Calculated aggregate metrics for period {start_time} to {end_time}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating aggregate metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to calculate aggregate metrics: {str(e)}")


class LLMEfficiencyTracker:
    """
    Tracks and analyzes LLM efficiency metrics.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM efficiency tracker.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.db = LLMMetricsDatabase(self.config.get("db_path"))
        
        # Initialize tracking state
        self.current_tracking = {}
        
        logger.info("Initialized LLM efficiency tracker")

    def start_tracking(
        self,
        module: str,
        operation: str,
        artist_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
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
        tracking_id = str(uuid.uuid4())
        
        self.current_tracking[tracking_id] = {
            "module": module,
            "operation": operation,
            "artist_id": artist_id,
            "start_time": time.time(),
            "metadata": metadata or {}
        }
        
        logger.debug(f"Started tracking LLM interaction {tracking_id} for {module}.{operation}")
        return tracking_id

    def end_tracking(
        self,
        tracking_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        success: bool,
        cost: Optional[float] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
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
        try:
            if tracking_id not in self.current_tracking:
                raise LLMMetricsError(f"Unknown tracking ID: {tracking_id}")
            
            tracking_data = self.current_tracking[tracking_id]
            end_time = time.time()
            latency_ms = int((end_time - tracking_data["start_time"]) * 1000)
            
            # Calculate cost if not provided
            if cost is None:
                cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
            
            # Merge additional metadata
            metadata = tracking_data["metadata"].copy()
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Record interaction in database
            interaction_id = self.db.record_interaction(
                module=tracking_data["module"],
                operation=tracking_data["operation"],
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                success=success,
                cost=cost,
                artist_id=tracking_data["artist_id"],
                metadata=metadata
            )
            
            # Prepare result
            result = {
                "interaction_id": interaction_id,
                "tracking_id": tracking_id,
                "module": tracking_data["module"],
                "operation": tracking_data["operation"],
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "latency_ms": latency_ms,
                "success": success,
                "cost": cost
            }
            
            # Clean up tracking data
            del self.current_tracking[tracking_id]
            
            logger.debug(f"Ended tracking LLM interaction {tracking_id} with {result['total_tokens']} tokens")
            return result
            
        except Exception as e:
            # Clean up tracking data even if there's an error
            if tracking_id in self.current_tracking:
                del self.current_tracking[tracking_id]
            
            logger.error(f"Error ending tracking: {str(e)}")
            raise LLMMetricsError(f"Failed to end tracking: {str(e)}")

    def track_interaction(
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
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track an LLM interaction in a single call (without start/end).
        
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
        try:
            # Calculate cost if not provided
            if cost is None:
                cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
            
            # Record interaction in database
            interaction_id = self.db.record_interaction(
                module=module,
                operation=operation,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                success=success,
                cost=cost,
                artist_id=artist_id,
                metadata=metadata
            )
            
            # Prepare result
            result = {
                "interaction_id": interaction_id,
                "module": module,
                "operation": operation,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "latency_ms": latency_ms,
                "success": success,
                "cost": cost
            }
            
            logger.debug(f"Tracked LLM interaction {interaction_id} with {result['total_tokens']} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking interaction: {str(e)}")
            raise LLMMetricsError(f"Failed to track interaction: {str(e)}")

    def record_optimization(
        self,
        module: str,
        operation: str,
        optimization_type: str,
        before_value: Optional[float] = None,
        after_value: Optional[float] = None,
        applied: bool = False,
        metadata: Optional[Dict[str, Any]] = None
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
        try:
            optimization_id = self.db.record_optimization(
                module=module,
                operation=operation,
                optimization_type=optimization_type,
                before_value=before_value,
                after_value=after_value,
                applied=applied,
                metadata=metadata
            )
            
            logger.debug(f"Recorded optimization {optimization_id} of type {optimization_type}")
            return optimization_id
            
        except Exception as e:
            logger.error(f"Error recording optimization: {str(e)}")
            raise LLMMetricsError(f"Failed to record optimization: {str(e)}")

    def get_efficiency_report(
        self,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        module: Optional[str] = None,
        operation: Optional[str] = None,
        artist_id: Optional[str] = None
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
        try:
            # Use default time range if not specified
            if not end_time:
                end_time = datetime.now()
            if not start_time:
                # Default to 30 days before end_time
                if isinstance(end_time, str):
                    end_time_dt = datetime.fromisoformat(end_time)
                else:
                    end_time_dt = end_time
                start_time = (end_time_dt.replace(hour=0, minute=0, second=0, microsecond=0) - 
                             datetime.timedelta(days=30)).isoformat()
            
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            # Get interactions for the period
            interactions = self.db.get_interactions(
                module=module,
                operation=operation,
                artist_id=artist_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000  # Use a large limit to get all interactions
            )
            
            # Calculate aggregate metrics
            aggregate_metrics = self.db.calculate_aggregate_metrics(
                start_time=start_time,
                end_time=end_time,
                time_period="custom"
            )
            
            # Get optimizations for the period
            optimizations = self.db.get_optimizations(
                module=module,
                operation=operation,
                start_time=start_time,
                end_time=end_time,
                limit=1000  # Use a large limit to get all optimizations
            )
            
            # Calculate optimization impact
            optimization_impact = self._calculate_optimization_impact(optimizations)
            
            # Prepare report
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "time_period": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "filters": {
                    "module": module,
                    "operation": operation,
                    "artist_id": artist_id
                },
                "summary": {
                    "total_interactions": len(interactions),
                    "total_tokens": aggregate_metrics["total_tokens"],
                    "total_cost": aggregate_metrics["total_cost"],
                    "success_rate": aggregate_metrics["success_rate"],
                    "avg_tokens_per_interaction": aggregate_metrics["avg_tokens_per_interaction"],
                    "avg_cost_per_interaction": aggregate_metrics["avg_cost_per_interaction"],
                    "avg_latency_ms": aggregate_metrics["avg_latency_ms"],
                    "total_optimizations": len(optimizations),
                    "applied_optimizations": sum(1 for opt in optimizations if opt["applied"]),
                    "estimated_savings": optimization_impact["estimated_savings"]
                },
                "token_usage": {
                    "prompt_tokens": aggregate_metrics["prompt_tokens"],
                    "completion_tokens": aggregate_metrics["completion_tokens"],
                    "prompt_completion_ratio": aggregate_metrics["prompt_completion_ratio"]
                },
                "module_metrics": aggregate_metrics["module_metrics"],
                "operation_metrics": aggregate_metrics["operation_metrics"],
                "optimization_impact": optimization_impact,
                "recommendations": self._generate_efficiency_recommendations(
                    interactions, aggregate_metrics, optimizations
                )
            }
            
            logger.info(f"Generated efficiency report with {len(interactions)} interactions and {len(optimizations)} optimizations")
            return report
            
        except Exception as e:
            logger.error(f"Error generating efficiency report: {str(e)}")
            raise LLMMetricsError(f"Failed to generate efficiency report: {str(e)}")

    def get_artist_efficiency_metrics(
        self,
        artist_id: str,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None
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
        try:
            # Use default time range if not specified
            if not end_time:
                end_time = datetime.now()
            if not start_time:
                # Default to 90 days before end_time
                if isinstance(end_time, str):
                    end_time_dt = datetime.fromisoformat(end_time)
                else:
                    end_time_dt = end_time
                start_time = (end_time_dt.replace(hour=0, minute=0, second=0, microsecond=0) - 
                             datetime.timedelta(days=90)).isoformat()
            
            # Convert datetime objects to ISO format strings if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            
            # Get interactions for the artist
            interactions = self.db.get_interactions(
                artist_id=artist_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000  # Use a large limit to get all interactions
            )
            
            if not interactions:
                return {
                    "artist_id": artist_id,
                    "time_period": {
                        "start_time": start_time,
                        "end_time": end_time
                    },
                    "metrics": {
                        "total_interactions": 0,
                        "total_tokens": 0,
                        "total_cost": 0
                    },
                    "message": "No interactions found for this artist in the specified time period"
                }
            
            # Calculate metrics
            total_tokens = sum(interaction["total_tokens"] for interaction in interactions)
            total_cost = sum(interaction["cost"] for interaction in interactions)
            successful_interactions = sum(1 for interaction in interactions if interaction["success"])
            success_rate = (successful_interactions / len(interactions)) * 100 if interactions else 0
            avg_tokens_per_interaction = total_tokens / len(interactions) if interactions else 0
            avg_cost_per_interaction = total_cost / len(interactions) if interactions else 0
            
            # Group by module and operation
            module_metrics = {}
            operation_metrics = {}
            
            for interaction in interactions:
                module = interaction["module"]
                operation = interaction["operation"]
                
                # Update module metrics
                if module not in module_metrics:
                    module_metrics[module] = {
                        "total_interactions": 0,
                        "total_tokens": 0,
                        "total_cost": 0
                    }
                
                module_metrics[module]["total_interactions"] += 1
                module_metrics[module]["total_tokens"] += interaction["total_tokens"]
                module_metrics[module]["total_cost"] += interaction["cost"]
                
                # Update operation metrics
                key = f"{module}.{operation}"
                if key not in operation_metrics:
                    operation_metrics[key] = {
                        "total_interactions": 0,
                        "total_tokens": 0,
                        "total_cost": 0
                    }
                
                operation_metrics[key]["total_interactions"] += 1
                operation_metrics[key]["total_tokens"] += interaction["total_tokens"]
                operation_metrics[key]["total_cost"] += interaction["cost"]
            
            # Prepare result
            result = {
                "artist_id": artist_id,
                "time_period": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "metrics": {
                    "total_interactions": len(interactions),
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "success_rate": success_rate,
                    "avg_tokens_per_interaction": avg_tokens_per_interaction,
                    "avg_cost_per_interaction": avg_cost_per_interaction
                },
                "module_metrics": module_metrics,
                "operation_metrics": operation_metrics
            }
            
            logger.info(f"Generated artist efficiency metrics for artist {artist_id} with {len(interactions)} interactions")
            return result
            
        except Exception as e:
            logger.error(f"Error generating artist efficiency metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to generate artist efficiency metrics: {str(e)}")

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate the cost of an LLM interaction.
        
        Args:
            model: The LLM model used
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            
        Returns:
            Estimated cost in USD
        """
        # Pricing per 1000 tokens (as of 2023)
        # These should be updated as pricing changes
        pricing = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
            "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
            "text-davinci-003": {"prompt": 0.02, "completion": 0.02},
            "text-embedding-ada-002": {"prompt": 0.0001, "completion": 0.0},
            "claude-2": {"prompt": 0.01, "completion": 0.03},
            "claude-instant-1": {"prompt": 0.0015, "completion": 0.0065}
        }
        
        # Use default pricing if model not found
        model_pricing = pricing.get(model.lower(), {"prompt": 0.01, "completion": 0.02})
        
        # Calculate cost
        prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * model_pricing["completion"]
        
        return prompt_cost + completion_cost

    def _calculate_optimization_impact(
        self,
        optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate the impact of optimizations.
        
        Args:
            optimizations: List of optimization records
            
        Returns:
            Dictionary containing optimization impact metrics
        """
        # Initialize result
        result = {
            "total_optimizations": len(optimizations),
            "applied_optimizations": sum(1 for opt in optimizations if opt["applied"]),
            "optimization_types": {},
            "estimated_savings": 0.0,
            "top_optimizations": []
        }
        
        # Group by optimization type
        for opt in optimizations:
            opt_type = opt["optimization_type"]
            
            if opt_type not in result["optimization_types"]:
                result["optimization_types"][opt_type] = {
                    "count": 0,
                    "applied": 0,
                    "avg_improvement": 0.0,
                    "estimated_savings": 0.0
                }
            
            result["optimization_types"][opt_type]["count"] += 1
            
            if opt["applied"]:
                result["optimization_types"][opt_type]["applied"] += 1
            
            # Calculate improvement and savings
            if opt["improvement_percent"] is not None and opt["applied"]:
                current_avg = result["optimization_types"][opt_type]["avg_improvement"]
                current_count = result["optimization_types"][opt_type]["applied"]
                
                # Update running average
                if current_count > 1:
                    result["optimization_types"][opt_type]["avg_improvement"] = (
                        (current_avg * (current_count - 1) + opt["improvement_percent"]) / current_count
                    )
                else:
                    result["optimization_types"][opt_type]["avg_improvement"] = opt["improvement_percent"]
                
                # Estimate savings (this is a simplified calculation)
                # In a real system, this would be more sophisticated
                if opt["before_value"] is not None and opt["after_value"] is not None:
                    savings = opt["before_value"] - opt["after_value"]
                    result["optimization_types"][opt_type]["estimated_savings"] += savings
                    result["estimated_savings"] += savings
        
        # Find top optimizations by improvement percentage
        applied_opts = [opt for opt in optimizations if opt["applied"] and opt["improvement_percent"] is not None]
        applied_opts.sort(key=lambda x: x["improvement_percent"], reverse=True)
        
        result["top_optimizations"] = applied_opts[:5]  # Top 5 optimizations
        
        return result

    def _generate_efficiency_recommendations(
        self,
        interactions: List[Dict[str, Any]],
        aggregate_metrics: Dict[str, Any],
        optimizations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate efficiency recommendations based on metrics.
        
        Args:
            interactions: List of interaction records
            aggregate_metrics: Aggregate metrics
            optimizations: List of optimization records
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check prompt-completion ratio
        prompt_completion_ratio = aggregate_metrics["prompt_completion_ratio"]
        if prompt_completion_ratio > 3.0:
            recommendations.append({
                "type": "prompt_optimization",
                "priority": "high",
                "description": "Reduce prompt size relative to completion",
                "rationale": f"Current prompt-completion ratio is {prompt_completion_ratio:.2f}, which is higher than the recommended maximum of 3.0",
                "potential_impact": "Reducing prompt size could significantly decrease token usage and cost",
                "suggested_actions": [
                    "Review and simplify prompts",
                    "Remove redundant information from prompts",
                    "Use more efficient prompt structures"
                ]
            })
        
        # Check average tokens per interaction
        avg_tokens = aggregate_metrics["avg_tokens_per_interaction"]
        if avg_tokens > 2000:
            recommendations.append({
                "type": "token_optimization",
                "priority": "medium",
                "description": "Reduce average tokens per interaction",
                "rationale": f"Current average is {avg_tokens:.2f} tokens per interaction, which is higher than the recommended maximum of 2000",
                "potential_impact": "Reducing token usage could decrease costs and improve response times",
                "suggested_actions": [
                    "Break complex operations into smaller steps",
                    "Implement caching for repeated operations",
                    "Use more efficient prompt engineering techniques"
                ]
            })
        
        # Check success rate
        success_rate = aggregate_metrics["success_rate"]
        if success_rate < 95:
            recommendations.append({
                "type": "reliability_optimization",
                "priority": "high",
                "description": "Improve LLM interaction success rate",
                "rationale": f"Current success rate is {success_rate:.2f}%, which is below the recommended minimum of 95%",
                "potential_impact": "Improving success rate reduces wasted tokens and improves user experience",
                "suggested_actions": [
                    "Implement better error handling and retry logic",
                    "Review and improve prompts for problematic operations",
                    "Consider using more reliable models for critical operations"
                ]
            })
        
        # Check latency
        avg_latency = aggregate_metrics["avg_latency_ms"]
        if avg_latency > 3000:  # 3 seconds
            recommendations.append({
                "type": "latency_optimization",
                "priority": "medium",
                "description": "Reduce average latency",
                "rationale": f"Current average latency is {avg_latency:.2f}ms, which is higher than the recommended maximum of 3000ms",
                "potential_impact": "Reducing latency improves user experience and system responsiveness",
                "suggested_actions": [
                    "Implement request batching where appropriate",
                    "Consider using faster models for non-critical operations",
                    "Optimize prompt length and complexity"
                ]
            })
        
        # Check for operations with high token usage
        high_token_operations = []
        for op_key, metrics in aggregate_metrics["operation_metrics"].items():
            if metrics["total_interactions"] >= 10 and metrics["total_tokens"] / metrics["total_interactions"] > 3000:
                high_token_operations.append({
                    "operation": op_key,
                    "avg_tokens": metrics["total_tokens"] / metrics["total_interactions"],
                    "total_interactions": metrics["total_interactions"]
                })
        
        if high_token_operations:
            high_token_operations.sort(key=lambda x: x["avg_tokens"], reverse=True)
            top_operations = high_token_operations[:3]  # Top 3 operations
            
            operations_list = ", ".join([f"{op['operation']} ({op['avg_tokens']:.2f} tokens)" for op in top_operations])
            
            recommendations.append({
                "type": "operation_optimization",
                "priority": "high",
                "description": "Optimize high-token operations",
                "rationale": f"The following operations have high token usage: {operations_list}",
                "potential_impact": "Optimizing these operations could significantly reduce overall token usage and cost",
                "suggested_actions": [
                    "Review and optimize prompts for these operations",
                    "Consider breaking these operations into smaller steps",
                    "Implement caching for repeated operations"
                ],
                "target_operations": [op["operation"] for op in top_operations]
            })
        
        # Check for underutilized optimizations
        optimization_types = set(opt["optimization_type"] for opt in optimizations)
        applied_optimization_types = set(opt["optimization_type"] for opt in optimizations if opt["applied"])
        
        unapplied_optimizations = optimization_types - applied_optimization_types
        if unapplied_optimizations:
            recommendations.append({
                "type": "optimization_adoption",
                "priority": "medium",
                "description": "Implement identified optimizations",
                "rationale": f"The following optimization types have been identified but not applied: {', '.join(unapplied_optimizations)}",
                "potential_impact": "Implementing these optimizations could improve efficiency and reduce costs",
                "suggested_actions": [
                    "Review and implement identified optimizations",
                    "Prioritize optimizations with highest potential impact",
                    "Develop a plan for testing and rolling out optimizations"
                ],
                "target_optimizations": list(unapplied_optimizations)
            })
        
        return recommendations
