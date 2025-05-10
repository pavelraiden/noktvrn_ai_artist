# Self-Learning Module Template

## Overview
This template provides guidance for creating new modules in the AI Artist Creation and Management System with built-in self-learning capabilities. Use this structure to ensure your module can improve over time based on performance data and feedback.

## Module Structure

```
module_name/
├── __init__.py           # Exports public interfaces
├── core.py               # Core functionality
├── models.py             # Data models and schemas
├── adapters.py           # Self-learning adaptation mechanisms
├── metrics.py            # Performance tracking and metrics collection
├── feedback.py           # Feedback processing
├── utils.py              # Helper functions
├── exceptions.py         # Module-specific exceptions
├── config.py             # Configuration handling
└── test_*.py             # Unit tests
```

## Implementation Guidelines

### Step 1: Define the Interface
Begin by defining the public interface for your module, including self-learning capabilities.

```python
# __init__.py
from .core import ModuleNameManager
from .models import ModuleNameConfig, ModuleNameResult
from .adapters import ModuleNameAdapter
from .metrics import ModuleNameMetrics
from .exceptions import ModuleNameError

__all__ = [
    'ModuleNameManager', 
    'ModuleNameConfig', 
    'ModuleNameResult', 
    'ModuleNameAdapter',
    'ModuleNameMetrics',
    'ModuleNameError'
]
```

### Step 2: Create Data Models
Define the data models that your module will use, including metrics and adaptation models.

```python
# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class OperationStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

class ModuleNameConfig(BaseModel):
    """Configuration for the ModuleName module."""
    parameter_1: str = Field(..., description="Description of parameter 1")
    parameter_2: int = Field(42, description="Description of parameter 2")
    optional_param: Optional[str] = Field(None, description="Optional parameter")
    
    # Self-learning configuration
    enable_adaptation: bool = Field(True, description="Enable self-learning adaptations")
    adaptation_threshold: float = Field(0.7, description="Confidence threshold for applying adaptations")
    metrics_collection_level: str = Field("standard", description="Level of metrics to collect (minimal, standard, comprehensive)")
    
    class Config:
        extra = "forbid"  # Prevent extra fields

class ModuleNameResult(BaseModel):
    """Result from ModuleName operations."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(..., description="Result data")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance metadata
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    quality_score: Optional[float] = Field(None, description="Quality score of the result")
    adaptation_applied: Optional[bool] = Field(None, description="Whether adaptation was applied")

class ModuleNameMetricEntry(BaseModel):
    """Single metric entry for the ModuleName module."""
    timestamp: datetime = Field(default_factory=datetime.now)
    operation: str = Field(..., description="Operation name")
    status: OperationStatus = Field(..., description="Operation status")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    context: Dict[str, Any] = Field(default_factory=dict, description="Operation context")
    error: Optional[str] = Field(None, description="Error message if status is FAILURE")
    
class ModuleNameAdaptation(BaseModel):
    """Adaptation record for the ModuleName module."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    parameter_name: str = Field(..., description="Name of parameter being adapted")
    old_value: Any = Field(..., description="Previous parameter value")
    new_value: Any = Field(..., description="New parameter value")
    confidence: float = Field(..., description="Confidence in the adaptation (0-1)")
    reason: str = Field(..., description="Reason for the adaptation")
    metrics_basis: List[str] = Field(..., description="Metric IDs used for this adaptation")
    applied: bool = Field(False, description="Whether the adaptation was applied")
```

### Step 3: Implement Core Functionality
Implement the core functionality of your module with hooks for self-learning.

