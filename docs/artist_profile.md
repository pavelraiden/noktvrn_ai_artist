# AI Artist Profile Structure and Lifecycle

This document details the data structure for an AI artist profile within the system and explains the different lifecycle states an artist can be in.

## Artist Profile Structure

Each AI artist is represented by a data structure (typically stored in the database, e.g., in the `artists` table managed by `services/artist_db_service.py`) containing the following key fields:

*   **`artist_id` (str):** A unique identifier for the artist (e.g., `surreal_dreamer_01`).
*   **`name` (str):** A human-readable name for the artist (e.g., "Surreal Dreamer").
*   **`genre` (str):** The primary musical genre the artist operates in (e.g., "ambient", "lofi", "electronic").
*   **`style_notes` (str):** Textual descriptions defining the artist's unique style, influences, and target aesthetic. Used to guide content generation.
*   **`llm_config` (dict):** Configuration parameters for the Language Model (LLM) used during content generation or evolution. This might include:
    *   `model` (str): Identifier for the specific LLM to use.
    *   `temperature` (float): Controls the creativity/randomness of the LLM output. This is a key parameter adjusted during evolution.
    *   Other model-specific parameters.
*   **`status` (str):** The current lifecycle state of the artist. See "Lifecycle States" below.
*   **`performance_history` (list):** A list of records detailing past generation runs. Each record typically includes:
    *   `run_id` (str): Unique ID for the generation run.
    *   `timestamp` (str): ISO 8601 timestamp of the run completion.
    *   `status` (str): Outcome of the run (e.g., "approved", "rejected", "error").
    *   Other relevant metrics (e.g., prompts used, generated asset IDs).
*   **`last_run_at` (str, Optional):** ISO 8601 timestamp of the last time the artist attempted a generation run. Used for inactivity calculations.
*   **`consecutive_rejections` (int):** A counter tracking the number of immediately preceding rejected runs. Reset upon an approved run. Used for retirement checks.
*   **`created_at` (str):** ISO 8601 timestamp when the artist profile was first created.
*   **`updated_at` (str):** ISO 8601 timestamp when the artist profile was last modified.

## Lifecycle States and Transitions

The `status` field indicates the artist's current stage in its lifecycle, managed by `services/artist_lifecycle_manager.py`. The states and transitions are as follows:

1.  **`Candidate`:**
    *   **Description:** A newly created artist that has not yet produced enough content to be fully evaluated or promoted.
    *   **Transitions To:**
        *   `Active`: If performance (based on `MIN_RUNS_FOR_EVALUATION`) is adequate or good (`>= EVOLUTION_POOR_PERF_APPROVAL_RATE`).
        *   `Paused`: If inactive for `PAUSE_INACTIVITY_DAYS` even with insufficient runs.
        *   `Retired`: If `RETIREMENT_CONSECUTIVE_REJECTIONS` threshold is met.

2.  **`Active`:**
    *   **Description:** An established artist performing adequately and actively generating content.
    *   **Transitions To:**
        *   `Evolving`: If performance drops below `EVOLUTION_POOR_PERF_APPROVAL_RATE` (but above `PAUSE_APPROVAL_RATE_THRESHOLD`).
        *   `Paused`: If performance drops below `PAUSE_APPROVAL_RATE_THRESHOLD`, error rate exceeds `PAUSE_ERROR_RATE_THRESHOLD`, or inactive for `PAUSE_INACTIVITY_DAYS`.
        *   `Retired`: If `RETIREMENT_CONSECUTIVE_REJECTIONS` threshold is met.

3.  **`Evolving`:**
    *   **Description:** An artist undergoing automated adjustments (e.g., LLM config changes) due to poor performance. The `trigger_evolution` function attempts modifications.
    *   **Transitions To:**
        *   `Active`: If the evolution attempt (e.g., temperature adjustment) is successfully applied via `update_artist`.
        *   `Paused`: If the evolution attempt fails (e.g., no strategy applicable, DB update fails).
        *   `Retired`: If `RETIREMENT_CONSECUTIVE_REJECTIONS` threshold is met (checked before other evaluations).
    *   **Note:** The `evaluate_artist_lifecycle` function might also transition an artist *out* of `Evolving` back to `Active` if a subsequent evaluation shows adequate performance, although the primary transition happens within `trigger_evolution`.

4.  **`Paused`:**
    *   **Description:** An artist temporarily deactivated due to critical performance issues, high error rates, prolonged inactivity, or failed evolution attempts.
    *   **Transitions To:**
        *   `Retired`: If inactive (paused) for longer than `RETIREMENT_PAUSED_DAYS` OR if `RETIREMENT_CONSECUTIVE_REJECTIONS` threshold is met.
    *   **Note:** Currently, there is no automated transition *out* of `Paused` back to `Active`. This would likely require manual review or a specific reactivation trigger.

5.  **`Retired`:**
    *   **Description:** An artist permanently deactivated due to persistent poor performance (consecutive rejections) or prolonged inactivity while paused.
    *   **Transitions To:** None. This is a terminal state.

**Important Note on Validation:** As documented in the `dev_diary.md` (entry 2025-05-03), the validation of the lifecycle logic is currently **deferred**. A persistent syntax error in `services/artist_lifecycle_manager.py` prevents the test suite from running correctly. This error requires manual correction by the user after the code is pushed to the repository. The described transitions reflect the intended logic, but full confirmation awaits successful validation.
