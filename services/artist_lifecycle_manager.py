# /home/ubuntu/ai_artist_system_clone/services/artist_lifecycle_manager.py
"""
Service for managing the lifecycle of AI artists based on performance and other criteria.
"""

import logging
import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Ensure the project root is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --- Logging Setup ---# Moved logging setup here to ensure it's configured before any potential import errors are logged
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Import functions directly from artist_db_service
    from services.artist_db_service import (
        get_artist,
        update_artist,
        update_artist_status,
        get_all_artists,
        initialize_database,
        add_artist
        # Add get_artist_performance_summary if it exists and is needed, or implement calculation here
    )
    # TODO: Import LLM Orchestrator when needed for advanced evolution
    # from llm_orchestrator.orchestrator import LLMOrchestrator
    db_imports_successful = True
except ImportError as e:
    logger.error(f"Failed to import required DB functions from services.artist_db_service: {e}. Lifecycle manager will not function correctly.")
    db_imports_successful = False
    # Define dummy functions if import fails, to allow basic structure loading but prevent execution
    def get_artist(artist_id): logger.error("DB function get_artist not available."); return None
    def update_artist(artist_id, data): logger.error("DB function update_artist not available."); return False
    def update_artist_status(artist_id, status): logger.error("DB function update_artist_status not available."); return False
    def get_all_artists(status_filter=None): logger.error("DB function get_all_artists not available."); return []
    def initialize_database(): logger.error("DB function initialize_database not available."); pass
    def add_artist(artist_data): logger.error("DB function add_artist not available."); return None

# --- Configuration (Load from .env or config file ideally) ---
# Performance Evaluation
PERFORMANCE_EVALUATION_PERIOD_DAYS = int(os.getenv("PERFORMANCE_EVALUATION_PERIOD_DAYS", 30))
MIN_RUNS_FOR_EVALUATION = int(os.getenv("MIN_RUNS_FOR_EVALUATION", 10))
# Evolution Triggers
EVOLUTION_POOR_PERF_APPROVAL_RATE = float(os.getenv("EVOLUTION_POOR_PERF_APPROVAL_RATE", 0.40))
EVOLUTION_GOOD_PERF_APPROVAL_RATE = float(os.getenv("EVOLUTION_GOOD_PERF_APPROVAL_RATE", 0.85))
# Pausing Triggers
PAUSE_APPROVAL_RATE_THRESHOLD = float(os.getenv("PAUSE_APPROVAL_RATE_THRESHOLD", 0.20))
PAUSE_ERROR_RATE_THRESHOLD = float(os.getenv("PAUSE_ERROR_RATE_THRESHOLD", 0.30))
PAUSE_INACTIVITY_DAYS = int(os.getenv("PAUSE_INACTIVITY_DAYS", 45))
# Retirement Triggers
RETIREMENT_CONSECUTIVE_REJECTIONS = int(os.getenv("RETIREMENT_CONSECUTIVE_REJECTIONS", 5))
RETIREMENT_PAUSED_DAYS = int(os.getenv("RETIREMENT_PAUSED_DAYS", 90))
RETIREMENT_FAILED_EVOLUTIONS = int(os.getenv("RETIREMENT_FAILED_EVOLUTIONS", 3))

