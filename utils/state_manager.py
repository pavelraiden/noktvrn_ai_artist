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
DEV_DIARY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "dev_diary.md")
)


def get_current_git_branch(repo_path):
    """Gets the current Git branch name."""
    try:
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
    git_branch = get_current_git_branch(repo_path)
    state_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_task_description": task_desc,
        "last_completed_step_id": last_step,
        "next_step_id": next_step,
        "git_branch": git_branch,
        "relevant_knowledge_ids": knowledge_ids,
        "volatile_state": {},
    }
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
    except (IOError, TypeError) as e:
        logger.error(f"Error saving recovery manifest: {e}")
        return False


def update_dev_diary(update_content):
    """Appends content to the dev_diary.md file."""
    logger.info(f"Appending update to {DEV_DIARY_PATH}")
    try:
        os.makedirs(os.path.dirname(DEV_DIARY_PATH), exist_ok=True)
        with open(DEV_DIARY_PATH, "a") as f:
            if f.tell() > 0:
                f.write("\n")
            f.write(f"## {datetime.now(timezone.utc).isoformat()}\n")
            f.write(update_content)
            f.write("\n")
        logger.info("dev_diary.md updated successfully.")
        return True
    except IOError as e:
        logger.error(f"Error updating dev_diary.md: {e}")
        return False


