# modules/suno/suno_state_manager.py

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime  # Added missing import

logger = logging.getLogger(__name__)


class SunoStateManagerError(Exception):
    """Custom exception for State Manager errors."""


class SunoStateManager:
    """Manages the state of Suno generation runs, including retries and progress."""

    def __init__(self, state_dir: str = "./suno_run_states"):
        """Initializes the State Manager.

        Args:
            state_dir: Directory to store run state files.
        """
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        logger.info(
            f"Suno State Manager initialized. "
            f"State directory: {self.state_dir}"
        )

    def _get_state_filepath(self, run_id: str) -> str:
        """Constructs the filepath for a given run_id."""
        return os.path.join(self.state_dir, f"suno_run_{run_id}.json")

    def load_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Loads the state for a given run_id.

        Args:
            run_id: The unique identifier for the generation run.

        Returns:
            The loaded state dictionary, or None if no state file exists.
        """
        filepath = self._get_state_filepath(run_id)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    state = json.load(f)
                    logger.info(f"Loaded state for run_id: {run_id}")
                    return state
            except json.JSONDecodeError as e:
                logger.error(
                    f"Error decoding state file for run_id {run_id}: {e}"
                )
                raise SunoStateManagerError(
                    f"Failed to decode state file: {filepath}"
                ) from e
            except IOError as e:
                logger.error(
                    f"Error reading state file for run_id {run_id}: {e}"
                )
                raise SunoStateManagerError(
                    f"Failed to read state file: {filepath}"
                ) from e
        else:
            logger.info(
                f"No existing state found for run_id: {run_id}. "
                f"Starting fresh."
            )
            return None

    def save_state(self, run_id: str, state: Dict[str, Any]):
        """Saves the current state for a given run_id.

        Args:
            run_id: The unique identifier for the generation run.
            state: The state dictionary to save.
        """
        filepath = self._get_state_filepath(run_id)
        try:
            # Add timestamp or versioning if needed
            state["_last_updated"] = datetime.utcnow().isoformat()
            with open(filepath, "w") as f:
                json.dump(state, f, indent=4)
            logger.info(f"Saved state for run_id: {run_id}")
        except IOError as e:
            logger.error(f"Error writing state file for run_id {run_id}: {e}")
            raise SunoStateManagerError(
                f"Failed to write state file: {filepath}"
            ) from e
        except TypeError as e:
            logger.error(f"Error serializing state for run_id {run_id}: {e}")
            raise SunoStateManagerError(
                "State object is not JSON serializable"
            ) from e

    def update_state(self, run_id: str, update_data: Dict[str, Any]):
        """Loads, updates, and saves the state for a run_id.

        Args:
            run_id: The unique identifier for the generation run.
            update_data: Dictionary containing data to update in the state.
        """
        current_state = self.load_state(run_id) or {}
        current_state.update(update_data)
        self.save_state(run_id, current_state)
        logger.debug(
            f"Updated state for run_id: {run_id} "
            f"with keys: {list(update_data.keys())}"
        )

    def save_final_state(
        self,
        run_id: str,
        final_output: Optional[Dict[str, Any]],
        status: str = "unknown",
        error: Optional[str] = None,
    ):
        """Saves the final state, including status and any errors.

        Args:
            run_id: The unique identifier for the generation run.
            final_output: The final result dictionary (e.g., song URL).
            status: Final status ("completed", "failed", "cancelled").
            error: Error message if the run failed.
        """
        final_state = {
            "status": status,
            "final_output": final_output,
            "error": error,
        }
        self.update_state(run_id, final_state)
        logger.info(
            f"Saved final state for run_id: {run_id} with status: {status}"
        )


# Example usage (for testing purposes)
if __name__ == "__main__":
    import logging

    # from datetime import datetime # Already imported above
    logging.basicConfig(level=logging.DEBUG)

    manager = SunoStateManager(state_dir="./test_suno_states")
    test_id = "state_test_001"

    # Initial load (should be None)
    print(f"Initial state: {manager.load_state(test_id)}")

    # Save initial state
    initial_state = {"prompt": "test prompt", "step": 1, "retries": 0}
    manager.save_state(test_id, initial_state)

    # Load again
    print(f"Loaded state: {manager.load_state(test_id)}")

    # Update state
    manager.update_state(
        test_id, {"step": 2, "last_action_result": {"success": True}}
    )
    print(f"Updated state: {manager.load_state(test_id)}")

    # Save final state (success)
    manager.save_final_state(
        test_id, {"song_url": "fake_url"}, status="completed"
    )
    print(f"Final state (success): {manager.load_state(test_id)}")

    # Save final state (failure)
    test_id_fail = "state_test_002"
    manager.save_final_state(
        test_id_fail, None, status="failed", error="Something went wrong"
    )
    print(f"Final state (failure): {manager.load_state(test_id_fail)}")

    # Clean up test directory

    # shutil.rmtree("./test_suno_states")
    print("Cleanup complete (manual step for safety).")
