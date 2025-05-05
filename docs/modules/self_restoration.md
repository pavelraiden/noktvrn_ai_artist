# Self-Restoration Mechanism

**Module:** `utils/state_manager.py`

## 1. Purpose

The Self-Restoration Mechanism provides the AI Artist System agent with the ability to recover its working context, memory, and task state after disruptions such as session resets, chat migrations, or temporary sandbox loss. It ensures continuity by persisting critical state information to the project's Git repository and restoring it upon initialization.

## 2. Architecture

The architecture relies on Git as the primary persistence layer and source of truth. Key components include:

*   **State Capture Module (`capture_state`):** Gathers essential state information (current task, plan steps, Git branch, relevant knowledge IDs, timestamp).
*   **Persistence Mechanism (`persist_state_to_git`):**
    *   Saves the captured state to `recovery.json`.
    *   Appends progress updates to `dev_diary.md`.
    *   Commits `recovery.json`, `dev_diary.md`, and relevant code changes to the current Git branch.
    *   Pushes the commit to the remote GitHub repository.
*   **State Restoration Module (`trigger_automatic_restore`, `trigger_manual_restore`, `_restore_state_core`):**
    *   Pulls the latest changes from the Git repository.
    *   Reads the `recovery.json` manifest.
    *   Checks out the correct Git branch if specified in the manifest.
    *   Loads and returns the state data for the agent's core logic to apply.
*   **Recovery Manifest (`recovery.json`):** A JSON file in the repository root containing structured state information (timestamp, task description, step IDs, branch, knowledge IDs, minimal volatile state).
*   **Development Diary (`dev_diary.md`):** A markdown file tracking progress, decisions, and reflections, updated during state persistence.

## 3. Workflow

### 3.1. State Capture & Persistence

1.  **Trigger:** Automatically invoked after completing a significant task step or before potentially disruptive operations.
2.  **Gather State:** The `capture_state` function collects task details, plan progress, Git branch, and knowledge context.
3.  **Save Manifest:** The collected state is saved to `recovery.json` by `save_recovery_manifest`.
4.  **Update Diary:** A summary of the completed step and any reflections are appended to `dev_diary.md` by `update_dev_diary`.
5.  **Commit & Push:** The `persist_state_to_git` function stages `recovery.json`, `dev_diary.md`, and associated code changes, commits them atomically, and pushes the commit to GitHub.

### 3.2. State Restoration

1.  **Trigger:** Automatically during agent initialization (`trigger_automatic_restore`) or manually via a command (`trigger_manual_restore`).
2.  **Sync Repository:** Pulls the latest changes from the current Git branch using `git pull`.
3.  **Read Manifest:** Reads `recovery.json`.
4.  **Branch Checkout (if needed):** If the branch specified in `recovery.json` differs from the current branch, checks out the target branch and pulls again.
5.  **Load State:** Parses `recovery.json` (potentially re-reading after checkout) using `_restore_state_core`.
6.  **Apply State:** The agent's core logic (outside this module) uses the returned state data to set its current task, plan steps, load knowledge, etc.

## 4. Implementation Notes

*   **Dependencies:** Requires `git` to be installed and accessible in the environment's PATH. Uses Python's `json`, `os`, `logging`, `subprocess`, and `datetime` modules.
*   **Configuration:** Relies on the presence of `recovery.json` and `dev_diary.md` in the repository root. Assumes Git user identity is configured.
*   **Agent Integration:** The core agent logic needs to:
    *   Call `capture_state` and `persist_state_to_git` at appropriate points, providing necessary context (task description, step IDs, knowledge IDs, commit message, files to add).
    *   Call `trigger_automatic_restore` during initialization.
    *   Implement the logic to *apply* the state data returned by the restoration functions to its internal context (e.g., update planner, load knowledge).
    *   Optionally, handle a user command (e.g., `!restore`) to call `trigger_manual_restore`.
*   **Error Handling:** Includes basic error handling for file I/O and Git operations. Failures during critical steps (like Git push or pull) are logged and may abort the operation.
*   **Security:** Does not handle sensitive credentials directly. Assumes Git authentication (e.g., via HTTPS token in URL) is handled externally.

## 5. Usage Example (Conceptual)

```python
# In agent's core logic
import utils.state_manager as sm

REPO_PATH = "/path/to/ai_artist_system_clone"

def initialize_agent():
    restored_state = sm.trigger_automatic_restore(REPO_PATH)
    if restored_state:
        # Apply restored state to agent's internal context
        apply_restored_state(restored_state)
        print("Agent state restored.")
    else:
        print("Starting agent with fresh state.")

def complete_step(step_id, next_step_id, task_desc, knowledge_ids, changed_files):
    # ... perform step actions ...

    # Persist state after completing the step
    state_data = sm.capture_state(task_desc, step_id, next_step_id, knowledge_ids, REPO_PATH)
    diary_update = f"Completed step {step_id}. Moving to {next_step_id}."
    commit_msg = f"chore: save recovery state after step {step_id}"
    files_to_add = [sm.os.path.abspath(f) for f in changed_files] # Add changed files
    sm.persist_state_to_git(state_data, diary_update, REPO_PATH, commit_msg, files_to_add=files_to_add)

# Conceptual function to apply state
def apply_restored_state(state_data):
    # agent.current_task = state_data.get('current_task_description')
    # agent.planner.set_steps(state_data.get('last_completed_step_id'), state_data.get('next_step_id'))
    # agent.knowledge.load(state_data.get('relevant_knowledge_ids'))
    pass
```

