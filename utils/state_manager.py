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
        # Ensure directory exists (though it should in the repo)
        os.makedirs(os.path.dirname(DEV_DIARY_PATH), exist_ok=True)
        with open(DEV_DIARY_PATH, "a") as f:
            # Add a newline before the content if the file is not empty
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
    logger.info(f"Running git command: {' '.join(command)} in {repo_path}")
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
        # Decide if this should be a hard failure

    # 3. Git Add
    if files_to_add is None:
        files_to_add = ["utils/state_manager.py"] # Default to add the module itself

    # Ensure relative paths for git add if repo_path is the cwd
    paths_to_add = [RECOVERY_FILE_PATH, DEV_DIARY_PATH] + files_to_add
    # Convert absolute paths to relative if necessary, or ensure git runs from repo root
    # Assuming run_git_command uses repo_path as cwd, relative paths from there are needed.
    relative_paths_to_add = [os.path.relpath(p, repo_path) for p in paths_to_add]

    add_command = ["git", "add"] + relative_paths_to_add
    success, _ = run_git_command(add_command, repo_path)
    if not success:
        logger.error("Git add failed. Aborting persistence.")
        return False

    # 4. Git Commit
    commit_command = ["git", "commit", "-m", commit_message]
    success, _ = run_git_command(commit_command, repo_path)
    if not success:
        # Check if commit failed because there are no changes
        if "nothing to commit, working tree clean" in _:
             logger.info("No changes to commit.")
             # If nothing changed, maybe push isn't needed either? Or maybe push anyway?
             # Let's assume for now if commit fails due to no changes, we skip push.
             return True # Consider this a success, state is already persisted
        else:
            logger.error("Git commit failed. Aborting persistence.")
            return False

    # 5. Git Push
    branch = state_data.get("git_branch", "main") # Use branch from state data
    push_command = ["git", "push", "origin", branch]
    success, _ = run_git_command(push_command, repo_path)
    if not success:
        logger.error("Git push failed.")
        # Depending on policy, this might be acceptable (e.g., offline work)
        # For now, log as error but don't return False unless required
        return False # Treat push failure as critical for this mechanism

    logger.info("State persisted to Git successfully.")
    return True


def read_recovery_manifest():
    """Reads and parses the recovery manifest file."""
    # ... (previous implementation) ...
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

def restore_state(agent_context, repo_path):
    """Restores the agent's state based on the recovery manifest.

    Args:
        agent_context: Placeholder for the agent's internal context/state object.
        repo_path (str): Absolute path to the git repository.
    """
    logger.info("Attempting to restore agent state...")

    # Ensure repo is up-to-date before reading manifest
    logger.info("Pulling latest changes from Git...")
    pull_success, _ = run_git_command(["git", "pull"], repo_path)
    if not pull_success:
        logger.error("Git pull failed. Restoration might use stale data.")
        # Decide on policy: halt or continue with potentially old data?
        # For now, continue but log error.

    state_data = read_recovery_manifest()
    if state_data:
        logger.info(f"Restoring state from manifest dated {state_data.get('timestamp')}")

        # Handle Git branch checkout if necessary
        current_branch = get_current_git_branch(repo_path)
        target_branch = state_data.get('git_branch')
        if target_branch and current_branch != target_branch:
            logger.info(f"Checking out Git branch: {target_branch}")
            checkout_success, _ = run_git_command(["git", "checkout", target_branch], repo_path)
            if not checkout_success:
                logger.error(f"Failed to checkout branch {target_branch}. State might be inconsistent.")
                # Decide on policy: halt or continue?

        # Placeholder: Implement logic to apply the state_data to the agent's context
        # Example (conceptual):
        # agent_context.set_current_task(state_data.get('current_task_description'))
        # agent_context.set_plan_steps(state_data.get('last_completed_step_id'), state_data.get('next_step_id'))
        # agent_context.load_knowledge(state_data.get('relevant_knowledge_ids'))
        # agent_context.restore_volatile_state(state_data.get('volatile_state'))
        logger.info("State restoration logic needs full implementation using agent context.")
        # TODO: Implement actual state restoration using agent_context object

        logger.info("Agent state restored (partially - implementation pending).")
        return state_data
    else:
        logger.info("No recovery data found or error reading manifest. Starting fresh.")
        return None


# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Testing state manager functions...")

    repo_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Simulate context for capture
    sim_task = "Implement self-restoration layer - Git Integration"
    sim_last_step = "018"
    sim_next_step = "019"
    sim_knowledge = ["user_56", "user_63", "user_59"]

    # Test capture
    current_state = capture_state(
        sim_task, sim_last_step, sim_next_step, sim_knowledge, repo_directory
    )

    # Test persistence
    diary_entry = "Implemented Git integration for state persistence."
    commit_msg = f"chore: save recovery state after step {sim_last_step}"
    # Add the state manager itself to the commit
    files = [os.path.abspath(__file__)]
    persisted = persist_state_to_git(current_state, diary_entry, repo_directory, commit_msg, files_to_add=files)

    if persisted:
        logger.info("Persistence test successful.")
        # Test read and restore (will require agent context implementation later)
        sim_agent_context = {}
        logger.info("Attempting restoration test...")
        restored_state_info = restore_state(sim_agent_context, repo_directory)
        if restored_state_info:
            logger.info("Restoration test successful (data loaded).")
        else:
            logger.error("Restoration test failed (data not loaded).")
    else:
        logger.error("Persistence test failed.")

