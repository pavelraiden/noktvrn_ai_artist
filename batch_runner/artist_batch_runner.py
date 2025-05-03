#!/usr/bin/env python3

import logging
import os
import sys
import time
import uuid
import json
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Load Environment Variables ---
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=DOTENV_PATH)
PROJECT_ROOT_DOTENV = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(PROJECT_ROOT_DOTENV):
    load_dotenv(dotenv_path=PROJECT_ROOT_DOTENV, override=False)

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
STREAMLIT_APP_PATH = os.path.join(PROJECT_ROOT, "streamlit_app")
sys.path.append(STREAMLIT_APP_PATH)

# --- Import existing modules ---
try:
    from services.telegram_service import send_preview_to_telegram
    from release_chain.release_chain import process_approved_run
    from llm_orchestrator.orchestrator import LLMOrchestrator, LLMOrchestratorError
    from services.artist_db_service import (
        add_artist,
        get_artist,
        get_all_artists,
        update_artist,
        update_artist_performance_db,
        initialize_database as initialize_artist_db
    )
    # Import the lifecycle manager
    from services.artist_lifecycle_manager import ArtistLifecycleManager
    # from services.trend_analysis_service import TrendAnalysisService
except ImportError as e:
    logging.error(f"Failed to import core modules, release_chain, orchestrator, or services: {e}. Exiting.")
    sys.exit(1)

# --- Configuration ---
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "batch_runner.log")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RUN_STATUS_DIR = os.path.join(OUTPUT_DIR, "run_status")
MAX_APPROVAL_WAIT_TIME = int(os.getenv("MAX_APPROVAL_WAIT_TIME", 300))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
REFLECTION_LLM_PRIMARY = os.getenv("REFLECTION_LLM_PRIMARY", "deepseek:deepseek-chat")
REFLECTION_LLM_FALLBACKS = os.getenv("REFLECTION_LLM_FALLBACKS", "gemini:gemini-pro").split(",")
REFLECTION_MAX_TOKENS = int(os.getenv("REFLECTION_MAX_TOKENS", 500))
REFLECTION_TEMPERATURE = float(os.getenv("REFLECTION_TEMPERATURE", 0.6))
# ARTIST_RETIREMENT_THRESHOLD is now primarily handled by lifecycle manager config, but keep for performance update function
ARTIST_RETIREMENT_THRESHOLD = int(os.getenv("RETIREMENT_CONSECUTIVE_REJECTIONS", 5))
ARTIST_CREATION_PROBABILITY = float(os.getenv("ARTIST_CREATION_PROBABILITY", 0.05)) # Reduced probability slightly
LIFECYCLE_CHECK_INTERVAL_MINUTES = int(os.getenv("LIFECYCLE_CHECK_INTERVAL_MINUTES", 60 * 6)) # Check every 6 hours

# --- A/B Testing Configuration ---
AB_TESTING_ENABLED = os.getenv("AB_TESTING_ENABLED", "False").lower() == "true"
AB_TEST_VARIATIONS = {
    "suno_prompt_prefix": [
        "A dreamy {genre} track", # Control (Variation A)
        "An experimental {genre} piece", # Variation B
        "A high-energy {genre} anthem" # Variation C
    ]
}
AB_TEST_PARAMETER = "suno_prompt_prefix"

# Ensure directories exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RUN_STATUS_DIR, exist_ok=True)