class ArtistLifecycleManager:
    def __init__(self):
        """Initializes the Artist Lifecycle Manager."""
        # No need to instantiate db_service, functions are imported directly
        # TODO: Initialize LLM Orchestrator if needed for advanced evolution
        # self.llm_orchestrator = LLMOrchestrator()
        if not db_imports_successful:
             logger.critical("ArtistLifecycleManager initialized WITHOUT database functions. Lifecycle checks will fail.")
        else:
             logger.info("Artist Lifecycle Manager initialized.")

    def _get_performance_summary(self, artist_id: str) -> Dict[str, Any]:
        """Retrieves and calculates performance summary for an artist."""
        if not db_imports_successful: return {"error": "Database functions not available"}

        artist_data = get_artist(artist_id)
        if not artist_data:
            return {"error": "Artist not found"}

        history = artist_data.get("performance_history", [])
        if not isinstance(history, list):
             logger.warning(f"Performance history for artist {artist_id} is not a list: {history}")
             history = []

        # Filter history for the evaluation period
        cutoff_date = datetime.utcnow() - timedelta(days=PERFORMANCE_EVALUATION_PERIOD_DAYS)
        recent_history = [run for run in history if datetime.fromisoformat(run["timestamp"]) >= cutoff_date]

        total_runs = len(recent_history)
        approved_runs = sum(1 for run in recent_history if run["status"] == "approved")
        rejected_runs = sum(1 for run in recent_history if run["status"] == "rejected")
        # TODO: Calculate error rate if error status is logged in history
        error_runs = sum(1 for run in recent_history if run["status"] == "error")

        approval_rate = approved_runs / total_runs if total_runs > 0 else 0
        error_rate = error_runs / total_runs if total_runs > 0 else 0

        # Calculate inactivity
        last_run_timestamp_str = artist_data.get("last_run_at")
        inactivity_days = None
        if last_run_timestamp_str:
            try:
                last_run_timestamp = datetime.fromisoformat(last_run_timestamp_str)
                inactivity_days = (datetime.utcnow() - last_run_timestamp).days
            except ValueError:
                logger.warning(f"Invalid last_run_at format for artist {artist_id}: {last_run_timestamp_str}")

        summary = {
            "total_runs": total_runs,
            "approved_runs": approved_runs,
            "rejected_runs": rejected_runs,
            "error_runs": error_runs,
            "approval_rate": approval_rate,
            "error_rate": error_rate,
            "consecutive_rejections": artist_data.get("consecutive_rejections", 0),
            "inactivity_days": inactivity_days,
            "current_status": artist_data.get("status", "Unknown")
        }
        return summary

    def evaluate_artist_lifecycle(self, artist_id: str) -> Optional[str]:
        """Evaluates an artist and triggers lifecycle actions (evolution, pausing, retirement)."""
        if not db_imports_successful: return None

        logger.info(f"Evaluating lifecycle for artist {artist_id}...")
        performance = self._get_performance_summary(artist_id)

        if "error" in performance:
            logger.error(f"Cannot evaluate artist {artist_id}: {performance['error']}")
            return None

        total_runs = performance["total_runs"]
        approval_rate = performance["approval_rate"]
        error_rate = performance["error_rate"]
        consecutive_rejections = performance["consecutive_rejections"]
        inactivity_days = performance["inactivity_days"]
        current_status = performance["current_status"]

        logger.info(f"Artist {artist_id} Performance Summary: Runs={total_runs}, ApprovalRate={approval_rate:.2f}, ErrorRate={error_rate:.2f}, ConsecRej={consecutive_rejections}, InactiveDays={inactivity_days}, Status={current_status}")

        # --- Lifecycle Decision Logic --- #

        # 0. Check for Retirement (Consecutive Rejections) - Moved to top, applies regardless of status (unless already Retired)
        if current_status != "Retired" and consecutive_rejections >= RETIREMENT_CONSECUTIVE_REJECTIONS:
            logger.warning(f"Artist {artist_id} met retirement threshold ({consecutive_rejections} consecutive rejections). Retiring.")
            update_artist_status(artist_id, "Retired")
            return "Retired"

        # 1. Handle non-active states first
        if current_status not in ["Active", "Evolving", "Candidate"]:
            # Check if paused artist should be retired due to prolonged pause
            if current_status == "Paused" and inactivity_days is not None and inactivity_days > RETIREMENT_PAUSED_DAYS:
                 logger.warning(f"Artist {artist_id} has been paused for {inactivity_days} days. Retiring.")
                 update_artist_status(artist_id, "Retired")
                 return "Retired"
            # If already Retired or Paused (but not long enough for retirement), skip further evaluation
            logger.info(f"Artist {artist_id} is in status \'{current_status}\'. Skipping active performance evaluation.")
            return current_status # No change

        # --- Evaluations for Active, Evolving, Candidate artists --- #

        # 2. Need sufficient data for performance-based decisions
        if total_runs < MIN_RUNS_FOR_EVALUATION:
            # Check for inactivity even with few runs
            if inactivity_days is not None and inactivity_days > PAUSE_INACTIVITY_DAYS:
                logger.warning(f"Artist {artist_id} has insufficient runs ({total_runs}) but is inactive for {inactivity_days} days. Pausing.")
                update_artist_status(artist_id, "Paused")
                return "Paused"
            logger.info(f"Artist {artist_id} has insufficient runs ({total_runs}) for full performance evaluation. Skipping performance checks.")
            # If Candidate with few runs, keep as Candidate. If Active/Evolving, keep as is.
            return current_status # No change yet

        # 3. Check for Pausing (Severe Poor Performance or Errors)
        if approval_rate < PAUSE_APPROVAL_RATE_THRESHOLD or error_rate > PAUSE_ERROR_RATE_THRESHOLD:
            logger.warning(f"Artist {artist_id} performance is critically low (Approval: {approval_rate:.2f}, Error: {error_rate:.2f}). Pausing.")
            update_artist_status(artist_id, "Paused")
            return "Paused"

        # 4. Check for Pausing (Inactivity)
        if inactivity_days is not None and inactivity_days > PAUSE_INACTIVITY_DAYS:
            logger.warning(f"Artist {artist_id} has been inactive for {inactivity_days} days. Pausing.")
            update_artist_status(artist_id, "Paused")
            return "Paused"

        # 5. Check for Evolution (Poor Performance, but not critical)
        if approval_rate < EVOLUTION_POOR_PERF_APPROVAL_RATE:
            logger.warning(f"Artist {artist_id} shows poor performance (Approval Rate: {approval_rate:.2f}). Triggering evolution.")
            evolved = self.trigger_evolution(artist_id, performance)
            # trigger_evolution sets status to Active if successful, Paused if failed
            # We return the status set by trigger_evolution implicitly via DB read next cycle, or just report Evolving attempt
            # For clarity, let's return the status set by the evolution function if possible, otherwise the current status
            # Re-fetch status after evolution attempt? Or rely on next cycle? Let's rely on next cycle for now.
            # The function returns True/False, not the new status. Let's report 'Evolving' conceptually.
            # If evolution was attempted, the status is likely 'Active' or 'Paused' now.
            # Let's return the *intended* outcome status based on `evolved` flag.
            return "Active" if evolved else "Paused" # Return status set by evolution attempt

        # 6. Check for Evolution (Good Performance - Refinement Opportunity)
        if approval_rate > EVOLUTION_GOOD_PERF_APPROVAL_RATE:
            logger.info(f"Artist {artist_id} shows good performance (Approval Rate: {approval_rate:.2f}). Potential for refinement.")
            # Placeholder: Log for now, could trigger a different type of evolution later
            # self.trigger_refinement_evolution(artist_id, performance)
            # If Candidate and good performance, promote to Active
            if current_status == "Candidate":
                logger.info(f"Promoting Candidate artist {artist_id} to Active based on good performance.")
                update_artist_status(artist_id, "Active")
                return "Active"
            return current_status # No status change for Active/Evolving high performers for now

        # 7. Artist is performing adequately
        logger.info(f"Artist {artist_id} performance is adequate.")
        # If Candidate and adequate performance, promote to Active
        if current_status == "Candidate":
             logger.info(f"Promoting Candidate artist {artist_id} to Active based on adequate performance.")
             update_artist_status(artist_id, "Active")
             return "Active"
        # If status was Evolving, set back to Active after successful evaluation period
        if current_status == "Evolving":
            update_artist_status(artist_id, "Active")
            return "Active"
        return current_status # Should already be Active

    def trigger_evolution(self, artist_id: str, performance_summary: Dict[str, Any]) -> bool:
        """Attempts to evolve an artist based on poor performance. Sets status to Active if successful, Paused if failed."""
        if not db_imports_successful: return False

        artist_data = get_artist(artist_id)
        if not artist_data:
            logger.error(f"Cannot evolve non-existent artist {artist_id}.")
            return False

        logger.info(f"Attempting evolution for artist {artist_id} due to poor performance.")
        # Set status to Evolving temporarily during the process? Or just attempt change?
        # Let's attempt change and set final status based on outcome.
        # update_artist_status(artist_id, "Evolving") # Maybe not needed if we set Active/Paused at end

        # --- Evolution Strategies --- #
        # Strategy 1: Adjust LLM Config (e.g., temperature)
        current_llm_config = artist_data.get("llm_config", {})
        if isinstance(current_llm_config, dict) and "temperature" in current_llm_config:
            original_temp = current_llm_config["temperature"]
            # Simple adjustment: slightly increase temp if low, decrease if high
            adjustment = random.uniform(-0.1, 0.1)
            new_temp = max(0.1, min(1.0, original_temp + adjustment))
            if abs(new_temp - original_temp) > 0.01: # Only update if changed significantly
                current_llm_config["temperature"] = round(new_temp, 2)
                logger.info(f"Evolution Strategy: Adjusting temperature for {artist_id} from {original_temp} to {new_temp}")
                # Update config and set status to Active (evolution attempt complete)
                success = update_artist(artist_id, {"llm_config": current_llm_config, "status": "Active"})
                if success:
                    logger.info(f"Evolution successful for {artist_id}. New temp: {new_temp}. Status set to Active.")
                    return True
                else:
                    logger.error(f"Failed to update artist {artist_id} during evolution.")
                    update_artist_status(artist_id, "Paused") # Pause if DB update fails
                    return False
            else:
                logger.info(f"Evolution for {artist_id}: Temperature adjustment resulted in negligible change. No update applied.")
                # Fall through to other strategies or failure

        # Strategy 2: Modify Style Notes (e.g., add/remove a keyword)
        # TODO: Implement style note modification strategy (requires more sophisticated logic or LLM call)
        logger.warning(f"Evolution for {artist_id}: Temperature adjustment not applicable or failed. No other strategies implemented yet.")

        # If no strategy applied or failed
        logger.warning(f"Evolution failed to apply changes for artist {artist_id}. Setting status to Paused.")
        update_artist_status(artist_id, "Paused")
        return False

    # Placeholder for a different type of evolution for high performers
    # def trigger_refinement_evolution(self, artist_id: str, performance_summary: Dict[str, Any]):
    #     logger.info(f"(Placeholder) Triggering refinement evolution for high-performing artist {artist_id}.")
    #     pass

    def run_lifecycle_check_all(self):
        """Runs the performance evaluation and lifecycle checks for all relevant artists."""
        if not db_imports_successful: return

        logger.info("Running lifecycle check for all relevant artists (Candidate, Active, Evolving, Paused)...")
        # Fetch artists that might need evaluation or state change
        relevant_artists = get_all_artists(status_filter=None) # Get all and filter locally for more complex logic
        evaluated_count = 0
        for artist in relevant_artists:
            artist_id = artist["artist_id"]
            # Evaluate regardless of current status, let evaluate_artist_lifecycle handle logic
            self.evaluate_artist_lifecycle(artist_id)
            evaluated_count += 1
            # Removed status check here, evaluate_artist_lifecycle handles skipping retired

        logger.info(f"Finished lifecycle check. Evaluated {evaluated_count} artists.")