```python
# core.py
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from .models import ModuleNameConfig, ModuleNameResult, OperationStatus
from .exceptions import ModuleNameError
from .metrics import MetricsCollector
from .adapters import ParameterAdapter

logger = logging.getLogger(__name__)

class ModuleNameManager:
    """Manager class for ModuleName functionality with self-learning capabilities."""
    
    def __init__(self, config: ModuleNameConfig, metrics_collector: Optional[MetricsCollector] = None, 
                 parameter_adapter: Optional[ParameterAdapter] = None):
        """Initialize with configuration and optional components."""
        self.config = config
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.parameter_adapter = parameter_adapter or ParameterAdapter()
        logger.info(f"ModuleNameManager initialized with config: {config}")
    
    def process(self, input_data: Dict[str, Any]) -> ModuleNameResult:
        """Process input data and return a result with performance tracking."""
        operation_id = str(uuid.uuid4())
        start_time = time.time()
        context = {"input_size": len(str(input_data)), "operation_id": operation_id}
        adaptation_applied = False
        
        try:
            logger.debug(f"Processing input: {input_data}, operation_id: {operation_id}")
            
            # Apply parameter adaptations if enabled
            processing_params = self._get_adapted_parameters(input_data)
            if processing_params != self.config.dict():
                adaptation_applied = True
                logger.info(f"Using adapted parameters for operation {operation_id}")
            
            # Implementation logic here
            result_id = f"result_{operation_id}"
            result_data = {"processed": True, "input": input_data}
            
            # Calculate quality score (implementation depends on module)
            quality_score = self._calculate_quality_score(result_data)
            
            # Create result with performance metadata
            execution_time_ms = int((time.time() - start_time) * 1000)
            result = ModuleNameResult(
                id=result_id,
                data=result_data,
                execution_time_ms=execution_time_ms,
                quality_score=quality_score,
                adaptation_applied=adaptation_applied
            )
            
            # Record metrics
            self.metrics_collector.record_operation(
                operation="process",
                status=OperationStatus.SUCCESS,
                duration_ms=execution_time_ms,
                context=context,
                quality_score=quality_score
            )
            
            logger.info(f"Successfully processed input, result ID: {result_id}, execution_time: {execution_time_ms}ms")
            return result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Error processing input: {str(e)}, operation_id: {operation_id}", exc_info=True)
            
            # Record failure metrics
            self.metrics_collector.record_operation(
                operation="process",
                status=OperationStatus.FAILURE,
                duration_ms=execution_time_ms,
                context=context,
                error=str(e)
            )
            
            raise ModuleNameError(f"Failed to process input: {str(e)}") from e
    
    def _get_adapted_parameters(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get parameters adapted based on historical performance."""
        if not self.config.enable_adaptation:
            return self.config.dict()
        
        # Get context-specific adaptations
        context = self._extract_adaptation_context(input_data)
        adapted_params = self.parameter_adapter.get_adapted_parameters(
            base_parameters=self.config.dict(),
            context=context,
            adaptation_threshold=self.config.adaptation_threshold
        )
        
        return adapted_params
    
    def _extract_adaptation_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context for adaptation from input data."""
        # Implementation depends on module specifics
        # Example: extract genre, complexity, size, etc.
        context = {}
        
        # Add relevant context factors
        if "type" in input_data:
            context["input_type"] = input_data["type"]
        
        # Add more context extraction logic
        
        return context
    
    def _calculate_quality_score(self, result_data: Dict[str, Any]) -> float:
        """Calculate quality score for the result."""
        # Implementation depends on module specifics
        # Example: assess completeness, consistency, creativity
        
        # Placeholder implementation
        score = 0.8  # Default good score
        
        # Add quality assessment logic
        
        return score
    
    def get_performance_metrics(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get performance metrics for this module."""
        return self.metrics_collector.get_summary(time_period=time_period)
    
    def apply_feedback(self, result_id: str, feedback_data: Dict[str, Any]) -> None:
        """Apply external feedback to improve future operations."""
        logger.info(f"Received feedback for result {result_id}: {feedback_data}")
        
        # Record feedback for adaptation
        self.parameter_adapter.record_feedback(
            result_id=result_id,
            feedback_data=feedback_data
        )
        
        # Trigger adaptation learning if enough feedback collected
        if self.config.enable_adaptation:
            self.parameter_adapter.learn_from_feedback()
```

