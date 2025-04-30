#!/usr/bin/env python3

import logging
import os
import sys
import time
import uuid
import json
import asyncio
from datetime import datetime
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
    # Import the release chain processor
    from release_chain.release_chain import process_approved_run
except ImportError as e:
    logging.error(f"Failed to import core modules or release_chain: {e}. Exiting.")
    sys.exit(1)

# --- Configuration ---
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "batch_runner.log")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RUN_STATUS_DIR = os.path.join(OUTPUT_DIR, "run_status")
MAX_APPROVAL_WAIT_TIME = int(os.getenv("MAX_APPROVAL_WAIT_TIME", 300))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

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
    "CRITICAL": logging.CRITICAL
}
effective_log_level = log_level_mapping.get(LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=effective_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"Log level set to: {LOG_LEVEL}")
logger.info(f"Max approval wait time: {MAX_APPROVAL_WAIT_TIME}s")
logger.info(f"Approval poll interval: {POLL_INTERVAL}s")

# --- Placeholder Functions (Replace with actual integrations) ---

def select_next_artist():
    logger.info("Selecting next artist (placeholder)...")
    return {"artist_id": 1, "name": "Synthwave Dreamer", "genre": "synthwave"}

def get_adapted_parameters(artist_profile):
    logger.info(f"Getting adapted parameters for artist {artist_profile.get(\'artist_id\')} (placeholder)...")
    genre = artist_profile.get("genre", "synthwave")
    return {
        "suno_prompt": f"A dreamy {genre} track, upbeat tempo",
        "suno_style": genre,
        "video_keywords": [genre, "retro", "neon"],
        "make_instrumental": False
    }

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
    logger.info(f"Selecting video for track {track_info.get(\'track_id\')} with keywords: {video_keywords} (placeholder)...")
    try:
        time.sleep(1)
        video_url = f"http://fake-pexels.com/video/{uuid.uuid4()}"
        logger.info(f"Selected video (placeholder): URL={video_url}")
        return {"video_url": video_url, "source": "pexels"}
    except Exception as e:
        logger.error(f"Error during placeholder video selection: {e}", exc_info=True)
        return None

# --- Telegram Integration & Status Handling --- #

def update_run_status(run_id, new_status, reason=None):
    """Updates the status and reason in the run's status file."""
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
        if new_status in ["approved", "rejected"] and "approved_at" not in run_data:
             run_data["approved_at"] = run_data["updated_at"]

        with open(status_filepath, "w") as f:
            json.dump(run_data, f, indent=4)
        logger.info(f"Updated status for run {run_id} to \'{new_status}\' in {status_filepath}")

    except Exception as e:
        logger.error(f"Failed to update status file {status_filepath}: {e}", exc_info=True)

def create_initial_run_status(run_id, artist_profile, parameters, track_info, video_info):
    """Creates the initial status file for a run, including parameters used."""
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    run_data = {
        "run_id": run_id,
        "status": "pending_approval",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "artist_id": artist_profile.get("artist_id"),
        "artist_name": artist_profile.get("name"),
        "genre": artist_profile.get("genre"), # Store genre from profile
        "track_id": track_info.get("track_id"),
        "track_url": track_info.get("track_url"),
        "video_url": video_info.get("video_url"),
        "video_source": video_info.get("source"),
        "approved_at": None,
        "final_status_reason": None,
        # Store parameters used for release chain
        "suno_prompt": parameters.get("suno_prompt"),
        "suno_style": parameters.get("suno_style"),
        "video_keywords": parameters.get("video_keywords"),
        "make_instrumental": parameters.get("make_instrumental")
        # Add other parameters if needed
    }
    try:
        with open(status_filepath, "w") as f:
            json.dump(run_data, f, indent=4)
        logger.info(f"Created initial status file: {status_filepath}")
        return True
    except IOError as e:
        logger.error(f"Failed to create initial status file {status_filepath}: {e}")
        update_run_status(run_id, "failed_setup", f"IOError creating status file: {e}")
        return False

def send_to_telegram_for_approval(run_id, artist_profile, parameters, track_info, video_info):
    """Sends content preview to Telegram using the telegram_service."""
    logger.info(f"Sending run {run_id} to Telegram for approval...")

    # Pass parameters to save them in the status file
    if not create_initial_run_status(run_id, artist_profile, parameters, track_info, video_info):
        return False

    try:
        success = asyncio.run(send_preview_to_telegram(
            artist_name=artist_profile.get("name", "Unknown Artist"),
            track_url=track_info.get("track_url", ""),
            video_url=video_info.get("video_url", ""),
            release_id=run_id
        ))
        if success:
            logger.info(f"Successfully sent run {run_id} to Telegram.")
            return True
        else:
            logger.error(f"Failed to send run {run_id} to Telegram (telegram_service returned False).")
            update_run_status(run_id, "failed_to_send", "Telegram service failed")
            return False
    except Exception as e:
        logger.error(f"Exception sending run {run_id} to Telegram: {e}", exc_info=True)
        update_run_status(run_id, "failed_to_send", f"Exception: {e}")
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
        else:
            logger.warning(f"Run {run_id} has unexpected status: {current_status}. Treating as rejected.")
            return False

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding status file {status_filepath}: {e}. Treating as pending.")
        return None
    except IOError as e:
        logger.error(f"Error reading status file {status_filepath}: {e}. Treating as pending.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error checking status file {status_filepath}: {e}", exc_info=True)
        return None

