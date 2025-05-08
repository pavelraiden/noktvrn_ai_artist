# modules/suno/suno_logger.py

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Use standard Python logging
# Configure root logger elsewhere or use basicConfig for standalone testing


class SunoLogger:
    """Provides structured logging for Suno BAS operations."""

    def __init__(self, log_dir: str = "./suno_run_logs"):
        """Initializes the Suno Logger.

        Args:
            log_dir: Directory to store structured run log files.
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = logging.getLogger(
            "SunoBASLogger"
        )  # Dedicated logger instance
        # Avoid adding handlers here if root logger is configured elsewhere
        # If standalone, configure a file handler:
        # log_file = os.path.join(self.log_dir, "suno_bas_operations.log")
        # file_handler = logging.FileHandler(log_file)
        # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # file_handler.setFormatter(formatter)
        # if not self.logger.handlers:
        #     self.logger.addHandler(file_handler)
        #     self.logger.setLevel(logging.INFO)
        self.logger.info(
            f"Suno Logger initialized. Log directory: {self.log_dir}"
        )

    def _get_run_log_filepath(self, run_id: str) -> str:
        """Constructs the filepath for a specific run's structured log."""
        return os.path.join(self.log_dir, f"suno_run_{run_id}_structured.log")

    def _log_structured_event(self, run_id: str, event_data: Dict[str, Any]):
        """Appends a structured event to the run's log file.

        Args:
            run_id: The unique identifier for the generation run.
            event_data: Dictionary containing the event details.
        """
        filepath = self._get_run_log_filepath(run_id)
        event_data["timestamp"] = datetime.utcnow().isoformat()
        try:
            with open(filepath, "a") as f:
                json.dump(event_data, f)
                f.write("\n")  # Newline for each JSON entry
        except IOError as e:
            self.logger.error(
                f"Failed to write structured log for run_id {run_id}: {e}"
            )
        except TypeError as e:
            self.logger.error(
                f"Failed to serialize log event for run_id {run_id}: {e}"
            )

    def start_run(self, run_id: str, initial_prompt: Dict[str, Any]):
        """Logs the start of a generation run."""
        event = {
            "event_type": "run_start",
            "run_id": run_id,
            "initial_prompt": initial_prompt,
        }
        self.logger.info(f"Run started: {run_id}")
        self._log_structured_event(run_id, event)

    def log_step(
        self,
        run_id: str,
        step_index: int,
        action: Dict[str, Any],
        action_result: Dict[str, Any],
        validation_result: Optional[Dict[str, Any]] = None,
    ):
        """Logs the details of a single action step.

        Args:
            run_id: The unique identifier for the generation run.
            step_index: The index of the step.
            action: The action performed.
            action_result: The result of the action.
            validation_result: The result from the feedback loop validation (optional).
        """
        event = {
            "event_type": "step_log",
            "run_id": run_id,
            "step_index": step_index,
            "action": action,
            "action_result": action_result,
            "validation_result": validation_result,
        }
        status = "success" if action_result.get("success") else "failed"
        validation_status = (
            "pending"
            if validation_result is None
            else (
                "approved" if validation_result.get("approved") else "rejected"
            )
        )
        self.logger.info(
            f"Run {run_id}, Step {step_index}: Action=\"{action.get('action')}\" Status={status}, Validation={validation_status}"
        )
        self._log_structured_event(run_id, event)

    def log_event(
        self,
        run_id: str,
        event_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Logs a generic event during the run."""
        event = {
            "event_type": event_type,
            "run_id": run_id,
            "message": message,
            "details": details or {},
        }
        self.logger.info(f"Run {run_id}: [{event_type}] {message}")
        self._log_structured_event(run_id, event)

    def end_run(
        self,
        run_id: str,
        final_output: Optional[Dict[str, Any]],
        status: str,
        error: Optional[str] = None,
    ):
        """Logs the end of a generation run.

        Args:
            run_id: The unique identifier for the generation run.
            final_output: The final result dictionary (e.g., song URL).
            status: Final status ('completed', 'failed', 'cancelled').
            error: Error message if the run failed.
        """
        event = {
            "event_type": "run_end",
            "run_id": run_id,
            "status": status,
            "final_output": final_output,
            "error": error,
        }
        log_level = logging.ERROR if status == "failed" else logging.INFO
        self.logger.log(
            log_level,
            f"Run ended: {run_id}, Status: {status}"
            + (f", Error: {error}" if error else ""),
        )
        self._log_structured_event(run_id, event)


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure basic logging for the example
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger_instance = SunoLogger(log_dir="./test_suno_logs")
    test_id = "logger_test_001"

    prompt = {"lyrics": "Test", "style": "Pop"}
    logger_instance.start_run(test_id, prompt)

    action1 = {"action": "navigate", "url": "https://suno.com/"}
    result1 = {"success": True}
    validation1 = {"approved": True, "feedback": "Navigation OK"}
    logger_instance.log_step(test_id, 1, action1, result1, validation1)

    action2 = {"action": "input", "target": "lyrics_input", "value": "Test"}
    result2 = {"success": False, "error": "Element not found"}
    logger_instance.log_step(
        test_id, 2, action2, result2
    )  # No validation as action failed

    logger_instance.log_event(
        test_id, "retry_attempt", "Attempting retry 1/3", {"retry_count": 1}
    )

    logger_instance.end_run(
        test_id, None, status="failed", error="Element not found during step 2"
    )

    print(f"Check logs in ./test_suno_logs/suno_run_{test_id}_structured.log")

    # Clean up test directory
    # import shutil
    # shutil.rmtree("./test_suno_logs")
    print("Cleanup complete (manual step for safety).")