### Step 4: Implement Metrics Collection
Create a metrics collection system for tracking performance.

```python
# metrics.py
import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .models import ModuleNameMetricEntry, OperationStatus

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and analyzes performance metrics."""
    
    def __init__(self, storage_backend=None):
        """Initialize with optional storage backend."""
        self.storage = storage_backend or InMemoryMetricsStorage()
        logger.info("MetricsCollector initialized")
    
    def record_operation(self, operation: str, status: OperationStatus, 
                         duration_ms: int, context: Dict[str, Any] = None,
                         quality_score: Optional[float] = None,
                         error: Optional[str] = None) -> str:
        """Record a single operation metric."""
        metric_id = str(uuid.uuid4())
        
        # Enhance context with quality score if available
        context = context or {}
        if quality_score is not None:
            context["quality_score"] = quality_score
        
        # Create metric entry
        entry = ModuleNameMetricEntry(
            id=metric_id,
            timestamp=datetime.now(),
            operation=operation,
            status=status,
            duration_ms=duration_ms,
            context=context,
            error=error
        )
        
        # Store the metric
        self.storage.store_metric(entry)
        
        logger.debug(f"Recorded metric {metric_id} for operation {operation}")
        return metric_id
    
    def get_summary(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get a summary of metrics for the specified time period."""
        # Convert time period to timedelta
        period_delta = self._parse_time_period(time_period)
        start_time = datetime.now() - period_delta
        
        # Retrieve metrics for the period
        metrics = self.storage.get_metrics_since(start_time)
        
        # Calculate summary statistics
        summary = {
            "period": time_period,
            "total_operations": len(metrics),
            "success_rate": self._calculate_success_rate(metrics),
            "average_duration_ms": self._calculate_average_duration(metrics),
            "operation_counts": self._count_by_operation(metrics),
            "status_counts": self._count_by_status(metrics),
            "quality_score_avg": self._calculate_average_quality(metrics),
        }
        
        return summary
    
    def get_metrics_for_context(self, context_filter: Dict[str, Any], 
                               limit: int = 100) -> List[ModuleNameMetricEntry]:
        """Get metrics matching the specified context filter."""
        return self.storage.get_metrics_by_context(context_filter, limit)
    
    def _parse_time_period(self, time_period: str) -> timedelta:
        """Convert time period string to timedelta."""
        if time_period == "1h":
            return timedelta(hours=1)
        elif time_period == "24h":
            return timedelta(days=1)
        elif time_period == "7d":
            return timedelta(days=7)
        elif time_period == "30d":
            return timedelta(days=30)
        else:
            # Default to 24 hours
            logger.warning(f"Unknown time period {time_period}, using 24h")
            return timedelta(days=1)
    
    def _calculate_success_rate(self, metrics: List[ModuleNameMetricEntry]) -> float:
        """Calculate success rate from metrics."""
        if not metrics:
            return 0.0
        
        success_count = sum(1 for m in metrics if m.status == OperationStatus.SUCCESS)
        return (success_count / len(metrics)) * 100
    
    def _calculate_average_duration(self, metrics: List[ModuleNameMetricEntry]) -> float:
        """Calculate average duration from metrics."""
        if not metrics:
            return 0.0
        
        total_duration = sum(m.duration_ms for m in metrics)
        return total_duration / len(metrics)
    
    def _calculate_average_quality(self, metrics: List[ModuleNameMetricEntry]) -> float:
        """Calculate average quality score from metrics."""
        quality_metrics = [m for m in metrics if "quality_score" in m.context]
        if not quality_metrics:
            return 0.0
        
        total_quality = sum(m.context["quality_score"] for m in quality_metrics)
        return total_quality / len(quality_metrics)
    
    def _count_by_operation(self, metrics: List[ModuleNameMetricEntry]) -> Dict[str, int]:
        """Count metrics by operation."""
        counts = {}
        for metric in metrics:
            counts[metric.operation] = counts.get(metric.operation, 0) + 1
        return counts
    
    def _count_by_status(self, metrics: List[ModuleNameMetricEntry]) -> Dict[str, int]:
        """Count metrics by status."""
        counts = {}
        for metric in metrics:
            counts[metric.status] = counts.get(metric.status, 0) + 1
        return counts


class InMemoryMetricsStorage:
    """In-memory storage for metrics."""
    
    def __init__(self, max_size: int = 10000):
        """Initialize with maximum storage size."""
        self.metrics = []
        self.max_size = max_size
    
    def store_metric(self, metric: ModuleNameMetricEntry) -> None:
        """Store a metric entry."""
        self.metrics.append(metric)
        
        # Trim if exceeding max size
        if len(self.metrics) > self.max_size:
            self.metrics = self.metrics[-self.max_size:]
    
    def get_metrics_since(self, start_time: datetime) -> List[ModuleNameMetricEntry]:
        """Get metrics since the specified time."""
        return [m for m in self.metrics if m.timestamp >= start_time]
    
    def get_metrics_by_context(self, context_filter: Dict[str, Any], 
                              limit: int) -> List[ModuleNameMetricEntry]:
        """Get metrics matching the context filter."""
        result = []
        for metric in reversed(self.metrics):  # Most recent first
            matches = True
            for key, value in context_filter.items():
                if key not in metric.context or metric.context[key] != value:
                    matches = False
                    break
            
            if matches:
                result.append(metric)
                if len(result) >= limit:
                    break
        
        return result
```

