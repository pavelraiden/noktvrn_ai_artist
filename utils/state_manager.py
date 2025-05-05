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
    """Gathers critical state information from the agent's context."""
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
    cmd_str = " ".join(command)
    logger.info(f"Running git command: {cmd_str} in {repo_path}")
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
    """Saves manifest, updates diary, and commits/pushes state to Git."""
    logger.info("Persisting state to Git...")
    if not save_recovery_manifest(state_data):
        logger.error("Failed to save recovery manifest. Aborting persistence.")
        return False
    if not update_dev_diary(dev_diary_update):
        logger.warning("Failed to update dev_diary.md, but proceeding with commit.")
    if files_to_add is None:
        files_to_add = [os.path.abspath(__file__)]
    paths_to_add = [RECOVERY_FILE_PATH, DEV_DIARY_PATH] + files_to_add
    relative_paths_to_add = []
    for p in paths_to_add:
        try:
            if os.path.exists(p):
                # Ensure path is within the repo before getting relative path
                if p.startswith(repo_path):
                    relative_paths_to_add.append(os.path.relpath(p, repo_path))
                else:
                    logger.warning(f"Path {p} is outside repo {repo_path}, skipping git add.")
            else:
                logger.warning(f"Path not found, skipping git add: {p}")
        except ValueError:
             logger.warning(f"Could not get relative path for {p}, adding absolute path.")
             relative_paths_to_add.append(p)
    if not relative_paths_to_add:
        logger.warning("No valid files found to add to Git.")
        return True
    add_command = ["git", "add"] + relative_paths_to_add
    success, _ = run_git_command(add_command, repo_path)
    if not success:
        logger.error("Git add failed. Aborting persistence.")
        return False
    commit_command = ["git", "commit", "-m", commit_message]
    success, output = run_git_command(commit_command, repo_path)
    if not success:
        if "nothing to commit" in output or "no changes added to commit" in output:
             logger.info("No changes to commit.")
             return True
        else:
            logger.error("Git commit failed. Aborting persistence.")
            return False
    branch = state_data.get("git_branch", "main")
    push_command = ["git", "push", "origin", branch]
    success, _ = run_git_command(push_command, repo_path)
    if not success:
        logger.error("Git push failed.")
        return False
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


def _restore_state_core(repo_path):
    """Core logic for restoring state after pulling/checking out branch."""
    state_data = read_recovery_manifest()
    if state_data:
        logger.info(f"Restoring state from manifest dated {state_data.get('timestamp')}")
        logger.info("State data loaded successfully. Agent core logic should apply the following:")
        logger.info(f"  - Task Description: {state_data.get('current_task_description')}")
        logger.info(f"  - Last Completed Step: {state_data.get('last_completed_step_id')}")
        logger.info(f"  - Next Step: {state_data.get('next_step_id')}")
        logger.info(f"  - Target Git Branch: {state_data.get('git_branch')}")
        logger.info(f"  - Relevant Knowledge IDs: {state_data.get('relevant_knowledge_ids')}")
        logger.info(f"  - Volatile State: {state_data.get('volatile_state')}")
        logger.info("restore_state function finished. Returning loaded state data.")
        return state_data
    else:
        logger.info("No recovery data found or error reading manifest after potential branch checkout. Starting fresh.")
        return None


