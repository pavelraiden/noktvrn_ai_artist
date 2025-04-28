"""
Review Logger Module

This module provides functionality for logging and retrieving review information
during the artist prompt creation process, enabling auditability and rollback.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("review_logger")


class ReviewLogger:
    """
    Logs and retrieves review information during the artist prompt creation process.

    This class saves all intermediate prompt versions, LLM feedbacks, and validation
    results, organized by session ID and iteration number.
    """

    def __init__(
        self,
        storage_dir: str = "/tmp/llm_orchestrator/reviews",
        enable_detailed_logging: bool = True,
    ):
        """
        Initialize a new review logger.

        Args:
            storage_dir: Directory for storing review logs
            enable_detailed_logging: Whether to log detailed information
        """
        self.storage_dir = storage_dir
        self.enable_detailed_logging = enable_detailed_logging

        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

        logger.info(f"Initialized review logger with storage directory: {storage_dir}")

    def log_prompt_version(
        self,
        session_id: str,
        iteration: int,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log a prompt version.

        Args:
            session_id: The ID of the session
            iteration: The iteration number
            prompt: The prompt text
            metadata: Additional metadata for the prompt

        Returns:
            The ID of the logged prompt
        """
        # Create prompt log entry
        timestamp = datetime.now().isoformat()
        prompt_id = f"{session_id}_{iteration}_{timestamp.replace(':', '-')}"

        prompt_data = {
            "id": prompt_id,
            "session_id": session_id,
            "iteration": iteration,
            "timestamp": timestamp,
            "prompt": prompt,
            "metadata": metadata or {},
        }

        # Save to storage
        self._save_log_entry(session_id, "prompts", prompt_id, prompt_data)

        logger.info(
            f"Logged prompt version for session {session_id}, iteration {iteration}"
        )
        return prompt_id

    def log_feedback(
        self,
        session_id: str,
        iteration: int,
        prompt_id: str,
        feedback: Dict[str, Any],
        source: str = "llm_review",
    ) -> str:
        """
        Log feedback for a prompt.

        Args:
            session_id: The ID of the session
            iteration: The iteration number
            prompt_id: The ID of the prompt being reviewed
            feedback: The feedback content
            source: The source of the feedback

        Returns:
            The ID of the logged feedback
        """
        # Create feedback log entry
        timestamp = datetime.now().isoformat()
        feedback_id = f"{session_id}_{iteration}_feedback_{timestamp.replace(':', '-')}"

        feedback_data = {
            "id": feedback_id,
            "session_id": session_id,
            "iteration": iteration,
            "prompt_id": prompt_id,
            "timestamp": timestamp,
            "feedback": feedback,
            "source": source,
        }

        # Save to storage
        self._save_log_entry(session_id, "feedback", feedback_id, feedback_data)

        logger.info(f"Logged feedback for session {session_id}, iteration {iteration}")
        return feedback_id

    def log_validation_result(
        self,
        session_id: str,
        iteration: int,
        prompt_id: str,
        validation_result: Dict[str, Any],
    ) -> str:
        """
        Log validation result for a prompt.

        Args:
            session_id: The ID of the session
            iteration: The iteration number
            prompt_id: The ID of the prompt being validated
            validation_result: The validation result

        Returns:
            The ID of the logged validation result
        """
        # Create validation log entry
        timestamp = datetime.now().isoformat()
        validation_id = (
            f"{session_id}_{iteration}_validation_{timestamp.replace(':', '-')}"
        )

        validation_data = {
            "id": validation_id,
            "session_id": session_id,
            "iteration": iteration,
            "prompt_id": prompt_id,
            "timestamp": timestamp,
            "validation_result": validation_result,
        }

        # Save to storage
        self._save_log_entry(session_id, "validations", validation_id, validation_data)

        logger.info(
            f"Logged validation result for session {session_id}, iteration {iteration}"
        )
        return validation_id

    def log_iteration_summary(
        self,
        session_id: str,
        iteration: int,
        prompt_id: str,
        feedback_id: Optional[str],
        validation_id: str,
        status: str,
        confidence_score: float,
    ) -> str:
        """
        Log a summary of an iteration.

        Args:
            session_id: The ID of the session
            iteration: The iteration number
            prompt_id: The ID of the prompt
            feedback_id: The ID of the feedback (if any)
            validation_id: The ID of the validation result
            status: The status of the iteration
            confidence_score: The confidence score from validation

        Returns:
            The ID of the logged summary
        """
        # Create summary log entry
        timestamp = datetime.now().isoformat()
        summary_id = f"{session_id}_{iteration}_summary_{timestamp.replace(':', '-')}"

        summary_data = {
            "id": summary_id,
            "session_id": session_id,
            "iteration": iteration,
            "timestamp": timestamp,
            "prompt_id": prompt_id,
            "feedback_id": feedback_id,
            "validation_id": validation_id,
            "status": status,
            "confidence_score": confidence_score,
        }

        # Save to storage
        self._save_log_entry(session_id, "summaries", summary_id, summary_data)

        logger.info(
            f"Logged iteration summary for session {session_id}, iteration {iteration}"
        )
        return summary_id

    def get_logs_by_session(self, session_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all logs for a session.

        Args:
            session_id: The ID of the session

        Returns:
            A dictionary of log categories and their entries
        """
        session_dir = os.path.join(self.storage_dir, session_id)
        if not os.path.exists(session_dir):
            logger.warning(f"No logs found for session {session_id}")
            return {}

        logs = {}
        categories = ["prompts", "feedback", "validations", "summaries"]

        for category in categories:
            category_dir = os.path.join(session_dir, category)
            if os.path.exists(category_dir):
                logs[category] = []

                # Get all log files in the category
                log_files = [f for f in os.listdir(category_dir) if f.endswith(".json")]

                # Load each log file
                for log_file in log_files:
                    try:
                        log_path = os.path.join(category_dir, log_file)
                        with open(log_path, "r") as f:
                            log_data = json.load(f)

                        logs[category].append(log_data)
                    except Exception as e:
                        logger.error(f"Error loading log file {log_file}: {str(e)}")

        # Sort logs by iteration and timestamp
        for category in logs:
            logs[category].sort(
                key=lambda x: (x.get("iteration", 0), x.get("timestamp", ""))
            )

        logger.info(
            f"Retrieved {sum(len(logs.get(c, [])) for c in categories)} logs for session {session_id}"
        )
        return logs

    def get_iteration_history(
        self, session_id: str, iteration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get the history for a specific iteration or all iterations.

        Args:
            session_id: The ID of the session
            iteration: The iteration number (None for all iterations)

        Returns:
            A dictionary with iteration history
        """
        # Get all logs for the session
        all_logs = self.get_logs_by_session(session_id)

        # If no logs, return empty history
        if not all_logs:
            return {"iterations": []}

        # Extract summaries
        summaries = all_logs.get("summaries", [])

        # Filter by iteration if specified
        if iteration is not None:
            summaries = [s for s in summaries if s.get("iteration") == iteration]

        # Build iteration history
        iterations = []
        for summary in summaries:
            iter_num = summary.get("iteration")
            prompt_id = summary.get("prompt_id")
            feedback_id = summary.get("feedback_id")
            validation_id = summary.get("validation_id")

            # Find corresponding prompt, feedback, and validation
            prompt_data = next(
                (p for p in all_logs.get("prompts", []) if p.get("id") == prompt_id),
                None,
            )
            feedback_data = next(
                (f for f in all_logs.get("feedback", []) if f.get("id") == feedback_id),
                None,
            )
            validation_data = next(
                (
                    v
                    for v in all_logs.get("validations", [])
                    if v.get("id") == validation_id
                ),
                None,
            )

            # Build iteration data
            iteration_data = {
                "iteration": iter_num,
                "status": summary.get("status"),
                "confidence_score": summary.get("confidence_score"),
                "timestamp": summary.get("timestamp"),
            }

            # Add prompt, feedback, and validation if available
            if prompt_data:
                iteration_data["prompt"] = prompt_data.get("prompt")
                iteration_data["prompt_metadata"] = prompt_data.get("metadata")

            if feedback_data:
                iteration_data["feedback"] = feedback_data.get("feedback")
                iteration_data["feedback_source"] = feedback_data.get("source")

            if validation_data:
                iteration_data["validation_result"] = validation_data.get(
                    "validation_result"
                )

            iterations.append(iteration_data)

        # Sort iterations by iteration number
        iterations.sort(key=lambda x: x.get("iteration", 0))

        logger.info(
            f"Retrieved history for session {session_id}, {'iteration ' + str(iteration) if iteration is not None else 'all iterations'}"
        )
        return {"iterations": iterations}

    def get_latest_prompt(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest prompt for a session.

        Args:
            session_id: The ID of the session

        Returns:
            The latest prompt data, or None if not found
        """
        # Get all logs for the session
        all_logs = self.get_logs_by_session(session_id)

        # If no logs, return None
        if not all_logs or "prompts" not in all_logs:
            return None

        # Get prompts and sort by iteration (descending)
        prompts = all_logs["prompts"]
        prompts.sort(key=lambda x: x.get("iteration", 0), reverse=True)

        # Return the first (latest) prompt
        return prompts[0] if prompts else None

    def get_best_prompt(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the prompt with the highest confidence score for a session.

        Args:
            session_id: The ID of the session

        Returns:
            The best prompt data, or None if not found
        """
        # Get all logs for the session
        all_logs = self.get_logs_by_session(session_id)

        # If no logs, return None
        if not all_logs or "summaries" not in all_logs or "prompts" not in all_logs:
            return None

        # Get summaries and find the one with the highest confidence score
        summaries = all_logs["summaries"]
        if not summaries:
            return None

        best_summary = max(summaries, key=lambda x: x.get("confidence_score", 0))
        best_prompt_id = best_summary.get("prompt_id")

        # Find the corresponding prompt
        best_prompt = next(
            (p for p in all_logs["prompts"] if p.get("id") == best_prompt_id), None
        )

        return best_prompt

    def _save_log_entry(
        self, session_id: str, category: str, entry_id: str, data: Dict[str, Any]
    ) -> None:
        """
        Save a log entry to storage.

        Args:
            session_id: The ID of the session
            category: The category of the log entry
            entry_id: The ID of the log entry
            data: The log entry data
        """
        # Create session directory if it doesn't exist
        session_dir = os.path.join(self.storage_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Create category directory if it doesn't exist
        category_dir = os.path.join(session_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        # Save log entry
        entry_path = os.path.join(category_dir, f"{entry_id}.json")
        try:
            with open(entry_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving log entry {entry_id}: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Create a review logger
    logger = ReviewLogger()

    # Example session and iteration
    session_id = "test_session_123"
    iteration = 1

    # Log a prompt version
    prompt = "A mysterious dark trap artist who thrives in the urban night scene."
    prompt_id = logger.log_prompt_version(session_id, iteration, prompt)

    # Log feedback
    feedback = {
        "suggestions": [
            "Add more details about the artist's appearance",
            "Describe the artist's voice",
        ],
        "rating": 7,
    }
    feedback_id = logger.log_feedback(session_id, iteration, prompt_id, feedback)

    # Log validation result
    validation_result = {
        "result": "needs_improvement",
        "confidence_score": 0.65,
        "feedback": {
            "length": {"status": "pass"},
            "required_elements": {"status": "fail", "missing": ["voice", "appearance"]},
        },
    }
    validation_id = logger.log_validation_result(
        session_id, iteration, prompt_id, validation_result
    )

    # Log iteration summary
    summary_id = logger.log_iteration_summary(
        session_id,
        iteration,
        prompt_id,
        feedback_id,
        validation_id,
        "needs_improvement",
        0.65,
    )

    # Get logs for the session
    logs = logger.get_logs_by_session(session_id)
    print(
        f"Retrieved {sum(len(logs.get(c, [])) for c in logs)} logs for session {session_id}"
    )

    # Get iteration history
    history = logger.get_iteration_history(session_id)
    print(f"Retrieved history with {len(history['iterations'])} iterations")