### Step 5: Implement Adaptation Mechanisms
Create adaptation mechanisms that learn from performance data.

```python
# adapters.py
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .models import ModuleNameAdaptation

logger = logging.getLogger(__name__)

class ParameterAdapter:
    """Adapts parameters based on performance metrics and feedback."""
    
    def __init__(self, storage_backend=None):
        """Initialize with optional storage backend."""
        self.storage = storage_backend or InMemoryAdaptationStorage()
        logger.info("ParameterAdapter initialized")
    
    def get_adapted_parameters(self, base_parameters: Dict[str, Any], 
                              context: Dict[str, Any],
                              adaptation_threshold: float = 0.7) -> Dict[str, Any]:
        """Get parameters adapted for the specific context."""
        # Start with base parameters
        adapted_params = base_parameters.copy()
        
        # Get relevant adaptations for this context
        adaptations = self.storage.get_adaptations_for_context(context)
        
        # Apply adaptations that meet the threshold
        for adaptation in adaptations:
            if adaptation.confidence >= adaptation_threshold:
                logger.debug(f"Applying adaptation {adaptation.id}: {adaptation.parameter_name} = {adaptation.new_value}")
                adapted_params[adaptation.parameter_name] = adaptation.new_value
                
                # Mark as applied
                adaptation.applied = True
                self.storage.update_adaptation(adaptation)
        
        return adapted_params
    
    def suggest_adaptation(self, parameter_name: str, current_value: Any, 
                          suggested_value: Any, confidence: float,
                          reason: str, metrics_basis: List[str],
                          context: Dict[str, Any]) -> str:
        """Suggest a parameter adaptation based on observed patterns."""
        adaptation_id = str(uuid.uuid4())
        
        # Create adaptation record
        adaptation = ModuleNameAdaptation(
            id=adaptation_id,
            created_at=datetime.now(),
            parameter_name=parameter_name,
            old_value=current_value,
            new_value=suggested_value,
            confidence=confidence,
            reason=reason,
            metrics_basis=metrics_basis,
            context=context,
            applied=False
        )
        
        # Store the adaptation
        self.storage.store_adaptation(adaptation)
        
        logger.info(f"Suggested adaptation {adaptation_id}: {parameter_name} from {current_value} to {suggested_value} with confidence {confidence}")
        return adaptation_id
    
    def record_feedback(self, result_id: str, feedback_data: Dict[str, Any]) -> None:
        """Record feedback for a result to inform future adaptations."""
        self.storage.store_feedback(result_id, feedback_data)
        logger.debug(f"Recorded feedback for result {result_id}")
    
    def learn_from_feedback(self) -> List[str]:
        """Analyze feedback and generate new adaptations."""
        # Get unprocessed feedback
        feedback_entries = self.storage.get_unprocessed_feedback(limit=100)
        if not feedback_entries:
            return []
        
        logger.info(f"Learning from {len(feedback_entries)} feedback entries")
        
        # Group feedback by context patterns
        grouped_feedback = self._group_feedback_by_context(feedback_entries)
        
        # Generate adaptations based on patterns
        adaptation_ids = []
        for context, entries in grouped_feedback.items():
            new_adaptations = self._generate_adaptations_from_feedback(context, entries)
            adaptation_ids.extend(new_adaptations)
            
        # Mark feedback as processed
        self.storage.mark_feedback_processed([f["id"] for f in feedback_entries])
        
        return adaptation_ids
    
    def _group_feedback_by_context(self, feedback_entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group feedback entries by context similarity."""
        # Implementation depends on specific context factors
        # Simplified example: group by input_type if present
        grouped = {}
        
        for entry in feedback_entries:
            context = entry.get("context", {})
            key = context.get("input_type", "default")
            
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(entry)
        
        return grouped
    
    def _generate_adaptations_from_feedback(self, context_key: str, 
                                           feedback_entries: List[Dict[str, Any]]) -> List[str]:
        """Generate adaptations based on feedback patterns."""
        # Implementation depends on specific adaptation strategies
        # Simplified example: adjust temperature based on quality feedback
        
        adaptation_ids = []
        
        # Example: If multiple entries show quality issues, suggest temperature adjustment
        quality_scores = [f.get("quality_score", 0) for f in feedback_entries if "quality_score" in f]
        if quality_scores and len(quality_scores) >= 3:
            avg_quality = sum(quality_scores) / len(quality_scores)
            
            # If quality is consistently low, suggest higher temperature
            if avg_quality < 0.5:
                context = {"input_type": context_key}
                adaptation_id = self.suggest_adaptation(
                    parameter_name="temperature",
                    current_value=0.7,  # Would come from base parameters
                    suggested_value=0.8,
                    confidence=0.75,
                    reason=f"Low quality scores (avg: {avg_quality}) suggest need for more creativity",
                    metrics_basis=[f["id"] for f in feedback_entries],
                    context=context
                )
                adaptation_ids.append(adaptation_id)
        
        return adaptation_ids


class InMemoryAdaptationStorage:
    """In-memory storage for adaptations and feedback."""
    
    def __init__(self):
        """Initialize storage."""
        self.adaptations = []
        self.feedback = []
    
    def store_adaptation(self, adaptation: ModuleNameAdaptation) -> None:
        """Store an adaptation."""
        self.adaptations.append(adaptation)
    
    def update_adaptation(self, adaptation: ModuleNameAdaptation) -> None:
        """Update an existing adaptation."""
        for i, a in enumerate(self.adaptations):
            if a.id == adaptation.id:
                self.adaptations[i] = adaptation
                break
    
    def get_adaptations_for_context(self, context: Dict[str, Any]) -> List[ModuleNameAdaptation]:
        """Get adaptations relevant for the given context."""
        # Simplified matching logic - in production would use more sophisticated matching
        result = []
        for adaptation in self.adaptations:
            # Check if adaptation context is a subset of the given context
            if all(k in context and context[k] == v for k, v in adaptation.context.items()):
                result.append(adaptation)
        return result
    
    def store_feedback(self, result_id: str, feedback_data: Dict[str, Any]) -> None:
        """Store feedback for a result."""
        feedback_entry = {
            "id": str(uuid.uuid4()),
            "result_id": result_id,
            "timestamp": datetime.now(),
            "data": feedback_data,
            "processed": False
        }
        self.feedback.append(feedback_entry)
    
    def get_unprocessed_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get unprocessed feedback entries."""
        unprocessed = [f for f in self.feedback if not f["processed"]]
        return unprocessed[:limit]
    
    def mark_feedback_processed(self, feedback_ids: List[str]) -> None:
        """Mark feedback entries as processed."""
        for feedback in self.feedback:
            if feedback["id"] in feedback_ids:
                feedback["processed"] = True
```