def trigger_automatic_restore(repo_path):
    """Performs automatic state restoration on agent startup."""
    logger.info("Triggering automatic state restoration...")
    initial_branch = get_current_git_branch(repo_path)
    if initial_branch == "unknown_branch":
        logger.error("Cannot determine current branch for git pull. Aborting restore.")
        return None
    logger.info(f"Pulling latest changes for branch '{initial_branch}'...")
    pull_success, _ = run_git_command(["git", "pull", "origin", initial_branch], repo_path)
    if not pull_success:
        logger.error("Git pull failed. Restoration might use stale data or fail. Aborting restore.")
        return None
    state_data_pre_checkout = read_recovery_manifest()
    if not state_data_pre_checkout:
        logger.info("No recovery manifest found on current branch after pull. Starting fresh.")
        return None
    target_branch = state_data_pre_checkout.get('git_branch')
    if target_branch and initial_branch != target_branch:
        logger.info(f"Manifest indicates target branch is '{target_branch}'. Checking out...")
        checkout_success, _ = run_git_command(["git", "checkout", target_branch], repo_path)
        if not checkout_success:
            logger.error(f"Failed to checkout branch {target_branch}. State might be inconsistent. Aborting restore.")
            return None
        logger.info(f"Pulling latest changes for newly checked out branch '{target_branch}'...")
        pull_success_new_branch, _ = run_git_command(["git", "pull", "origin", target_branch], repo_path)
        if not pull_success_new_branch:
             logger.error(f"Git pull failed on branch {target_branch}. Restoration might use stale data or fail. Aborting restore.")
             return None
        return _restore_state_core(repo_path)
    else:
        logger.info(f"Already on target branch '{initial_branch}' or no specific branch in manifest.")
        return _restore_state_core(repo_path)


def trigger_manual_restore(repo_path):
    """Performs state restoration when manually triggered (e.g., by !restore command)."""
    logger.info("Triggering manual state restoration...")
    return trigger_automatic_restore(repo_path)


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Setup logging to capture output
    log_file = "/home/ubuntu/state_manager_test.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() # Also print to console
        ]
    )
    logger.info("Starting state manager validation test...")

    repo_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # --- Test Persistence --- 
    logger.info("--- Testing Persistence ---")
    sim_task_persist = "Implement self-restoration layer - Validation Test"
    sim_last_step_persist = "021" # Step completed before validation
    sim_next_step_persist = "022" # Current step is validation
    sim_knowledge_persist = ["user_56", "user_63", "user_59", "user_62"]
    current_state_persist = capture_state(
        sim_task_persist, sim_last_step_persist, sim_next_step_persist, sim_knowledge_persist, repo_directory
    )
    diary_entry_persist = f"Validation Step {sim_next_step_persist}: Persisting state before attempting restoration."
    commit_msg_persist = f"chore: save recovery state before validation step {sim_next_step_persist}"
    # Ensure the state manager itself is included in the commit
    files_persist = [os.path.abspath(__file__)]
    persisted = persist_state_to_git(current_state_persist, diary_entry_persist, repo_directory, commit_msg_persist, files_to_add=files_persist)
    
    if not persisted:
        logger.error("Persistence failed. Cannot proceed with restoration test.")
    else:
        logger.info("Persistence test successful. Proceeding to restoration test.")
        
        # --- Test Restoration Trigger --- 
        logger.info("--- Testing Restoration Trigger ---")
        logger.info("Attempting automatic restoration trigger...")
        # Simulate restoration in a 'new session' by calling the trigger
        restored_state_info = trigger_automatic_restore(repo_directory)
        
        if restored_state_info:
            logger.info("Automatic restoration trigger test successful (data loaded).")
            # Basic verification
            if (restored_state_info.get('current_task_description') == sim_task_persist and
                restored_state_info.get('last_completed_step_id') == sim_last_step_persist and
                restored_state_info.get('next_step_id') == sim_next_step_persist and
                restored_state_info.get('git_branch') == 'feature/self-restoration'): # Assuming we are on this branch
                logger.info("VERIFICATION PASSED: Restored state data matches persisted data.")
            else:
                logger.error("VERIFICATION FAILED: Restored state data does NOT match persisted data.")
                logger.error(f"Expected Task: {sim_task_persist}, Got: {restored_state_info.get('current_task_description')}")
                logger.error(f"Expected Last Step: {sim_last_step_persist}, Got: {restored_state_info.get('last_completed_step_id')}")
                logger.error(f"Expected Next Step: {sim_next_step_persist}, Got: {restored_state_info.get('next_step_id')}")
                logger.error(f"Expected Branch: feature/self-restoration, Got: {restored_state_info.get('git_branch')}")
        else:
            logger.error("Automatic restoration trigger test failed (data not loaded or process aborted).")

    logger.info("State manager validation test finished. Check log file: %s", log_file)

