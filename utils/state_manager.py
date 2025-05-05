# /home/ubuntu/ai_artist_system_clone/utils/state_manager.py
"""Module to handle state capture, persistence, and restoration."""

import json
import os
import logging
import subprocess
from datetime import datetime, timezone

# Configure logger for this module
logger = logging.getLogger(__name__)

# Define the path for the recovery manifest file
RECOVERY_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "recovery.json")
)


def get_current_git_branch(repo_path):
    """Gets the current Git branch name."""
    try:
        # Ensure we are in the correct directory for the git command
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_path
        )
        branch_name = result.stdout.strip()
        logger.debug(f"Current Git branch: {branch_name}")
        return branch_name
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Error getting Git branch: {e}")
        return "unknown_branch"


def capture_state(task_desc, last_step, next_step, knowledge_ids, repo_path):
    """Gathers critical state information from the agent's context.

    Args:
        task_desc (str): Description of the current task.
        last_step (str): ID of the last completed plan step.
        next_step (str): ID of the next plan step.
        knowledge_ids (list[str]): List of relevant knowledge base entry IDs.
        repo_path (str): Absolute path to the git repository.
    """
    logger.info("Capturing agent state...")

    # Get current Git branch
    git_branch = get_current_git_branch(repo_path)

    state_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_task_description": task_desc, # Provided by caller
        "last_completed_step_id": last_step,   # Provided by caller
        "next_step_id": next_step,             # Provided by caller
        "git_branch": git_branch,             # Retrieved via git command
        "relevant_knowledge_ids": knowledge_ids, # Provided by caller
        "volatile_state": {}, # Keep minimal for now
    }
    # TODO: Potentially add more state if needed (e.g., specific file versions)
    logger.debug(f"Captured state data: {state_data}")
    return state_data


def save_recovery_manifest(state_data):
    """Saves the captured state data to the recovery manifest file."""
    logger.info(f"Saving recovery manifest to {RECOVERY_FILE_PATH}")
    try:
        with open(RECOVERY_FILE_PATH, "w") as f:
            json.dump(state_data, f, indent=2)
        logger.info("Recovery manifest saved successfully.")
        return True
    except IOError as e:
        logger.error(f"Error saving recovery manifest: {e}")
        return False
    except TypeError as e:
        logger.error(f"Error serializing state data to JSON: {e}")
        return False


def read_recovery_manifest():
    """Reads and parses the recovery manifest file."""
    logger.info(f"Reading recovery manifest from {RECOVERY_FILE_PATH}")
    if not os.path.exists(RECOVERY_FILE_PATH):
        logger.warning("Recovery manifest file not found.")
        return None
    try:
        with open(RECOVERY_FILE_PATH, "r") as f:
            state_data = json.load(f)
        logger.info("Recovery manifest read successfully.")
        logger.debug(f"Read state data: {state_data}")
        return state_data
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error reading or parsing recovery manifest: {e}")
        return None


def restore_state(agent_context): # Added agent_context placeholder
    """Restores the agent's state based on the recovery manifest.

    Args:
        agent_context: Placeholder for the agent's internal context/state object
                       which needs to be updated.
    """
    logger.info("Attempting to restore agent state...")
    state_data = read_recovery_manifest()
    if state_data:
        logger.info(f"Restoring state from manifest dated {state_data.get('timestamp')}")
        # Placeholder: Implement logic to apply the state_data to the agent's context
        # Example (conceptual):
        # agent_context.set_current_task(state_data.get('current_task_description'))
        # agent_context.set_plan_steps(state_data.get('last_completed_step_id'), state_data.get('next_step_id'))
        # agent_context.load_knowledge(state_data.get('relevant_knowledge_ids'))
        # agent_context.restore_volatile_state(state_data.get('volatile_state'))

        # Handle Git branch checkout if necessary (requires repo_path)
        # current_branch = get_current_git_branch(repo_path)
        # target_branch = state_data.get('git_branch')
        # if target_branch and current_branch != target_branch:
        #     logger.info(f"Checking out Git branch: {target_branch}")
        #     try:
        #         subprocess.run(["git", "checkout", target_branch], check=True, cwd=repo_path)
        #     except Exception as e:
        #         logger.error(f"Failed to checkout branch {target_branch}: {e}")

        logger.info("State restoration logic needs full implementation using agent context.")
        # TODO: Implement actual state restoration using agent_context object
        logger.info("Agent state restored (partially - implementation pending).")
        return state_data # Return the loaded state for confirmation/use
    else:
        logger.info("No recovery data found or error reading manifest. Starting fresh.")
        return None


# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing state manager functions...")

    # Define repo path for testing
    repo_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Simulate context for capture
    sim_task = "Implement self-restoration layer"
    sim_last_step = "017"
    sim_next_step = "018"
    sim_knowledge = ["user_56", "user_63", "user_59"]

    # Test capture and save
    current_state = capture_state(
        sim_task, sim_last_step, sim_next_step, sim_knowledge, repo_directory
    )
    saved = save_recovery_manifest(current_state)

    if saved:
        # Test read and restore
        # Simulate providing an agent context object (even if just a dict for this test)
        sim_agent_context = {}
        restored_state_info = restore_state(sim_agent_context)
        if restored_state_info:
            logger.info("Restoration test successful (data loaded).")
            # Conceptual check
            # assert sim_agent_context.get('current_task') == sim_task
        else:
            logger.error("Restoration test failed (data not loaded).")
    else:
        logger.error("Save manifest failed, cannot test restoration.")

