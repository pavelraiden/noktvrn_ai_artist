#!/usr/bin/env python3

import logging
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import threading
import time

# --- Load Environment Variables ---
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=DOTENV_PATH)
PROJECT_ROOT_DOTENV = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(PROJECT_ROOT_DOTENV):
    load_dotenv(dotenv_path=PROJECT_ROOT_DOTENV, override=False)

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Configuration ---
LOG_LEVEL = os.getenv("UPLOADER_LOG_LEVEL", "INFO").upper()
OUTPUT_BASE_DIR = os.getenv(    "OUTPUT_BASE_DIR", os.path.join(PROJECT_ROOT, "output"))
RELEASES_DIR = os.getenv(    "RELEASES_DIR", os.path.join(OUTPUT_BASE_DIR, "releases"))
DEPLOY_READY_DIR = os.getenv(    "DEPLOY_READY_DIR", os.path.join(OUTPUT_BASE_DIR, "deploy_ready"))
RELEASE_QUEUE_FILE = os.getenv(    "RELEASE_QUEUE_FILE", os.path.join(OUTPUT_BASE_DIR, "release_queue.json"))
UPLOAD_STATUS_FILE = os.getenv(    "UPLOAD_STATUS_FILE",     os.path.join(OUTPUT_BASE_DIR, "release_upload_status.json"),)

# Ensure directories exist
os.makedirs(RELEASES_DIR, exist_ok=True)
os.makedirs(DEPLOY_READY_DIR, exist_ok=True)

# --- Logging Setup ---
log_level_mapping = {    "DEBUG": logging.DEBUG,     "INFO": logging.INFO,     "WARNING": logging.WARNING,     "ERROR": logging.ERROR,     "CRITICAL": logging.CRITICAL,}
effective_log_level = log_level_mapping.get(LOG_LEVEL, logging.INFO)

logging.basicConfig(    level=effective_log_level,     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",     handlers=[logging.StreamHandler(sys.stdout)],  # Add file handler if needed
)
logger = logging.getLogger(__name__)

# --- File Lock for Concurrent Writes --- #
file_lock = threading.Lock()

# --- Helper Functions --- #


def load_json_file(filepath):
    """Loads data from a JSON file."""
    try:
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, "r") as f:
                return json.load(f)
        else:
            logger.warning(f"File not found or empty: {filepath}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file {filepath}: {e}")
        return None
    except IOError as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None


def save_json_file(data, filepath):
    """Saves data to a JSON file."""
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.debug(f"Saved JSON file: {filepath}")
        return True
    except IOError as e:
        logger.error(f"Failed to save JSON file {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error serializing data to {filepath}: {e}")
        return False


def find_releases_to_upload():
    """Scans the release queue to find releases ready for upload processing."""
    logger.info(f"Scanning release queue file: {RELEASE_QUEUE_FILE}")
    queued_releases = load_json_file(RELEASE_QUEUE_FILE)
    upload_statuses = load_json_file(UPLOAD_STATUS_FILE) or {}

    if not isinstance(queued_releases, list):
        logger.error("Release queue file is not a valid list or is empty.")
        return []

    releases_to_process = []
    for entry in queued_releases:
        if (            isinstance(entry, dict)             and "release_id" in entry             and "release_directory" in entry        ):
            release_id = entry["release_id"]
            current_status = upload_statuses.get(release_id, {}).get(                "overall_status"            )
            if current_status not in [                "processed",                 "failed_permanently",                 "prepared_for_deploy",            ]:
                releases_to_process.append(entry)
            else:
                logger.info(                    f"Skipping release {release_id} with status:                         {current_status}"                )
        else:
            logger.warning(f"Skipping invalid entry in queue: {entry}")

    logger.info(        f"Found {len(releases_to_process)} releases in queue to process."    )
    return releases_to_process


# --- Status Logging --- #


def log_upload_status(release_id, overall_status, platform_statuses):
    """Logs the upload status for a release to the status JSON file."""
    with file_lock:
        logger.debug(            f"Attempting to log status for {release_id}: {overall_status}"        )
        statuses = load_json_file(UPLOAD_STATUS_FILE) or {}
        if not isinstance(statuses, dict):
            logger.error(                f"Upload status file {UPLOAD_STATUS_FILE} is not a dictionary.                     Resetting."            )
            statuses = {}

        statuses[release_id] = {            "overall_status": overall_status,             "platform_details": platform_statuses,             "last_updated": datetime.utcnow().isoformat(),        }

        if save_json_file(statuses, UPLOAD_STATUS_FILE):
            logger.info(                f"Successfully logged upload status for {release_id}:                     {overall_status}"            )
            return True
        else:
            logger.error(f"Failed to log upload status for {release_id}.")
            return False


# --- Dummy Upload Functions --- #


def upload_to_tunecore(release_id, release_dir):
    """Placeholder function to simulate uploading to TuneCore."""
    logger.info(        f"[DUMMY] Simulating upload of release {release_id} from {release_dir}             to TuneCore..."    )
    time.sleep(1)
    success = True
    if success:
        logger.info(f"[DUMMY] Successfully uploaded {release_id} to TuneCore.")
        return "uploaded_tunecore"
    else:
        logger.error(f"[DUMMY] Failed to upload {release_id} to TuneCore.")
        return "failed_tunecore"


