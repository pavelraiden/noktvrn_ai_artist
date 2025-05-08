# AI Artist Lifecycle Design

This document outlines the design for the modular artist lifecycle management system, including metrics, triggers, and thresholds for creation, evolution, and retirement/pausing.

## 1. Core Principles

- **Modularity:** Triggers and logic should be configurable and easily adaptable.
- **Data-Driven:** Decisions must be based on quantifiable performance metrics.
- **Self-Adaptation:** The system should support automatic adjustments based on performance (evolution).
- **Configurability:** Key thresholds and parameters should be externalized (e.g., in `.env` or a configuration file) for easier tuning.

## 2. Key Performance Indicators (KPIs) / Metrics

The following metrics will be tracked and used to inform lifecycle decisions. Data sources need to be confirmed and potentially enhanced (e.g., in `artist_db_service`).

- **Approval Rate:** Percentage of runs approved (manually or via autopilot) over a defined period (e.g., last 30 days or last 50 runs). `Source: artist_db_service (requires tracking run outcomes)`
- **Consecutive Rejections:** Number of immediately preceding runs that were rejected. `Source: artist_db_service (requires tracking run outcomes)`
- **Trend Score:** Score indicating alignment with current trends (if applicable to the artist's domain). `Source: trend_analysis_service`
- **Run Frequency / Activity:** Number of successful runs within a defined period (e.g., last 7 days). `Source: artist_db_service (requires tracking run timestamps)`
- **Inactivity Period:** Time elapsed since the last successful run. `Source: artist_db_service (requires tracking run timestamps)`
- **Error Rate:** Percentage of runs encountering critical errors over a defined period. `Source: error_analysis_service / artist_db_service (requires error logging per run)`
- **(Future) Engagement Metrics:** Placeholder for metrics like views, likes, shares if integrated with release platforms. `Source: External APIs / Release Chain Feedback`

## 3. Lifecycle States

- **Candidate:** Newly defined artist configuration, not yet active.
- **Active:** Artist is currently participating in generation runs.
- **Paused:** Artist is temporarily inactive (e.g., due to poor performance, manual intervention).
- **Retired:** Artist is permanently deactivated and will no longer participate in runs.
- **Evolving:** Artist is undergoing parameter adjustments based on performance.

## 4. Lifecycle Triggers & Thresholds

*(Note: Threshold values are examples and should be configurable)*

### 4.1. Artist Creation

- **Trigger:** Manual initiation via a dedicated script or interface.
- **Future Trigger (Optional):** Automatic creation triggered if the number of `Active` artists drops below a threshold OR a significantly high-potential new trend is identified.
- **Process:** Define initial parameters (style, domain, base prompts, LLM config). Assign `Candidate` status initially, requires manual activation or first successful run to become `Active`.

### 4.2. Artist Evolution

- **Trigger 1 (Positive Performance):**
    - `Approval Rate` > 85% over last 30 runs
    - `Trend Score` > 0.8 (if applicable)
    - **Action:** Mark for potential parameter refinement (e.g., explore slight variations in prompt structure, potentially try a more advanced LLM if available). Status changes to `Evolving` temporarily.
- **Trigger 2 (Poor Performance):**
    - `Approval Rate` < 40% over last 30 runs
    - `Consecutive Rejections` < 3 (to avoid immediate retirement)
    - **Action:** Initiate automated evolution. This could involve: analyzing failed prompts, adjusting prompt complexity, switching to a different (potentially more robust) LLM, adjusting style parameters. Status changes to `Evolving`.
- **Process:** The `ArtistLifecycleManager` triggers an evolution process (potentially involving an LLM to suggest modifications based on performance data). Changes are tested, and if successful, the artist returns to `Active` status with updated parameters. If evolution fails repeatedly, it might trigger a `Paused` state.

### 4.3. Artist Pausing

- **Trigger 1 (Performance Dip):**
    - `Approval Rate` < 20% over last 50 runs
    - `Error Rate` > 30% over last 50 runs
    - **Action:** Change status to `Paused`. Requires manual review or significant automated overhaul (evolution) before reactivation.
- **Trigger 2 (Inactivity):**
    - `Inactivity Period` > 45 days
    - **Action:** Change status to `Paused`. Can be reactivated manually.
- **Process:** Paused artists are excluded from regular batch runs. They might be candidates for later review, evolution, or eventual retirement.

### 4.4. Artist Retirement

- **Trigger 1 (Consecutive Failures):**
    - `Consecutive Rejections` >= 5
    - **Action:** Change status to `Retired`.
- **Trigger 2 (Prolonged Poor Performance / Stagnation):**
    - Artist in `Paused` state for > 90 days.
    - Failed evolution attempts > 3.
    - **Action:** Change status to `Retired`.
- **Process:** Retired artists are permanently deactivated. Their data might be archived but they won't be used for generation.

## 5. Implementation Notes

- **Configuration:** Thresholds (e.g., `RETIREMENT_CONSECUTIVE_REJECTIONS = 5`, `PAUSE_INACTIVITY_DAYS = 45`) should be loaded from `.env` or a dedicated config file.
- **Database Schema:** The `artists` table in `artists.db` needs to be updated to include:
    - `status` (Candidate, Active, Paused, Retired, Evolving)
    - `last_run_timestamp`
    - `creation_timestamp`
    - `consecutive_rejections` counter
    - Fields to store aggregated performance metrics (or link to a separate performance table).
- **Integration:** The `ArtistLifecycleManager` needs methods to be called by the `BatchRunner` (e.g., after each run to update stats) and potentially run periodically (e.g., daily) to check for inactivity or evaluate overall performance trends.