# --- Approval Handling & Output --- #

def save_approved_content(run_id):
    """Confirms approval and marks content as ready (data already in status file)."""
    logger.info(f"Processing approved content for run {run_id}...")
    status_filepath = os.path.join(RUN_STATUS_DIR, f"run_{run_id}.json")
    try:
        with open(status_filepath, "r") as f:
            run_data = json.load(f)

        if run_data.get("status") == "approved":
            logger.info(f"Confirmed run {run_id} is approved. Ready for release chain.")
            return True
        else:
            logger.warning(f"Attempted to save content for run {run_id}, but status is not \'approved\' ({run_data.get(\'status\')}).")
            return False
    except Exception as e:
        logger.error(f"Error processing approved content for run {run_id}: {e}", exc_info=True)
        return False

def trigger_release_logic(run_id):
    """Triggers the release chain processing for the approved run."""
    logger.info(f"Triggering release chain logic for approved run {run_id}...")
    try:
        # Call the imported function from release_chain.py
        success = process_approved_run(run_id)
        if success:
            logger.info(f"Release chain completed successfully for run {run_id}.")
        else:
            logger.error(f"Release chain failed for run {run_id}.")
            # Optionally update run status again to indicate release failure?
            # update_run_status(run_id, "failed_release", "Release chain processing failed")
    except Exception as e:
        logger.error(f"Exception during release chain processing for run {run_id}: {e}", exc_info=True)
        # update_run_status(run_id, "failed_release", f"Exception: {e}")

# --- Main Batch Runner Cycle --- #

def run_batch_cycle():
    """Runs a single cycle of the artist content generation batch process."""
    run_id = str(uuid.uuid4())[:8]
    logger.info(f"--- Starting Batch Runner Cycle: Run ID {run_id} ---")

    try:
        # 1. Select Artist
        artist_profile = select_next_artist()
        if not artist_profile:
            logger.warning("No artist selected. Skipping cycle.")
            return
        logger.debug(f"Selected artist: {artist_profile}")

        # 2. Get Parameters
        parameters = get_adapted_parameters(artist_profile)
        logger.debug(f"Adapted parameters: {parameters}")

        # 3. Generate Track
        track_info = generate_track(parameters)
        if not track_info:
            logger.error(f"Track generation failed for run {run_id}. Skipping cycle.")
            update_run_status(run_id, "failed_generation", "Track generation failed")
            return
        logger.debug(f"Generated track info: {track_info}")

        # 4. Select Video
        video_info = select_video(track_info, parameters.get("video_keywords", []))
        if not video_info:
            logger.error(f"Video selection failed for run {run_id}. Skipping cycle.")
            update_run_status(run_id, "failed_generation", "Video selection failed")
            return
        logger.debug(f"Selected video info: {video_info}")

        # 5. Send for Approval (Pass parameters to be saved)
        sent_ok = send_to_telegram_for_approval(run_id, artist_profile, parameters, track_info, video_info)
        if not sent_ok:
            return

        # 6. Wait for Approval (Polling)
        logger.info(f"Waiting up to {MAX_APPROVAL_WAIT_TIME}s for approval for run {run_id}...")
        start_wait = time.time()
        final_approval_status = None
        while time.time() - start_wait < MAX_APPROVAL_WAIT_TIME:
            approval_status = check_approval_status(run_id)
            if approval_status is not None:
                final_approval_status = approval_status
                break
            time.sleep(POLL_INTERVAL)
        else:
            logger.warning(f"Timeout waiting for approval for run {run_id}. Assuming rejected.")
            final_approval_status = False
            update_run_status(run_id, "rejected", "Timeout waiting for approval")

        # 7. Handle Approval Result
        if final_approval_status:
            logger.info(f"Run {run_id} approved by user.")
            if save_approved_content(run_id):
                # Call the updated trigger function which now calls the release chain
                trigger_release_logic(run_id)
        else:
            logger.info(f"Run {run_id} was rejected or timed out.")

    except KeyboardInterrupt:
        logger.warning(f"Keyboard interrupt received during run {run_id}. Shutting down.")
        update_run_status(run_id, "aborted", "Keyboard interrupt")
        raise
    except Exception as e:
        logger.critical(f"Critical unexpected error during batch cycle run {run_id}: {e}", exc_info=True)
        update_run_status(run_id, "failed_runtime_error", f"Critical Exception: {e}")

    finally:
        logger.info(f"--- Finished Batch Runner Cycle: Run ID {run_id} ---")

# --- Script Execution & Scheduling Notes --- #

if __name__ == "__main__":
    logger.info("Executing Artist Batch Runner script (single cycle)...")
    logger.info("NOTE: This script relies on an external webhook server to update run status files.")
    try:
        run_batch_cycle()
    except KeyboardInterrupt:
        logger.info("Batch runner execution stopped by user.")
    except Exception as e:
        logger.critical(f"Unhandled exception at top level: {e}", exc_info=True)
    finally:
        logger.info("Artist Batch Runner script finished.")

