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
ARTIST_RETIREMENT_THRESHOLD = int(os.getenv("ARTIST_RETIREMENT_THRESHOLD", 5))
ARTIST_CREATION_PROBABILITY = float(os.getenv("ARTIST_CREATION_PROBABILITY", 0.1))

# --- A/B Testing Configuration ---
AB_TESTING_ENABLED = os.getenv("AB_TESTING_ENABLED", "False").lower() == "true"
# Example: Define variations for suno_prompt prefix
AB_TEST_VARIATIONS = {
    "suno_prompt_prefix": [
        "A dreamy {genre} track", # Control (Variation A)
        "An experimental {genre} piece", # Variation B
        "A high-energy {genre} anthem" # Variation C
    ]
    # Add more parameter variations here as needed
}
AB_TEST_PARAMETER = "suno_prompt_prefix" # Parameter to test

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
            "created_at": datetime.utcnow().isoformat(),
            "last_run_at": None,
            "performance_history": [],
            "consecutive_rejections": 0,
            "is_active": True
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

def create_new_artist_profile():
    """Uses LLM to generate a new artist profile and adds it to the DB."""
    logger.info("Attempting to create a new artist profile...")
    new_id = str(uuid.uuid4())
    new_artist_data = {
        "artist_id": new_id,
        "name": f"Generated Artist {new_id[:4]}",
        "genre": random.choice(["electronic", "ambient", "lofi", "hyperpop"]), # Example genres
        "style_notes": "Experimental, evolving style.",
        "created_at": datetime.utcnow().isoformat(),
        "last_run_at": None,
        "performance_history": [],
        "consecutive_rejections": 0,
        "is_active": True
    }
    if add_artist(new_artist_data):
        logger.info(f"Created and added new artist profile to DB: ID={new_id}, Name=", {new_artist_data["name"]}, ")")
        return new_artist_data
    else:
        logger.error(f"Failed to add newly created artist {new_id} to the database.")
        return None

def select_next_artist():
    """Selects an active artist from DB, potentially creating a new one."""
    logger.info("Selecting next artist with lifecycle logic (using DB)...")
    active_artists = get_all_artists(only_active=True)

    if random.random() < ARTIST_CREATION_PROBABILITY or not active_artists:
        logger.info("Triggering new artist creation...")
        new_artist = create_new_artist_profile()
        if new_artist:
            logger.info(f"Successfully created new artist {new_artist["artist_id"]}. Selecting it.")
            return new_artist
        else:
            logger.warning("Failed to create a new artist. Proceeding with existing pool.")
            active_artists = get_all_artists(only_active=True)
            if not active_artists:
                 logger.error("No active artists available and failed to create a new one. Cannot proceed.")
                 return None

    if not active_artists:
        logger.error("No active artists found in the database.")
        return None

    sorted_artists = sorted(
        active_artists,
        key=lambda a: datetime.fromisoformat(a["last_run_at"]) if a["last_run_at"] else datetime.min
    )
    selected_artist = sorted_artists[0]
    logger.info(f"Selected artist {selected_artist["artist_id"]} (", {selected_artist["name"]}, ") based on least recent run.")
    return selected_artist

# --- Parameter Adaptation with A/B Testing --- #
def get_adapted_parameters(artist_profile):
    """Gets generation parameters, applying A/B test variations if enabled."""
    genre = artist_profile.get("genre", "synthwave")
    style_notes = artist_profile.get("style_notes", "standard synthwave")
    ab_test_info = {"enabled": False, "parameter": None, "variation_index": None, "variation_value": None}

    # Base parameters
    base_suno_prompt = f"upbeat tempo, inspired by {style_notes}"
    base_params = {
        "suno_style": genre,
        "video_keywords": [genre, "retro", "neon", "dreamy"],
        "make_instrumental": False,
    }

    # Apply A/B Test Variation if enabled
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

            # Example: Apply variation to suno_prompt_prefix
            if AB_TEST_PARAMETER == "suno_prompt_prefix":
                prompt_prefix = chosen_variation.format(genre=genre) # Format with genre
                base_params["suno_prompt"] = f"{prompt_prefix}, {base_suno_prompt}"
            # Add logic here for other testable parameters
            # elif AB_TEST_PARAMETER == "some_other_param":
            #     base_params["some_other_param"] = chosen_variation
            else:
                 logger.warning(f"A/B test parameter ", {AB_TEST_PARAMETER}, " not handled in get_adapted_parameters. Using default.")
                 # Fallback to default if parameter logic isn't implemented
                 base_params["suno_prompt"] = f"A dreamy {genre} track, {base_suno_prompt}"
        else:
            logger.warning(f"A/B testing enabled but no variations defined for ", {AB_TEST_PARAMETER}, ". Using default.")
            base_params["suno_prompt"] = f"A dreamy {genre} track, {base_suno_prompt}"
    else:
        # Default behavior when A/B testing is disabled or parameter not defined
        base_params["suno_prompt"] = f"A dreamy {genre} track, {base_suno_prompt}"

    # Include A/B test info in the returned dictionary
    base_params["ab_test_info"] = ab_test_info
    return base_params