### Step 6: Implement Feedback Processing
Create a system for processing external feedback.

```python
# feedback.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .adapters import ParameterAdapter

logger = logging.getLogger(__name__)

class FeedbackProcessor:
    """Processes external feedback to improve module performance."""
    
    def __init__(self, parameter_adapter: ParameterAdapter):
        """Initialize with parameter adapter."""
        self.parameter_adapter = parameter_adapter
        logger.info("FeedbackProcessor initialized")
    
    def process_user_feedback(self, result_id: str, user_rating: int, 
                             comments: Optional[str] = None) -> None:
        """Process user feedback for a result."""
        logger.info(f"Processing user feedback for result {result_id}: rating={user_rating}, comments={comments}")
        
        # Convert to standardized feedback format
        feedback_data = {
            "source": "user",
            "rating": user_rating,
            "comments": comments,
            "timestamp": datetime.now().isoformat(),
            "quality_score": user_rating / 5.0  # Normalize to 0-1 range
        }
        
        # Record feedback for adaptation
        self.parameter_adapter.record_feedback(result_id, feedback_data)
    
    def process_performance_feedback(self, result_id: str, metrics: Dict[str, Any]) -> None:
        """Process automated performance feedback."""
        logger.info(f"Processing performance feedback for result {result_id}")
        
        # Convert to standardized feedback format
        feedback_data = {
            "source": "automated",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate quality score if possible
        if "error_rate" in metrics:
            feedback_data["quality_score"] = 1.0 - metrics["error_rate"]
        
        # Record feedback for adaptation
        self.parameter_adapter.record_feedback(result_id, feedback_data)
    
    def trigger_learning_cycle(self) -> List[str]:
        """Trigger a learning cycle to generate adaptations from feedback."""
        logger.info("Triggering learning cycle from feedback")
        return self.parameter_adapter.learn_from_feedback()
```