def run_git_command(command, repo_path):
    """Runs a Git command using subprocess."""
    logger.info(f"Running git command: {" ".join(command)} in {repo_path}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_path
        )
        logger.info(f"Git command successful. Output:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"Git command stderr:\n{result.stderr}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        logger.error(f"Stderr:\n{e.stderr}")
        return False, e.stderr
    except FileNotFoundError as e:
        logger.error(f"Git command failed (git not found?): {e}")
        return False, str(e)


def persist_state_to_git(state_data, dev_diary_update, repo_path, commit_message, files_to_add=None):
    """Saves manifest, updates diary, and commits/pushes state to Git.

    Args:
        state_data (dict): The state data captured by capture_state.
        dev_diary_update (str): Content to append to dev_diary.md.
        repo_path (str): Absolute path to the git repository.
        commit_message (str): The commit message for this state save.
        files_to_add (list[str], optional): List of additional files/paths to add
                                           to the commit besides recovery.json
                                           and dev_diary.md. Defaults to ["utils/state_manager.py"].
    """
    logger.info("Persisting state to Git...")

    # 1. Save recovery manifest
    if not save_recovery_manifest(state_data):
        logger.error("Failed to save recovery manifest. Aborting persistence.")
        return False

    # 2. Update dev diary
    if not update_dev_diary(dev_diary_update):
        logger.warning("Failed to update dev_diary.md, but proceeding with commit.")

    # 3. Git Add
    if files_to_add is None:
        files_to_add = [os.path.abspath(__file__)] # Default to add this module file

    paths_to_add = [RECOVERY_FILE_PATH, DEV_DIARY_PATH] + files_to_add
    relative_paths_to_add = []
    for p in paths_to_add:
        try:
            # Ensure the path exists before trying to add
            if os.path.exists(p):
                relative_paths_to_add.append(os.path.relpath(p, repo_path))
            else:
                logger.warning(f"Path not found, skipping git add: {p}")
        except ValueError:
             # Handle cases where path might be on a different drive (less likely in sandbox)
             logger.warning(f"Could not get relative path for {p}, adding absolute path.")
             relative_paths_to_add.append(p)

    if not relative_paths_to_add:
        logger.warning("No valid files found to add to Git.")
        # Decide if this is an error or just nothing to do
        return True # Treat as success if nothing to add

    add_command = ["git", "add"] + relative_paths_to_add
    success, _ = run_git_command(add_command, repo_path)
    if not success:
        logger.error("Git add failed. Aborting persistence.")
        return False

    # 4. Git Commit
    commit_command = ["git", "commit", "-m", commit_message]
    success, output = run_git_command(commit_command, repo_path)
    if not success:
        if "nothing to commit" in output or "no changes added to commit" in output:
             logger.info("No changes to commit.")
             return True # Success, state is already persisted
        else:
            logger.error("Git commit failed. Aborting persistence.")
            return False

    # 5. Git Push
    branch = state_data.get("git_branch", "main")
    push_command = ["git", "push", "origin", branch]
    success, _ = run_git_command(push_command, repo_path)
    if not success:
        logger.error("Git push failed.")
        return False # Treat push failure as critical

    logger.info("State persisted to Git successfully.")
    return True


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

def restore_state(repo_path):
    """Restores the agent's state based on the recovery manifest.

    Reads the recovery manifest after ensuring the repository is up-to-date.
    Handles Git branch checkout if specified in the manifest.
    Returns the loaded state data for the agent's core logic to apply.

    Args:
        repo_path (str): Absolute path to the git repository.

    Returns:
        dict or None: The loaded state data from recovery.json, or None if failed.
    """
    logger.info("Attempting to restore agent state...")

    # Ensure repo is up-to-date before reading manifest
    logger.info("Pulling latest changes from Git...")
    # Determine current branch to pull correctly
    current_branch_for_pull = get_current_git_branch(repo_path)
    if current_branch_for_pull == "unknown_branch":
        logger.error("Cannot determine current branch for git pull. Aborting restore.")
        return None

    pull_success, _ = run_git_command(["git", "pull", "origin", current_branch_for_pull], repo_path)
    if not pull_success:
        logger.error("Git pull failed. Restoration might use stale data or fail. Aborting restore.")
        # Policy: Halt if pull fails, as state might be critically outdated.
        return None

    # Read the manifest file *after* pulling
    state_data = read_recovery_manifest()

    if state_data:
        logger.info(f"Restoring state from manifest dated {state_data.get('timestamp')}")

        # Handle Git branch checkout if necessary
        current_branch_after_pull = get_current_git_branch(repo_path)
        target_branch = state_data.get('git_branch')

        if target_branch and current_branch_after_pull != target_branch:
            logger.info(f"Current branch '{current_branch_after_pull}' differs from target '{target_branch}'. Checking out target branch.")
            checkout_success, _ = run_git_command(["git", "checkout", target_branch], repo_path)
            if not checkout_success:
                logger.error(f"Failed to checkout branch {target_branch}. State might be inconsistent. Aborting restore.")
                # Policy: Halt if checkout fails.
                return None
            # Re-read manifest if branch changed, as it might be different on that branch
            logger.info(f"Re-reading recovery manifest after checking out branch {target_branch}.")
            state_data = read_recovery_manifest()
            if not state_data:
                logger.error(f"Failed to read recovery manifest after checking out {target_branch}. Aborting restore.")
                return None

        # Log the information that needs to be restored by the agent's core logic
        logger.info("State data loaded successfully. Agent core logic should apply the following:")
        logger.info(f"  - Task Description: {state_data.get('current_task_description')}")
        logger.info(f"  - Last Completed Step: {state_data.get('last_completed_step_id')}")
        logger.info(f"  - Next Step: {state_data.get('next_step_id')}")
        logger.info(f"  - Target Git Branch: {state_data.get('git_branch')}")
        logger.info(f"  - Relevant Knowledge IDs: {state_data.get('relevant_knowledge_ids')}")
        logger.info(f"  - Volatile State: {state_data.get('volatile_state')}")

        # NOTE: Actual application of this state (setting plan, loading knowledge) must be
        # handled by the agent's core control loop or initialization logic, as this
        # module does not have direct access to the agent's internal state mechanisms.

        logger.info("restore_state function finished. Returning loaded state data.")
        return state_data
    else:
        logger.info("No recovery data found or error reading manifest. Starting fresh.")
        return None


# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Testing state manager functions...")

    repo_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # --- Test Persistence --- (Run this part first) --- 
    # logger.info("--- Testing Persistence ---")
    # sim_task_persist = "Implement self-restoration layer - Persistence Test"
    # sim_last_step_persist = "019"
    # sim_next_step_persist = "020"
    # sim_knowledge_persist = ["user_56", "user_63", "user_59", "user_64"]
    # current_state_persist = capture_state(
    #     sim_task_persist, sim_last_step_persist, sim_next_step_persist, sim_knowledge_persist, repo_directory
    # )
    # diary_entry_persist = "Testing state persistence function."
    # commit_msg_persist = f"chore: save recovery state after step {sim_last_step_persist}"
    # files_persist = [os.path.abspath(__file__)]
    # persisted = persist_state_to_git(current_state_persist, diary_entry_persist, repo_directory, commit_msg_persist, files_to_add=files_persist)
    # if persisted:
    #     logger.info("Persistence test successful.")
    # else:
    #     logger.error("Persistence test failed.")

    # --- Test Restoration --- (Run this part after persistence) ---
    logger.info("--- Testing Restoration ---")
    logger.info("Attempting restoration test...")
    # No agent_context needed as function now returns data
    restored_state_info = restore_state(repo_directory)
    if restored_state_info:
        logger.info("Restoration test successful (data loaded).")
        # Verify some loaded data (conceptual)
        # assert restored_state_info.get('current_task_description') == sim_task_persist
    else:
        logger.error("Restoration test failed (data not loaded or process aborted).")