# --- Logging Setup ---
log_level_mapping = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
effective_log_level = log_level_mapping.get(LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=effective_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

logger.info(f"Log level set to: {LOG_LEVEL}")
logger.info(f"Max approval wait time: {MAX_APPROVAL_WAIT_TIME}s")
logger.info(f"Approval poll interval: {POLL_INTERVAL}s")
logger.info(f"Reflection LLM Primary: {REFLECTION_LLM_PRIMARY}")
logger.info(f"Reflection LLM Fallbacks: {REFLECTION_LLM_FALLBACKS}")
logger.info(f"Artist Retirement Threshold (Consecutive Rejections): {ARTIST_RETIREMENT_THRESHOLD}")
logger.info(f"Artist Creation Probability: {ARTIST_CREATION_PROBABILITY}")
logger.info(f"Lifecycle Check Interval: {LIFECYCLE_CHECK_INTERVAL_MINUTES} minutes")
logger.info(f"A/B Testing Enabled: {AB_TESTING_ENABLED}")
if AB_TESTING_ENABLED:
    logger.info(f"A/B Testing Parameter: {AB_TEST_PARAMETER}")
    logger.info(f"A/B Testing Variations: {AB_TEST_VARIATIONS.get(AB_TEST_PARAMETER)}")

# --- Initialize Artist Database ---
try:
    initialize_artist_db()
    if not get_all_artists():
        logger.info("Artist database is empty. Adding default artist.")
        default_artist_data = {
            "artist_id": "1",
            "name": "Synthwave Dreamer",
            "genre": "synthwave",
            "style_notes": "Prefers dreamy melodies, moderate tempo, avoids harsh sounds.",
            "llm_config": {"model": "default-llm", "temperature": 0.7},
            "created_at": datetime.utcnow().isoformat(),
            "status": "Active" # Start default as Active
        }
        add_artist(default_artist_data)
except Exception as e:
    logger.critical(f"Failed to initialize or populate artist database: {e}. Exiting.")
    sys.exit(1)

# --- Initialize LLM Orchestrator ---
try:
    llm_orchestrator = LLMOrchestrator(
        primary_model=REFLECTION_LLM_PRIMARY,
        fallback_models=REFLECTION_LLM_FALLBACKS,
        enable_auto_discovery=False
    )
except Exception as e:
    logger.error(f"Failed to initialize LLM Orchestrator: {e}. Reflection/Creation disabled.")
    llm_orchestrator = None

# --- Initialize Artist Lifecycle Manager ---
try:
    lifecycle_manager = ArtistLifecycleManager()
    last_lifecycle_check_time = datetime.min # Ensure check runs on first iteration
except Exception as e:
    logger.critical(f"Failed to initialize Artist Lifecycle Manager: {e}. Exiting.")
    sys.exit(1)

def create_new_artist_profile():
    """Uses LLM (placeholder for now) to generate a new artist profile and adds it to the DB with Candidate status."""
    logger.info("Attempting to create a new artist profile...")
    # TODO: Use LLM to generate more creative name, genre, style_notes, llm_config
    new_id = str(uuid.uuid4())
    new_artist_data = {
        "artist_id": new_id,
        "name": f"Generated Artist {new_id[:4]}",
        "genre": random.choice(["electronic", "ambient", "lofi", "hyperpop", "cinematic"]), # Example genres
        "style_notes": "Experimental, evolving style. Focus on atmospheric textures.",
        "llm_config": {"model": REFLECTION_LLM_PRIMARY, "temperature": round(random.uniform(0.5, 0.9), 2)},
        "created_at": datetime.utcnow().isoformat(),
        "status": "Candidate", # New artists start as Candidate
        "autopilot_enabled": False # New artists start with autopilot off
    }
    added_id = add_artist(new_artist_data)
    if added_id:
        logger.info(f"Created and added new artist profile to DB: ID={added_id}, Name=", {new_artist_data["name"]}, ")")
        return get_artist(added_id) # Return full data from DB
    else:
        logger.error(f"Failed to add newly created artist {new_id} to the database.")
        return None

def run_global_lifecycle_check_if_needed():
    """Runs the global lifecycle check if the interval has passed."""
    global last_lifecycle_check_time
    now = datetime.utcnow()
    if now - last_lifecycle_check_time >= timedelta(minutes=LIFECYCLE_CHECK_INTERVAL_MINUTES):
        logger.info("Running global artist lifecycle check...")
        try:
            lifecycle_manager.run_lifecycle_check_all()
            last_lifecycle_check_time = now
            logger.info("Global lifecycle check completed.")
        except Exception as e:
            logger.error(f"Error during global lifecycle check: {e}", exc_info=True)
    else:
        logger.debug("Skipping global lifecycle check (interval not reached).")

def select_next_artist():
    """Selects an active artist from DB, potentially creating a new one."""
    logger.info("Selecting next artist...")

    # Run global check first to update statuses (e.g., pause inactive)
    run_global_lifecycle_check_if_needed()

    active_artists = get_all_artists(status_filter="Active")

    # Decide whether to create a new artist
    create_new = random.random() < ARTIST_CREATION_PROBABILITY

    if create_new or not active_artists:
        logger.info("Triggering new artist creation...")
        new_artist = create_new_artist_profile()
        if new_artist:
            logger.info(f"Successfully created new artist {new_artist["artist_id"]}. Selecting it (will run as Candidate).")
            # New artists start as Candidate, they will run once and become Active if approved.
            return new_artist
        else:
            logger.warning("Failed to create a new artist. Proceeding with existing active pool.")
            # Re-fetch active artists in case creation failed but there are active ones
            active_artists = get_all_artists(status_filter="Active")
            if not active_artists:
                 logger.error("No active artists available and failed to create a new one. Cannot proceed.")
                 return None

    if not active_artists:
        logger.error("No active artists found in the database.")
        return None

    # Select from active artists based on least recent run
    sorted_artists = sorted(
        active_artists,
        key=lambda a: datetime.fromisoformat(a["last_run_at"]) if a["last_run_at"] else datetime.min
    )
    selected_artist = sorted_artists[0]
    logger.info(f"Selected active artist {selected_artist["artist_id"]} ({selected_artist["name"]}) based on least recent run.")
    return selected_artist

# --- Parameter Adaptation with A/B Testing (Unchanged) --- #
def get_adapted_parameters(artist_profile):
    """Gets generation parameters, applying A/B test variations if enabled."""
    genre = artist_profile.get("genre", "synthwave")
    style_notes = artist_profile.get("style_notes", "standard synthwave")
    ab_test_info = {"enabled": False, "parameter": None, "variation_index": None, "variation_value": None}

    base_suno_prompt = f"upbeat tempo, inspired by {style_notes}"
    base_params = {
        "suno_style": genre,
        "video_keywords": [genre, "retro", "neon", "dreamy"],
        "make_instrumental": False,
    }

    if AB_TESTING_ENABLED and AB_TEST_PARAMETER in AB_TEST_VARIATIONS:
        variations = AB_TEST_VARIATIONS[AB_TEST_PARAMETER]
        if variations:
            chosen_index = random.randrange(len(variations))
            chosen_variation = variations[chosen_index]
            ab_test_info["enabled"] = True
            ab_test_info["parameter"] = AB_TEST_PARAMETER
            ab_test_info["variation_index"] = chosen_index
            ab_test_info["variation_value"] = chosen_variation
            logger.info(f"A/B Test: Applying variation {chosen_index} (", {chosen_variation}, ") for parameter ", {AB_TEST_PARAMETER}, ")")

            if AB_TEST_PARAMETER == "suno_prompt_prefix":
                prompt_prefix = chosen_variation.format(genre=genre)
                base_params["suno_prompt"] = f"{prompt_prefix}, {base_suno_prompt}"
            else:
                 logger.warning(f"A/B test parameter ", {AB_TEST_PARAMETER}, " not handled. Using default.")
                 base_params["suno_prompt"] = f"A dreamy {genre} track, {base_suno_prompt}"
        else:
            logger.warning(f"A/B testing enabled but no variations defined for ", {AB_TEST_PARAMETER}, ". Using default.")
            base_params["suno_prompt"] = f"A dreamy {genre} track, {base_suno_prompt}"
    else:
        base_params["suno_prompt"] = f"A dreamy {genre} track, {base_suno_prompt}"

    base_params["ab_test_info"] = ab_test_info
    return base_params

# --- Placeholder Generation Functions (Unchanged) ---
def generate_track(suno_params):
    logger.info(f"Generating track with params: {suno_params} (placeholder)...")
    try:
        time.sleep(2)
        track_id = str(uuid.uuid4())
        track_url = f"http://fake-suno.com/track/{track_id}"
        logger.info(f"Generated track (placeholder): ID={track_id}, URL={track_url}")
        return {"track_id": track_id, "track_url": track_url}
    except Exception as e:
        logger.error(f"Error during placeholder track generation: {e}", exc_info=True)
        return None

def select_video(track_info, video_keywords):
    try:
        time.sleep(1)
        video_url = f"http://fake-pexels.com/video/{uuid.uuid4()}"
        logger.info(f"Selected video (placeholder): URL={video_url}")
        return {"video_url": video_url, "source": "pexels"}
    except Exception as e:
        logger.error(f"Error during placeholder video selection: {e}", exc_info=True)
        return None

# --- Auto-Reflection Function (Unchanged) --- #
async def generate_reflection(artist_profile, parameters, track_info, video_info):
    if not llm_orchestrator:
        logger.warning("LLM Orchestrator not initialized. Skipping reflection.")
        return None
    logger.info("Generating reflection for the created content...")
    try:
        prompt_params = {k: v for k, v in parameters.items() if k != "ab_test_info"}
        prompt = f"""
        Artist Profile:
        - Name: {artist_profile.get("name", "N/A")}
        - Genre: {artist_profile.get("genre", "N/A")}
        - Style Notes: {artist_profile.get("style_notes", "N/A")}
        Generation Parameters:
        - Suno Prompt: {prompt_params.get("suno_prompt", "N/A")}
        - Suno Style: {prompt_params.get("suno_style", "N/A")}
        - Video Keywords: {prompt_params.get("video_keywords", "N/A")}
        - Instrumental: {prompt_params.get("make_instrumental", "N/A")}
        Generated Content:
        - Track URL: {track_info.get("track_url", "N/A")}
        - Video URL: {video_info.get("video_url", "N/A")}
        Task: Reflect on the generated track and video.
        1. Assess alignment with artist profile.
        2. Evaluate quality and coherence.
        3. Suggest 1-2 specific improvements for the next run.
        4. Provide a brief overall assessment.
        Keep the reflection concise and actionable.
        """
        reflection_text = await llm_orchestrator.generate(
            prompt=prompt,
            max_tokens=REFLECTION_MAX_TOKENS,
            temperature=REFLECTION_TEMPERATURE
        )
        if reflection_text:
            logger.info("Reflection generated successfully.")
            logger.debug(f"Reflection Text: {reflection_text}")
            return reflection_text
        else:
            logger.warning("Reflection generation returned empty content.")
            return None
    except LLMOrchestratorError as e:
        logger.error(f"LLM Orchestrator error during reflection generation: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during reflection generation: {e}", exc_info=True)
        return None

# --- Telegram Integration & Status Handling (Updated) --- #

def update_run_status(run_id, new_status, reason=None, reflection=None, artist_id=None):
    """Updates the status file and triggers artist performance update in DB.
       The DB update handles immediate retirement based on consecutive rejections.
    """
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    try:
        run_data = {}
        if os.path.exists(status_filepath):
            try:
                with open(status_filepath, "r") as f:
                    run_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading/decoding status file {status_filepath}, will overwrite: {e}")
        else:
            logger.warning(f"Status file {status_filepath} not found, creating basic structure.")

        # Ensure basic info exists
        run_data["run_id"] = run_id
        if "created_at" not in run_data:
             run_data["created_at"] = datetime.utcnow().isoformat()
        if artist_id:
            run_data["artist_id"] = artist_id

        run_data["status"] = new_status
        run_data["updated_at"] = datetime.utcnow().isoformat()
        if reason:
            run_data["final_status_reason"] = reason
        if reflection:
             run_data["reflection"] = reflection
        if new_status in ["approved", "autopilot_approved", "rejected"] and "approved_at" not in run_data:
            run_data["approved_at"] = run_data["updated_at"]

        with open(status_filepath, "w") as f:
            json.dump(run_data, f, indent=4)
        logger.info(f"Updated status for run {run_id} to {new_status} in {status_filepath}")

        # --- Trigger DB Performance Update --- #
        # Use the actual artist_id associated with the run
        db_artist_id = run_data.get("artist_id")
        if db_artist_id and new_status in ["approved", "autopilot_approved", "rejected"]:
            # Map autopilot_approved to approved for DB performance tracking
            db_status = "approved" if new_status == "autopilot_approved" else new_status
            logger.info(f"Updating performance DB for artist {db_artist_id} with run {run_id} status: {db_status}")
            try:
                update_success = update_artist_performance_db(
                    artist_id=db_artist_id,
                    run_id=run_id,
                    status=db_status,
                    retirement_threshold=ARTIST_RETIREMENT_THRESHOLD
                )
                if not update_success:
                     logger.error(f"Failed to update performance in DB for artist {db_artist_id}, run {run_id}.")
                else:
                     logger.info(f"Performance DB updated for artist {db_artist_id}.")
                     # After successful DB update, trigger the broader lifecycle evaluation
                     logger.info(f"Triggering post-run lifecycle evaluation for artist {db_artist_id}...")
                     try:
                         lifecycle_manager.evaluate_artist_lifecycle(db_artist_id)
                     except Exception as eval_e:
                         logger.error(f"Error during post-run lifecycle evaluation for artist {db_artist_id}: {eval_e}", exc_info=True)

            except Exception as db_e:
                logger.error(f"Error updating performance DB for artist {db_artist_id}: {db_e}", exc_info=True)
        elif not db_artist_id:
             logger.warning(f"Cannot update performance DB: artist_id missing in run status file {status_filepath}")

    except Exception as e:
        logger.error(f"Failed to update run status for {run_id}: {e}", exc_info=True)

async def send_to_telegram_for_approval(run_id, artist_profile, track_info, video_info, parameters):
    """Sends content preview to Telegram and waits for approval/rejection."""
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    artist_id = artist_profile["artist_id"]
    artist_name = artist_profile.get("name", "Unknown Artist")
    ab_test_info = parameters.get("ab_test_info", {})

    # Initial status update
    update_run_status(run_id, "pending_approval", artist_id=artist_id)

    # Generate reflection before sending
    reflection = await generate_reflection(artist_profile, parameters, track_info, video_info)
    if reflection:
        update_run_status(run_id, "pending_approval", reflection=reflection, artist_id=artist_id)

    # Construct message
    message = f"**New Content Preview**\n\n"
    message += f"**Run ID:** `{run_id}`\n"
    message += f"**Artist:** {artist_name} (`{artist_id}`)\n"
    message += f"**Track:** {track_info["track_url"]}\n"
    message += f"**Video:** {video_info["video_url"]}\n\n"
    if ab_test_info.get("enabled"):
        message += f"**A/B Test:** Parameter=`{ab_test_info["parameter"]}`, Variation=`{ab_test_info["variation_index"]}` (`{ab_test_info["variation_value"]}`)\n\n"
    if reflection:
        message += f"**Reflection:**\n```\n{reflection[:800]}...```\n\n" # Truncate reflection for TG
    message += f"Please approve or reject within {MAX_APPROVAL_WAIT_TIME // 60} minutes."

    try:
        # Send preview
        await send_preview_to_telegram(run_id, message)
        logger.info(f"Preview for run {run_id} sent to Telegram. Waiting for approval...")

        # Wait for approval status change
        start_time = time.time()
        while time.time() - start_time < MAX_APPROVAL_WAIT_TIME:
            if os.path.exists(status_filepath):
                try:
                    with open(status_filepath, "r") as f:
                        current_data = json.load(f)
                    current_status = current_data.get("status")
                    if current_status in ["approved", "rejected"]:
                        logger.info(f"Received status 	{current_status}	 for run {run_id} via status file.")
                        # Update status again to ensure DB performance is logged if needed
                        update_run_status(run_id, current_status, reason=current_data.get("final_status_reason"), reflection=reflection, artist_id=artist_id)
                        return current_status
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading status file {status_filepath} while polling: {e}")
            await asyncio.sleep(POLL_INTERVAL)

        # Timeout
        logger.warning(f"Timeout waiting for approval for run {run_id}. Marking as rejected.")
        update_run_status(run_id, "rejected", reason="Timeout waiting for approval", reflection=reflection, artist_id=artist_id)
        return "rejected"

    except Exception as e:
        logger.error(f"Error in Telegram approval process for run {run_id}: {e}", exc_info=True)
        update_run_status(run_id, "rejected", reason=f"Error during approval process: {e}", reflection=reflection, artist_id=artist_id)
        return "rejected"

# --- Main Execution Logic --- #
async def run_artist_cycle():
    """Runs a single generation cycle for a selected artist."""
    run_id = str(uuid.uuid4())
    logger.info(f"\n--- Starting Artist Cycle: Run ID {run_id} ---")

    # 1. Select Artist
    artist_profile = select_next_artist()
    if not artist_profile:
        logger.error("Failed to select an artist. Skipping cycle.")
        return
    artist_id = artist_profile["artist_id"]
    artist_status = artist_profile.get("status", "Unknown")
    logger.info(f"Running cycle for artist: {artist_id} ({artist_profile.get("name")}), Status: {artist_status}")

    # Create initial status file
    initial_status_data = {
        "run_id": run_id,
        "artist_id": artist_id,
        "artist_name": artist_profile.get("name"),
        "status": "generating",
        "created_at": datetime.utcnow().isoformat()
    }
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    try:
        with open(status_filepath, "w") as f:
            json.dump(initial_status_data, f, indent=4)
    except IOError as e:
        logger.error(f"Failed to create initial status file {status_filepath}: {e}. Proceeding cautiously.")

    # 2. Adapt Parameters (including A/B test)
    parameters = get_adapted_parameters(artist_profile)
    logger.debug(f"Adapted parameters: {parameters}")
    # Update status file with parameters
    initial_status_data["parameters"] = parameters
    try:
        with open(status_filepath, "w") as f:
            json.dump(initial_status_data, f, indent=4)
    except IOError as e:
         logger.error(f"Failed to update status file {status_filepath} with parameters: {e}")

    # 3. Generate Content (Placeholders)
    track_info = generate_track(parameters)
    if not track_info:
        logger.error("Track generation failed. Aborting cycle.")
        update_run_status(run_id, "failed", reason="Track generation failed", artist_id=artist_id)
        return

    video_info = select_video(track_info, parameters["video_keywords"])
    if not video_info:
        logger.error("Video selection failed. Aborting cycle.")
        update_run_status(run_id, "failed", reason="Video selection failed", artist_id=artist_id)
        return

    logger.info("Content generation completed.")
    update_run_status(run_id, "generated", artist_id=artist_id)

    # 4. Approval Step (Manual via Telegram or Autopilot)
    autopilot = artist_profile.get("autopilot_enabled", False)
    final_status = "unknown"

    if autopilot:
        logger.info(f"Artist {artist_id} is on Autopilot. Auto-approving run {run_id}.")
        # Generate reflection even for autopilot
        reflection = await generate_reflection(artist_profile, parameters, track_info, video_info)
        update_run_status(run_id, "autopilot_approved", reason="Autopilot enabled", reflection=reflection, artist_id=artist_id)
        final_status = "autopilot_approved"
    else:
        logger.info(f"Sending run {run_id} for manual approval via Telegram...")
        final_status = await send_to_telegram_for_approval(run_id, artist_profile, track_info, video_info, parameters)

    # 5. Process Approved Run (Release Chain)
    if final_status in ["approved", "autopilot_approved"]:
        logger.info(f"Run {run_id} approved. Processing through release chain...")
        try:
            release_result = process_approved_run(run_id, artist_profile, track_info, video_info, parameters)
            if release_result:
                logger.info(f"Release chain processing successful for run {run_id}.")
                update_run_status(run_id, "released", artist_id=artist_id)
            else:
                logger.error(f"Release chain processing failed for run {run_id}.")
                update_run_status(run_id, "release_failed", reason="Release chain function returned failure", artist_id=artist_id)
        except Exception as e:
            logger.error(f"Error during release chain processing for run {run_id}: {e}", exc_info=True)
            update_run_status(run_id, "release_failed", reason=f"Exception in release chain: {e}", artist_id=artist_id)
    else:
        logger.info(f"Run {run_id} was not approved (status: {final_status}). Skipping release chain.")

    logger.info(f"--- Finished Artist Cycle: Run ID {run_id} --- Final Status: {final_status} ---")

async def main():
    logger.info("Starting AI Artist Batch Runner...")
    while True:
        try:
            await run_artist_cycle()
            # Add a short delay between cycles
            sleep_time = random.uniform(5, 15) # Random sleep between 5-15 seconds
            logger.info(f"Cycle finished. Sleeping for {sleep_time:.1f} seconds...")
            await asyncio.sleep(sleep_time)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down batch runner...")
            break
        except Exception as e:
            logger.critical(f"Unhandled exception in main loop: {e}", exc_info=True)
            logger.info("Restarting cycle after error...")
            await asyncio.sleep(30) # Wait 30s before restarting after critical error

if __name__ == "__main__":
    asyncio.run(main())