### Step 7: Define Exceptions
Create custom exceptions for your module.

```python
# exceptions.py
class ModuleNameError(Exception):
    """Base exception for ModuleName module."""
    pass

class ModuleNameConfigError(ModuleNameError):
    """Exception raised for configuration errors."""
    pass

class ModuleNameProcessingError(ModuleNameError):
    """Exception raised for processing errors."""
    pass

class ModuleNameAdaptationError(ModuleNameError):
    """Exception raised for adaptation errors."""
    pass

class ModuleNameMetricsError(ModuleNameError):
    """Exception raised for metrics collection errors."""
    pass
```

### Step 8: Write Tests
Create comprehensive tests for your module, including self-learning components.

```python
# test_core.py
import unittest
from unittest.mock import MagicMock, patch
from .core import ModuleNameManager
from .models import ModuleNameConfig, OperationStatus
from .metrics import MetricsCollector
from .adapters import ParameterAdapter
from .exceptions import ModuleNameError

class TestModuleNameManager(unittest.TestCase):
    
    def setUp(self):
        self.metrics_collector = MagicMock(spec=MetricsCollector)
        self.parameter_adapter = MagicMock(spec=ParameterAdapter)
        self.config = ModuleNameConfig(parameter_1="test")
        self.manager = ModuleNameManager(
            self.config, 
            metrics_collector=self.metrics_collector,
            parameter_adapter=self.parameter_adapter
        )
    
    def test_process_valid_input(self):
        # Setup
        input_data = {"key": "value"}
        self.parameter_adapter.get_adapted_parameters.return_value = self.config.dict()
        
        # Execute
        result = self.manager.process(input_data)
        
        # Assert
        self.assertEqual(result.data["input"], input_data)
        self.assertTrue(result.data["processed"])
        self.assertIsNotNone(result.execution_time_ms)
        self.assertIsNotNone(result.quality_score)
        
        # Verify metrics were collected
        self.metrics_collector.record_operation.assert_called_once()
        call_args = self.metrics_collector.record_operation.call_args[1]
        self.assertEqual(call_args["operation"], "process")
        self.assertEqual(call_args["status"], OperationStatus.SUCCESS)
    
    def test_process_with_adaptation(self):
        # Setup
        input_data = {"key": "value"}
        adapted_params = self.config.dict()
        adapted_params["parameter_2"] = 99  # Changed parameter
        self.parameter_adapter.get_adapted_parameters.return_value = adapted_params
        
        # Execute
        result = self.manager.process(input_data)
        
        # Assert
        self.assertTrue(result.adaptation_applied)
        
        # Verify parameter adaptation was requested
        self.parameter_adapter.get_adapted_parameters.assert_called_once()
    
    def test_process_invalid_input(self):
        # Setup
        self.parameter_adapter.get_adapted_parameters.return_value = self.config.dict()
        
        # Execute and Assert
        with self.assertRaises(ModuleNameError):
            self.manager.process(None)
        
        # Verify failure metrics were collected
        self.metrics_collector.record_operation.assert_called_once()
        call_args = self.metrics_collector.record_operation.call_args[1]
        self.assertEqual(call_args["operation"], "process")
        self.assertEqual(call_args["status"], OperationStatus.FAILURE)
    
    def test_apply_feedback(self):
        # Setup
        result_id = "test_result_123"
        feedback_data = {"rating": 4, "comments": "Good result"}
        
        # Execute
        self.manager.apply_feedback(result_id, feedback_data)
        
        # Verify feedback was recorded
        self.parameter_adapter.record_feedback.assert_called_once_with(
            result_id=result_id,
            feedback_data=feedback_data
        )
        
        # Verify learning was triggered
        self.parameter_adapter.learn_from_feedback.assert_called_once()
```

