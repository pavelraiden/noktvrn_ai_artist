## Self-Restoration Layer

The Self-Restoration Layer is a critical component of the AI Artist system, designed to ensure operational continuity and data integrity in the event of unexpected failures or interruptions. This document provides an overview of its architecture, functionality, and usage.

### Purpose

The primary purpose of the Self-Restoration Layer is to:

1.  **Prevent Data Loss:** Capture and persist the system's state at critical junctures, allowing for recovery to a known good state.
2.  **Minimize Downtime:** Automate the recovery process as much as possible, reducing the time required to restore functionality.
3.  **Enhance Reliability:** Provide a robust fallback mechanism when primary systems encounter issues, ensuring a consistent user experience.

### Architecture

The Self-Restoration Layer is comprised of several key components:

*   **State Capture Module:** Responsible for capturing and persisting the system's current operational state. This includes critical variables, active processes, queue states, and relevant configuration settings. The state is saved to a `recovery.json` file.
*   **Recovery Manager Module:** Handles the actual restoration process. It reads the `recovery.json` file and uses the stored state information to bring the system back to a functional point. This may involve re-initializing modules, reloading configurations, and restarting specific services.
*   **Triggers (Automated and Manual):**
    *   **Automated Triggers:** The system can be configured to automatically initiate state capture at regular intervals or before/after critical operations.
    *   **Manual Triggers:** Administrators can manually trigger state capture or initiate a recovery process via CLI commands.
*   **Git Persistence:** The `recovery.json` file is committed and pushed to the Git repository, ensuring that recovery states are versioned and backed up. This allows for rollback to specific historical states if needed.
*   **Simulation Tests:** Dedicated tests are implemented to simulate session wipes and validate the restoration process, ensuring the layer functions as expected.

### Workflow

1.  **State Capture:** 
    *   Triggered automatically (e.g., scheduled, pre-critical-operation) or manually by an administrator.
    *   The State Capture Module gathers all necessary state information.
    *   The state is serialized and saved to the `config/recovery.json` file.
    *   The updated `recovery.json` is committed and pushed to the Git repository.
2.  **Failure Detection / Manual Intervention:**
    *   An unrecoverable error occurs, or an administrator decides to roll back to a previous state.
3.  **Recovery Initiation:**
    *   Triggered automatically upon certain critical failures (if configured) or manually by an administrator via a CLI command (e.g., `python manage.py recover_state --version <commit_hash_or_tag>`).
    *   The Recovery Manager fetches the specified (or latest) `recovery.json` from the Git repository.
4.  **State Restoration:** 
    *   The Recovery Manager parses `recovery.json`.
    *   It then systematically restores the system's components based on the saved state (e.g., re-initializing services, reloading data, setting configurations).
5.  **Verification:** 
    *   After restoration, the system performs self-checks and logs the outcome.
    *   Administrators are notified of the recovery attempt and its success or failure.

### Implementation Notes

*   **`recovery_manager.py`:** Contains the core logic for initiating and managing the recovery process. It includes functions to fetch `recovery.json` from Git, parse it, and orchestrate the restoration of different system modules.
*   **`state_capture.py`:** Implements the functionality to gather and serialize the system state. It defines what data points are critical for recovery.
*   **`config/recovery.json`:** A JSON file storing the captured state. Its structure must be well-defined and versioned if necessary. Example structure:
    ```json
    {
      "timestamp": "2025-05-08T15:00:00Z",
      "version": "1.0.0",
      "commit_hash": "abcdef1234567890",
      "system_status": {
        "active_services": ["llm_orchestrator", "suno_service"],
        "queue_lengths": {
          "image_generation": 0,
          "text_processing": 5
        }
      },
      "module_states": {
        "llm_orchestrator": { "current_model": "gpt-4", "fallback_active": false },
        "suno_service": { "api_key_valid": true }
      }
    }
    ```
*   **Git Integration:** Uses standard Git commands (executed via Python's `subprocess` module or a Git library) to pull the `recovery.json` and to commit/push updates to it.
*   **Security:** Ensure that `recovery.json` does not store sensitive credentials directly. If needed, it should store references to securely managed secrets.

### Usage (CLI Examples)

*   **Capture current state:** `python manage.py capture_state --message "Pre-deployment state capture"`
*   **Recover to latest state:** `python manage.py recover_state`
*   **Recover to a specific state (by commit hash):** `python manage.py recover_state --commit abcdef123`

### Limitations

*   The effectiveness of the recovery depends on the completeness and accuracy of the state captured in `recovery.json`.
*   Data loss can still occur for changes made between the last state capture and the point of failure (RPO).
*   The time to recover (RTO) depends on the complexity of the state and the restoration procedures.

### Future Enhancements

*   More granular state capture for individual modules.
*   Differential state capture to reduce the size of `recovery.json`.
*   Integration with external monitoring systems for automated failure detection and recovery initiation.
