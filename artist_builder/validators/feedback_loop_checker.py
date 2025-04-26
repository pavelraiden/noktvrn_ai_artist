"""
Feedback Loop Checker Module

This module provides functionality for monitoring prompt improvement across
multiple revision cycles and determining when to stop the feedback loop.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import statistics
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("feedback_loop_checker")


class FeedbackLoopStatus(Enum):
    """Status of a feedback loop."""
    IN_PROGRESS = "in_progress"
    COMPLETED_SUCCESS = "completed_success"
    COMPLETED_MAX_ITERATIONS = "completed_max_iterations"
    COMPLETED_NO_IMPROVEMENT = "completed_no_improvement"
    FAILED = "failed"


class FeedbackLoopChecker:
    """
    Monitors prompt improvement across multiple revision cycles.
    
    This class tracks validation scores over iterations, detects improvement
    trends, and determines when to stop the feedback loop.
    """
    
    def __init__(
        self,
        max_iterations: int = 3,
        success_threshold: float = 0.8,
        improvement_threshold: float = 0.05,
        consecutive_no_improvement: int = 2
    ):
        """
        Initialize a new feedback loop checker.
        
        Args:
            max_iterations: Maximum number of revision cycles allowed
            success_threshold: Confidence score threshold for success
            improvement_threshold: Minimum score improvement to be considered significant
            consecutive_no_improvement: Number of consecutive iterations without improvement before stopping
        """
        self.max_iterations = max_iterations
        self.success_threshold = success_threshold
        self.improvement_threshold = improvement_threshold
        self.consecutive_no_improvement = consecutive_no_improvement
        
        # Initialize tracking variables
        self.iterations: List[Dict[str, Any]] = []
        self.current_status = FeedbackLoopStatus.IN_PROGRESS
        
        logger.info(f"Initialized feedback loop checker with max {max_iterations} iterations")
    
    def track_iteration(
        self,
        iteration_number: int,
        confidence_score: float,
        validation_result: str,
        feedback: Dict[str, Any]
    ) -> None:
        """
        Track a new iteration in the feedback loop.
        
        Args:
            iteration_number: The current iteration number (1-based)
            confidence_score: The confidence score from validation
            validation_result: The validation result (valid, needs_improvement, invalid)
            feedback: Detailed feedback from validation
        """
        # Create iteration record
        iteration = {
            "iteration_number": iteration_number,
            "confidence_score": confidence_score,
            "validation_result": validation_result,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to iterations list
        self.iterations.append(iteration)
        
        # Update status based on new iteration
        self._update_status()
        
        logger.info(f"Tracked iteration {iteration_number} with score {confidence_score:.2f}, status: {self.current_status.value}")
    
    def should_continue(self) -> bool:
        """
        Determine if the feedback loop should continue.
        
        Returns:
            True if the loop should continue, False if it should stop
        """
        return self.current_status == FeedbackLoopStatus.IN_PROGRESS
    
    def get_improvement_trend(self) -> Dict[str, Any]:
        """
        Analyze the improvement trend across iterations.
        
        Returns:
            A dictionary with trend analysis
        """
        if len(self.iterations) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Not enough iterations to determine trend",
                "data": []
            }
        
        # Extract scores
        scores = [iteration["confidence_score"] for iteration in self.iterations]
        
        # Calculate changes between consecutive iterations
        changes = [scores[i] - scores[i-1] for i in range(1, len(scores))]
        
        # Calculate statistics
        avg_change = statistics.mean(changes) if changes else 0
        
        # Determine trend
        if avg_change > self.improvement_threshold:
            trend = "improving"
            message = "Prompt quality is improving with each iteration"
        elif avg_change < -self.improvement_threshold:
            trend = "declining"
            message = "Prompt quality is declining with each iteration"
        else:
            trend = "stable"
            message = "Prompt quality is relatively stable across iterations"
        
        return {
            "trend": trend,
            "message": message,
            "data": {
                "scores": scores,
                "changes": changes,
                "average_change": avg_change
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the feedback loop.
        
        Returns:
            A dictionary with status information
        """
        return {
            "status": self.current_status.value,
            "iterations_completed": len(self.iterations),
            "max_iterations": self.max_iterations,
            "latest_score": self.iterations[-1]["confidence_score"] if self.iterations else None,
            "best_score": max([i["confidence_score"] for i in self.iterations]) if self.iterations else None,
            "improvement_trend": self.get_improvement_trend() if len(self.iterations) > 1 else None
        }
    
    def get_best_iteration(self) -> Optional[Dict[str, Any]]:
        """
        Get the iteration with the highest confidence score.
        
        Returns:
            The iteration with the highest score, or None if no iterations
        """
        if not self.iterations:
            return None
        
        return max(self.iterations, key=lambda i: i["confidence_score"])
    
    def _update_status(self) -> None:
        """Update the current status based on iterations."""
        if not self.iterations:
            self.current_status = FeedbackLoopStatus.IN_PROGRESS
            return
        
        latest_iteration = self.iterations[-1]
        latest_score = latest_iteration["confidence_score"]
        
        # Check if latest score exceeds success threshold
        if latest_score >= self.success_threshold:
            self.current_status = FeedbackLoopStatus.COMPLETED_SUCCESS
            return
        
        # Check if max iterations reached
        if len(self.iterations) >= self.max_iterations:
            self.current_status = FeedbackLoopStatus.COMPLETED_MAX_ITERATIONS
            return
        
        # Check for consecutive iterations without improvement
        if len(self.iterations) >= 2:
            recent_scores = [i["confidence_score"] for i in self.iterations[-self.consecutive_no_improvement-1:]]
            improving = any(recent_scores[i] > recent_scores[i-1] + self.improvement_threshold 
                           for i in range(1, len(recent_scores)))
            
            if not improving and len(self.iterations) >= self.consecutive_no_improvement + 1:
                self.current_status = FeedbackLoopStatus.COMPLETED_NO_IMPROVEMENT
                return
        
        # Check if all iterations have failed validation
        all_invalid = all(i["validation_result"] == "invalid" for i in self.iterations)
        if all_invalid and len(self.iterations) >= 2:
            self.current_status = FeedbackLoopStatus.FAILED
            return
        
        # Default: still in progress
        self.current_status = FeedbackLoopStatus.IN_PROGRESS


# Example usage
if __name__ == "__main__":
    # Create a feedback loop checker
    checker = FeedbackLoopChecker()
    
    # Track some iterations
    checker.track_iteration(
        iteration_number=1,
        confidence_score=0.6,
        validation_result="needs_improvement",
        feedback={"improvement_suggestions": ["Add more details about the artist's style"]}
    )
    
    checker.track_iteration(
        iteration_number=2,
        confidence_score=0.75,
        validation_result="needs_improvement",
        feedback={"improvement_suggestions": ["Improve coherence between paragraphs"]}
    )
    
    checker.track_iteration(
        iteration_number=3,
        confidence_score=0.85,
        validation_result="valid",
        feedback={"improvement_suggestions": []}
    )
    
    # Check status
    status = checker.get_status()
    print(f"Status: {status['status']}")
    print(f"Iterations completed: {status['iterations_completed']}")
    print(f"Latest score: {status['latest_score']:.2f}")
    print(f"Best score: {status['best_score']:.2f}")
    
    # Get improvement trend
    trend = checker.get_improvement_trend()
    print(f"\nImprovement trend: {trend['trend']}")
    print(f"Message: {trend['message']}")
    
    # Get best iteration
    best = checker.get_best_iteration()
    print(f"\nBest iteration: {best['iteration_number']} with score {best['confidence_score']:.2f}")