# Example Usage (for testing)
if __name__ == "__main__":
    # Ensure logging is configured for test run
    logging.basicConfig(level=logging.DEBUG)

    if not db_imports_successful:
        logger.critical("Database functions failed to import. Cannot run tests.")
        sys.exit(1)

    # Ensure DB is initialized with new schema changes from artist_db_service
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Error ensuring database schema: {e}")
        sys.exit(1)

    manager = ArtistLifecycleManager()

    # --- Test Setup --- 
    # Create a test artist if needed
    test_artist_id = "test_evolve_artist_1"
    artist_data = get_artist(test_artist_id)
    if not artist_data:
        added_id = add_artist({
            "artist_id": test_artist_id,
            "name": "Evolve Test Artist",
            "genre": "evolution",
            "style_notes": "Needs evolution testing",
            "llm_config": {"model": "test-llm", "temperature": 0.5},
            "status": "Active", # Start as Active for testing
            "performance_history": [
                # Add dummy history to trigger evaluation (1 approved, 11 rejected -> low approval rate)
                {"run_id": "r1", "status": "approved", "timestamp": (datetime.utcnow() - timedelta(days=5)).isoformat()},
                {"run_id": "r2", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(days=4)).isoformat()},
                {"run_id": "r3", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat()},
                {"run_id": "r4", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat()},
                {"run_id": "r5", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()},
                {"run_id": "r6", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat()},
                {"run_id": "r7", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=11)).isoformat()},
                {"run_id": "r8", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=10)).isoformat()},
                {"run_id": "r9", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=9)).isoformat()},
                {"run_id": "r10", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=8)).isoformat()},
                {"run_id": "r11", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=7)).isoformat()},
                {"run_id": "r12", "status": "rejected", "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat()}
            ]
        })
        if added_id:
            logger.info(f"Created test artist {test_artist_id}")
            # Update consecutive rejections manually for test scenario (e.g., 4 rejections)
            update_artist(test_artist_id, {"consecutive_rejections": 4})
        else:
            logger.error(f"Failed to create test artist {test_artist_id}. Aborting test.")
            sys.exit(1)
    else:
        # Ensure artist is Active and has correct rejection count for test
        update_artist(test_artist_id, {"status": "Active", "consecutive_rejections": 4})
        logger.info(f"Ensured test artist {test_artist_id} is Active with 4 consecutive rejections.")

    # --- Run Evaluation (Should trigger Pause due to low approval rate < 0.20) ---
    logger.info(f"\n--- Evaluating artist {test_artist_id} (expect Pause) ---")
    eval_status_1 = manager.evaluate_artist_lifecycle(test_artist_id)
    logger.info(f"Evaluation 1 complete for {test_artist_id}. Final status reported: {eval_status_1}")
    artist_data_1 = get_artist(test_artist_id)
    db_status_1 = artist_data_1.get("status") if artist_data_1 else "Not Found"
    logger.info(f"DB status after Eval 1: {db_status_1}")
    if db_status_1 == "Paused":
        logger.info("TEST RESULT 1: Paused as expected due to low approval rate.")
    else:
        logger.error(f"TEST RESULT 1: FAILED - Expected Paused, got {db_status_1}")

    # --- Test Retirement by Consecutive Rejections (while Paused) ---
    logger.info(f"\n--- Testing Retirement for {test_artist_id} (while Paused) ---")
    # Update artist to have enough rejections (ensure status is still Paused)
    update_artist(test_artist_id, {"status": "Paused", "consecutive_rejections": RETIREMENT_CONSECUTIVE_REJECTIONS})
    logger.info(f"Set consecutive rejections to {RETIREMENT_CONSECUTIVE_REJECTIONS} for Paused artist {test_artist_id}.")
    eval_status_2 = manager.evaluate_artist_lifecycle(test_artist_id)
    logger.info(f"Retirement evaluation complete for {test_artist_id}. Final status reported: {eval_status_2}")
    artist_data_2 = get_artist(test_artist_id)
    db_status_2 = artist_data_2.get("status") if artist_data_2 else "Not Found"
    logger.info(f"DB status after Retirement check: {db_status_2}")
    if db_status_2 == "Retired":
        logger.info("TEST RESULT 2: Retirement occurred as expected.")
    else:
        logger.error(f"TEST RESULT 2: FAILED - Expected Retired, got {db_status_2}")

    # Example: Evaluate all artists (optional)
    # logger.info("\n--- Evaluating all artists ---")
    # manager.run_lifecycle_check_all()