def upload_to_web3_platform(release_id, release_dir):
    """Placeholder function to simulate uploading to a Web3 platform."""
    logger.info(        f"[DUMMY] Simulating upload of release {release_id} from {release_dir}             to Web3 Platform..."    )
    time.sleep(1)
    success = True
    if success:
        logger.info(            f"[DUMMY] Successfully uploaded {release_id} to Web3 Platform."        )
        return "uploaded_web3"
    else:
        logger.error(            f"[DUMMY] Failed to upload {release_id} to Web3 Platform."        )
        return "failed_web3"


# --- Deploy Ready Preparation --- #


def prepare_deploy_ready_output(release_id, source_release_dir):
    """Copies essential release files to the deploy_ready directory."""
    target_dir = Path(DEPLOY_READY_DIR) / release_id
    logger.info(        f"Preparing deploy-ready output for {release_id} in {target_dir}"    )

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        files_to_copy = [
            "metadata.json",
            "prompts_used.json",
            "cover_art.png",  # Placeholder
            "final_audio.mp3",  # Placeholder
            "final_video.mp4",  # Placeholder
            # TODO: Add feedback_score.json once implemented
        ]
        copied_files = []
        failed_files = []

        for filename in files_to_copy:
            source_file = Path(source_release_dir) / filename
            target_file = target_dir / filename
            if source_file.exists():
                try:
                    shutil.copy2(                        source_file, target_file                    )  # copy2 preserves metadata
                    copied_files.append(filename)
                    logger.debug(f"Copied {filename} to {target_dir}")
                except Exception as copy_err:
                    logger.error(                        f"Failed to copy {filename} for {release_id}:                             {copy_err}"                    )
                    failed_files.append(filename)
            else:
                logger.warning(                    f"Source file {filename} not found in {source_release_dir}                         for release {release_id}"                )
                failed_files.append(filename + " (missing)")

        if not failed_files:
            logger.info(                f"Successfully prepared deploy-ready output for {release_id}."            )
            return True
        else:
            logger.error(                f"Failed to prepare some deploy-ready files for {release_id}:                     {failed_files}"            )
            return False

    except Exception as e:
        logger.critical(            "Error creating deploy-ready directory or copying files for "             f"{release_id}: {e}",             exc_info=True,        )
        return False


# --- Main Processing Function --- #


def process_single_release(release_info):
    """Processes a single release: dummy uploads, status logging,         deploy prep."""
    release_id = release_info.get("release_id")
    release_dir_str = release_info.get("release_directory")

    if not release_id or not release_dir_str:
        logger.error(f"Invalid release info provided: {release_info}")
        log_upload_status(release_id or "unknown", "failed_invalid_info", [])
        return False

    release_dir = Path(release_dir_str)
    if not release_dir.is_dir():
        logger.error(f"Release directory not found: {release_dir}")
        log_upload_status(release_id, "failed_dir_not_found", [])
        return False

    logger.info(f"Processing release: {release_id} from {release_dir}")

    # 1. Perform Dummy Uploads
    platform_results = []
    upload_successful = True
    try:
        tunecore_status = upload_to_tunecore(release_id, release_dir)
        platform_results.append(tunecore_status)
        if "failed" in tunecore_status:
            upload_successful = False

        web3_status = upload_to_web3_platform(release_id, release_dir)
        platform_results.append(web3_status)
        if "failed" in web3_status:
            upload_successful = False

    except Exception as e:
        logger.error(            f"Error during dummy upload for {release_id}: {e}", exc_info=True        )
        log_upload_status(release_id, "failed_upload_error", platform_results)
        return False

    # Determine overall status for logging
    overall_log_status = "processed" if upload_successful else "failed"
    if not upload_successful:
        logger.error(            f"One or more dummy uploads failed for release {release_id}."        )
    else:
        logger.info(f"All dummy uploads completed for release {release_id}.")

    # 2. Prepare Deploy Ready Output (if uploads successful)
    deploy_prep_successful = False
    if upload_successful:
        deploy_prep_successful = prepare_deploy_ready_output(            release_id, release_dir        )
        if not deploy_prep_successful:
            overall_log_status = (
                "failed_deploy_prep"  # Update status if prep fails
            )
            logger.error(
                f"Failed to prepare deploy-ready output for {release_id}."
            )
        else:
            overall_log_status = "prepared_for_deploy"  # Final success status
            logger.info(                f"Successfully prepared deploy-ready output for {release_id}."            )

    # 3. Log Final Status
    log_upload_status(release_id, overall_log_status, platform_results)

    return upload_successful and deploy_prep_successful


# --- Main Script Logic --- #


def main():
    logger.info("--- Starting Release Uploader Script ---")

    releases = find_releases_to_upload()

    if not releases:
        logger.info("No releases found in the queue to process. Exiting.")
        return
    processed_count = 0
    failed_count = 0
    for release_info in releases:
        try:
            success = process_single_release(release_info)
            if success:
                processed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            release_id_for_log = release_info.get(                "release_id", "unknown_critical"            )
            logger.critical(                f"Unexpected error processing release {release_id_for_log}:                     {e}",                 exc_info=True,            )
            failed_count += 1
            log_upload_status(release_id_for_log, "failed_critical_error", [])

    logger.info(        f"Processing complete. Successfully prepared for deploy:             {processed_count}, Failed: {failed_count}"    )
    logger.info("--- Release Uploader Script Finished ---")


if __name__ == "__main__":
    main()