# --- Placeholder Generation Functions (Keep as is) ---
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

# --- Auto-Reflection Function (Keep as is) --- #
async def generate_reflection(artist_profile, parameters, track_info, video_info):
    """Generates a reflection on the created content using the LLM Orchestrator."""
    if not llm_orchestrator:
        logger.warning("LLM Orchestrator not initialized. Skipping reflection.")
        return None

    logger.info("Generating reflection for the created content...")
    try:
        # Exclude ab_test_info from the prompt to LLM
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
        1. Assess the alignment of the generated track and video with the artist"s profile (genre, style notes).
        2. Evaluate the quality and coherence of the track and video combination.
        3. Suggest 1-2 specific improvements for the next generation cycle for this artist (e.g., prompt adjustments, keyword changes, style focus).
        4. Provide a brief overall assessment (e.g., "Good alignment", "Needs improvement in video coherence", "Excellent match").
        Keep the reflection concise and actionable.
        """

        reflection_text = await llm_orchestrator.generate_text(
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

# --- Telegram Integration & Status Handling (Record A/B Test Info) --- #

def update_run_status(run_id, new_status, reason=None, reflection=None, artist_id=None):
    """Updates the status, reason, and optionally reflection in the run"s status file.
       Also triggers artist performance update in DB if status is final.
    """
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    try:
        run_data = {}
        if os.path.exists(status_filepath):
            try:
                with open(status_filepath, "r") as f:
                    run_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding existing status file {status_filepath}, will overwrite: {e}")
            except IOError as e:
                logger.error(f"Error reading existing status file {status_filepath}, will overwrite: {e}")
        else:
            logger.warning(f"Status file {status_filepath} not found for update, creating basic structure.")
            run_data = {"run_id": run_id, "created_at": datetime.utcnow().isoformat()}

        run_data["status"] = new_status
        run_data["updated_at"] = datetime.utcnow().isoformat()
        if reason:
            run_data["final_status_reason"] = reason
        if reflection:
             run_data["reflection"] = reflection
        if new_status in ["approved", "rejected"] and "approved_at" not in run_data:
            run_data["approved_at"] = run_data["updated_at"]
        if artist_id:
            run_data["artist_id"] = artist_id

        with open(status_filepath, "w") as f:
            json.dump(run_data, f, indent=4)
        logger.info(f"Updated status for run {run_id} to ", {new_status}, " in {status_filepath}")

        final_statuses = ["approved", "rejected", "failed_setup", "failed_generation", "failed_to_send", "failed_runtime_error", "aborted"]
        if new_status in final_statuses:
            current_artist_id = run_data.get("artist_id")
            if current_artist_id:
                update_artist_performance_db(current_artist_id, run_id, new_status, ARTIST_RETIREMENT_THRESHOLD)
            else:
                logger.warning(f"Cannot update artist performance for run {run_id}: artist_id missing in status file.")

    except Exception as e:
        logger.error(f"Failed to update status file {status_filepath} or artist DB: {e}", exc_info=True)

def create_initial_run_status(
    run_id, artist_profile, parameters, track_info, video_info, reflection_text
):
    """Creates the initial status file for a run, including parameters, reflection, and A/B test info."""
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    artist_id = artist_profile.get("artist_id")
    # Extract A/B test info from parameters
    ab_test_info = parameters.get("ab_test_info", {"enabled": False})
    # Prepare parameters for saving (exclude ab_test_info itself)
    saved_params = {k: v for k, v in parameters.items() if k != "ab_test_info"}

    run_data = {
        "run_id": run_id,
        "status": "pending_approval",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "artist_id": artist_id,
        "artist_name": artist_profile.get("name"),
        "genre": artist_profile.get("genre"),
        "style_notes": artist_profile.get("style_notes"),
        "track_id": track_info.get("track_id"),
        "track_url": track_info.get("track_url"),
        "video_url": video_info.get("video_url"),
        "video_source": video_info.get("source"),
        "reflection": reflection_text,
        "approved_at": None,
        "final_status_reason": None,
        "parameters": saved_params, # Store the actual parameters used
        "ab_test_info": ab_test_info # Store A/B test details
    }
    try:
        with open(status_filepath, "w") as f:
            json.dump(run_data, f, indent=4)
        logger.info(f"Created initial status file with reflection and A/B info: {status_filepath}")
        return True
    except IOError as e:
        logger.error(f"Failed to create initial status file {status_filepath}: {e}")
        update_run_status(run_id, "failed_setup", f"IOError creating status file: {e}", artist_id=artist_id)
        return False

def send_to_telegram_for_approval(
    run_id, artist_profile, parameters, track_info, video_info, reflection_text
):
    """Sends content preview to Telegram after creating the status file."""
    logger.info(f"Preparing to send run {run_id} to Telegram for approval...")
    artist_id = artist_profile.get("artist_id")

    if not create_initial_run_status(
        run_id, artist_profile, parameters, track_info, video_info, reflection_text
    ):
        logger.error(f"Failed to create initial status file for run {run_id}. Cannot send to Telegram.")
        return False

    logger.info(f"Sending run {run_id} content preview to Telegram...")
    try:
        caption = f"Artist: {artist_profile.get("name", "Unknown")}\nRun ID: {run_id}\nTrack: {track_info.get("track_url", "N/A")}\nVideo: {video_info.get("video_url", "N/A")}"
        # Optionally add A/B test info to caption for moderators?
        ab_test_info = parameters.get("ab_test_info", {})
        if ab_test_info.get("enabled"): 
            caption += f"\nA/B Test: {ab_test_info.get("parameter")} - Var {ab_test_info.get("variation_index")}"

        success = asyncio.run(
            send_preview_to_telegram(
                artist_name=artist_profile.get("name", "Unknown Artist"),
                track_url=track_info.get("track_url", ""),
                video_url=video_info.get("video_url", ""),
                release_id=run_id,
                # caption=caption # Uncomment if telegram_service supports custom captions
            )
        )
        if success:
            logger.info(f"Successfully sent run {run_id} to Telegram.")
            return True
        else:
            logger.error(f"Failed to send run {run_id} to Telegram (telegram_service returned False).")
            update_run_status(run_id, "failed_to_send", "Telegram service failed", artist_id=artist_id)
            return False
    except Exception as e:
        logger.error(f"Exception sending run {run_id} to Telegram: {e}", exc_info=True)
        update_run_status(run_id, "failed_to_send", f"Exception: {e}", artist_id=artist_id)
        return False

def check_approval_status(run_id):
    """Checks the status file updated by the webhook server."""
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    try:
        if not os.path.exists(status_filepath):
            logger.warning(f"Status file not found for run {run_id}: {status_filepath}. Assuming pending.")
            return None

        with open(status_filepath, "r") as f:
            run_data = json.load(f)

        current_status = run_data.get("status")

        if current_status == "approved":
            logger.debug(f"Approval status for run {run_id}: Approved")
            return True
        elif current_status == "rejected":
            logger.debug(f"Approval status for run {run_id}: Rejected")
            return False
        elif current_status == "pending_approval":
            logger.debug(f"Approval status for run {run_id}: Pending")
            return None
        elif current_status in ["failed_setup", "failed_generation", "failed_to_send", "failed_runtime_error", "aborted"]:
             logger.warning(f"Run {run_id} encountered failure status: {current_status}. Treating as rejected for approval check.")
             return False
        else:
            logger.warning(f"Run {run_id} has unexpected status: {current_status}. Treating as pending for approval check.")
            return None

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding status file {status_filepath}: {e}. Treating as pending.")
        return None
    except IOError as e:
        logger.error(f"Error reading status file {status_filepath}: {e}. Treating as pending.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error checking status file {status_filepath}: {e}", exc_info=True)
        return None

# --- Approval Handling & Output (Keep as is) --- #
def save_approved_content(run_id, artist_profile, track_info, video_info):
    """Saves metadata about approved content (placeholder)."""
    approved_dir = os.path.join(OUTPUT_DIR, "approved")
    os.makedirs(approved_dir, exist_ok=True)
    approved_filepath = os.path.join(approved_dir, f"approved_{run_id}.json")

    # Load the full run status to get parameters and A/B info
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    run_data = {}
    if os.path.exists(status_filepath):
        try:
            with open(status_filepath, "r") as f:
                run_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading run status file {status_filepath} for approved content save: {e}")

    content_data = {
        "run_id": run_id,
        "approved_at": datetime.utcnow().isoformat(),
        "artist_id": artist_profile.get("artist_id"),
        "artist_name": artist_profile.get("name"),
        "track_id": track_info.get("track_id"),
        "track_url": track_info.get("track_url"),
        "video_url": video_info.get("video_url"),
        "video_source": video_info.get("source"),
        "parameters": run_data.get("parameters", {}), # Include parameters
        "ab_test_info": run_data.get("ab_test_info", {"enabled": False}) # Include A/B info
    }
    try:
        with open(approved_filepath, "w") as f:
            json.dump(content_data, f, indent=4)
        logger.info(f"Saved approved content metadata (with params/AB info) to {approved_filepath}")
        return approved_filepath
    except IOError as e:
        logger.error(f"Failed to save approved content metadata: {e}")
        return None

# --- Main Batch Runner Logic (Integrates A/B Testing) --- #
async def run_artist_cycle():
    """Executes a single cycle of artist selection, content generation, and approval request."""
    run_id = str(uuid.uuid4())
    logger.info(f"Starting artist cycle run_id: {run_id}")
    artist_profile = None
    artist_id = None
    try:
        # 1. Select Artist
        artist_profile = select_next_artist()
        if not artist_profile:
            logger.error("Failed to select an artist. Aborting cycle.")
            return
        artist_id = artist_profile.get("artist_id")

        # 2. Get Parameters (with potential A/B variation)
        parameters = get_adapted_parameters(artist_profile)

        # 3. Generate Track
        track_info = generate_track(parameters)
        if not track_info:
            logger.error(f"Failed to generate track for artist {artist_id}. Aborting cycle.")
            update_run_status(run_id, "failed_generation", "Track generation failed", artist_id=artist_id)
            return

        # 4. Select Video
        video_info = select_video(track_info, parameters.get("video_keywords", []))
        if not video_info:
            logger.error(f"Failed to select video for artist {artist_id}. Aborting cycle.")
            update_run_status(run_id, "failed_generation", "Video selection failed", artist_id=artist_id)
            return

        # 5. Generate Reflection
        reflection_text = await generate_reflection(artist_profile, parameters, track_info, video_info)
        if not reflection_text:
             logger.warning(f"Proceeding without reflection for run {run_id}.")
             reflection_text = "Reflection generation failed or was skipped."

        # 6. Send for Approval (creates status file with A/B info)
        sent_ok = send_to_telegram_for_approval(
            run_id, artist_profile, parameters, track_info, video_info, reflection_text
        )
        if not sent_ok:
            logger.error(f"Failed to send run {run_id} for approval. Cycle ended.")
            return

        # 7. Wait for Approval / Timeout
        logger.info(f"Waiting for approval status for run {run_id} (max {MAX_APPROVAL_WAIT_TIME}s)...")
        start_time = time.time()
        approval_status = None
        while time.time() - start_time < MAX_APPROVAL_WAIT_TIME:
            approval_status = check_approval_status(run_id)
            if approval_status is not None:
                break
            await asyncio.sleep(POLL_INTERVAL)

        # 8. Process Result
        if approval_status is True:
            logger.info(f"Run {run_id} approved.")
            update_run_status(run_id, "approved", artist_id=artist_id)
            approved_metadata_path = save_approved_content(run_id, artist_profile, track_info, video_info)
            if approved_metadata_path:
                logger.info(f"Triggering release chain for approved run {run_id}...")
                process_approved_run(run_id, approved_metadata_path)
            else:
                logger.error(f"Failed to save approved metadata for run {run_id}. Release chain not triggered.")

        elif approval_status is False:
            logger.info(f"Run {run_id} rejected.")
            status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
            current_status = "unknown"
            if os.path.exists(status_filepath):
                 try:
                     with open(status_filepath, "r") as f:
                         run_data = json.load(f)
                         current_status = run_data.get("status", "unknown")
                 except Exception:
                     pass
            if current_status != "rejected":
                update_run_status(run_id, "rejected", "Rejected by user/moderator or failure", artist_id=artist_id)
            else:
                 update_artist_performance_db(artist_id, run_id, "rejected", ARTIST_RETIREMENT_THRESHOLD)

        else: # Timeout
            logger.warning(f"Run {run_id} timed out waiting for approval.")
            update_run_status(run_id, "aborted", "Timeout waiting for approval", artist_id=artist_id)

    except Exception as e:
        run_id_str = run_id if "run_id" in locals() else "UNKNOWN"
        artist_id_str = artist_id if artist_id else "UNKNOWN"
        logger.error(f"Unhandled exception in artist cycle run_id={run_id_str}: {e}", exc_info=True)
        if "run_id" in locals():
            update_run_status(run_id, "failed_runtime_error", f"Unhandled exception: {e}", artist_id=artist_id_str)

async def main():
    logger.info("Starting AI Artist Batch Runner...")
    while True:
        await run_artist_cycle()
        logger.info("Cycle finished. Waiting before starting next cycle...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Batch runner stopped by user.")
    except Exception as e:
        logger.critical(f"Critical error in main loop: {e}", exc_info=True)
        sys.exit(1)