## Integration Guidelines

### Self-Learning Integration
- Connect your module to the system's feedback loops
- Implement metrics collection for all operations
- Use the adaptation mechanisms for parameter tuning
- Regularly trigger learning cycles to improve performance

### Dependency Injection
- Use dependency injection to provide required services
- Make self-learning components optional but enabled by default
- Allow configuration of adaptation thresholds and learning rates
- Provide interfaces for storage backends to support different persistence options

### Error Handling
- Catch specific exceptions, not generic ones
- Include context in error messages for better debugging
- Log errors with appropriate severity levels
- Ensure self-learning components fail gracefully

### Logging
- Log all adaptations with their rationale
- Use debug level for detailed metrics
- Use info level for successful adaptations
- Use warning level for rejected adaptations
- Use error level for adaptation failures

## Documentation Requirements

- Include docstrings for all public classes and methods
- Document self-learning capabilities and configuration options
- Provide examples of how to use and configure adaptations
- Explain the metrics collected and how they're used
- Document the feedback mechanisms and how to integrate with them

## Performance Considerations

- Ensure metrics collection has minimal performance impact
- Use sampling for high-volume operations
- Consider asynchronous processing for adaptation learning
- Implement caching for frequently accessed metrics
- Use efficient storage backends for production environments

## Example Usage

```python
# Basic usage with self-learning enabled
config = ModuleNameConfig(
    parameter_1="value",
    enable_adaptation=True,
    adaptation_threshold=0.8
)
manager = ModuleNameManager(config)
result = manager.process({"input": "data"})

# Providing feedback
manager.apply_feedback(
    result_id=result.id,
    feedback_data={"quality": 0.9, "user_rating": 5}
)

# Checking performance metrics
metrics = manager.get_performance_metrics(time_period="7d")
print(f"Success rate: {metrics['success_rate']}%")
print(f"Average quality: {metrics['quality_score_avg']}")
```
