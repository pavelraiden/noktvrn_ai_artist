#!/usr/bin/env python3

import logging
import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import threading

# --- Load Environment Variables ---
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=DOTENV_PATH)
PROJECT_ROOT_DOTENV = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(PROJECT_ROOT_DOTENV):
    load_dotenv(dotenv_path=PROJECT_ROOT_DOTENV, override=False)

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Import Schemas ---
try:
    from .schemas import ReleaseMetadata, PromptsUsed
except ImportError:
    # Allow running script directly for testing if schemas are in the same dir
    try:
        from schemas import ReleaseMetadata, PromptsUsed
    except ImportError as e:
        logging.error(
            f"Failed to import schemas: {e}. Ensure schemas.py is accessible."
        )
        sys.exit(1)

# --- Configuration ---
LOG_LEVEL = os.getenv("RELEASE_CHAIN_LOG_LEVEL", "INFO").upper()
OUTPUT_BASE_DIR = os.getenv("OUTPUT_BASE_DIR", os.path.join(PROJECT_ROOT, "output"))
RELEASES_DIR = os.getenv("RELEASES_DIR", os.path.join(OUTPUT_BASE_DIR, "releases"))
RUN_STATUS_DIR = os.getenv(
    "RUN_STATUS_DIR", os.path.join(OUTPUT_BASE_DIR, "run_status")
)
RELEASE_LOG_FILE = os.getenv(
    "RELEASE_LOG_FILE", os.path.join(OUTPUT_BASE_DIR, "release_log.md")
)
RELEASE_QUEUE_FILE = os.getenv(
    "RELEASE_QUEUE_FILE", os.path.join(OUTPUT_BASE_DIR, "release_queue.json")
)
# New config for evolution log
EVOLUTION_LOG_FILE = os.getenv(
    "EVOLUTION_LOG_FILE",
    os.path.join(PROJECT_ROOT, "docs", "development", "artist_evolution_log.md"),
)

# Ensure directories exist
os.makedirs(RELEASES_DIR, exist_ok=True)
os.makedirs(RUN_STATUS_DIR, exist_ok=True)
# Ensure evolution log directory exists
if EVOLUTION_LOG_FILE:
    os.makedirs(os.path.dirname(EVOLUTION_LOG_FILE), exist_ok=True)

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
    handlers=[logging.StreamHandler(sys.stdout)],  # Add file handler if needed
)
logger = logging.getLogger(__name__)

# --- File Lock for Concurrent Writes --- #
file_lock = threading.Lock()

# --- Helper Functions --- #


def generate_artist_slug(artist_name):
    """Generates a filesystem-safe slug from the artist name."""
    if not artist_name:
        return "unknown_artist"
    slug = "".join(c for c in artist_name if c.isalnum() or c.isspace())
    slug = slug.strip().replace(" ", "_").lower()
    return slug if slug else "unknown_artist"


def create_release_directory(artist_slug, date_str):
    """Creates the structured directory for a new release."""
    try:
        release_path = Path(RELEASES_DIR) / f"{artist_slug}_{date_str}"
        release_path.mkdir(parents=True, exist_ok=True)
        (release_path / "audio").mkdir(exist_ok=True)
        (release_path / "video").mkdir(exist_ok=True)
        (release_path / "cover").mkdir(exist_ok=True)
        logger.info(f"Created release directory structure: {release_path}")
        return release_path
    except OSError as e:
        logger.error(f"Failed to create release directory {release_path}: {e}")
        return None


# --- Placeholder Asset Functions --- #


def download_asset(url, save_path):
    """Placeholder function to simulate downloading an asset."""
    logger.info(f"Simulating download of {url} to {save_path}")
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(f"Placeholder content for {url}\n")
        logger.info(f"Saved placeholder asset to {save_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to save placeholder asset {save_path}: {e}")
        return False


def generate_cover_art(artist_info, save_path):
    """Placeholder function to simulate cover art generation."""
    logger.info(
        f"Simulating cover art generation for artist {artist_info.get('name')} to {save_path}"
    )
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(f"Placeholder cover art for {artist_info.get('name')}\n")
        logger.info(f"Saved placeholder cover art to {save_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to save placeholder cover art {save_path}: {e}")
        return False


def analyze_track_structure(audio_path):
    """Placeholder function to simulate track analysis."""
    logger.info(f"Simulating analysis of track structure for {audio_path}")
    return "Intro - Verse - Chorus - Verse - Chorus - Bridge - Outro (Simulated)"


def get_prompts_from_run_data(run_data):
    """Extracts prompt information from the run data."""
    # TODO: Enhance this to extract full prompt chain (Author->Helper->Validator) if available
    return {
        "suno_prompt": run_data.get("suno_prompt", "N/A"),
        "video_keywords": run_data.get("video_keywords", []),
        "cover_prompt": "Placeholder cover prompt based on genre/mood",  # Placeholder
    }


# --- Metadata and File Saving --- #


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


def save_metadata_file(metadata_model, filepath):
    """Saves a Pydantic model as a JSON file."""
    try:
        with open(filepath, "w") as f:
            f.write(metadata_model.model_dump_json(indent=4))
        logger.info(f"Saved metadata file: {filepath}")
        return True
    except IOError as e:
        logger.error(f"Failed to save metadata file {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error serializing metadata to {filepath}: {e}")
        return False


def save_prompts_file(prompts_model, filepath):
    """Saves the prompts Pydantic model as a JSON file."""
    try:
        with open(filepath, "w") as f:
            f.write(prompts_model.model_dump_json(indent=4))
        logger.info(f"Saved prompts file: {filepath}")
        return True
    except IOError as e:
        logger.error(f"Failed to save prompts file {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error serializing prompts to {filepath}: {e}")
        return False


def create_feedback_placeholder(filepath):
    """Creates a placeholder JSON file for feedback scores."""
    placeholder_data = {"score": None, "reason": "pending"}
    if save_json_file(placeholder_data, filepath):
        logger.info(f"Created feedback placeholder file: {filepath}")
        return True
    else:
        logger.error(f"Failed to create feedback placeholder file: {filepath}")
        return False


# --- Logging and Queueing --- #


def log_release_to_markdown(metadata, release_dir_path):
    """Appends a summary of the release to the markdown log file."""
    log_entry = (
        f"### Release: {metadata.release_id}\n"
        f"- **Artist:** {metadata.artist_name}\n"
        f"- **Date:** {metadata.release_date}\n"
        f"- **Genre:** {metadata.genre or 'N/A'}\n"
        f"- **Track:** {metadata.track_title or 'N/A'}\n"
        f"- **Directory:** `{release_dir_path}`\n"
        f"- **Run ID:** {metadata.generation_run_id}\n"
        f"---\n\n"
    )

    with file_lock:
        try:
            with open(RELEASE_LOG_FILE, "a") as f:
                f.write(log_entry)
            logger.info(
                f"Appended release {metadata.release_id} to log file: {RELEASE_LOG_FILE}"
            )
            return True
        except IOError as e:
            logger.error(
                f"Failed to append to release log file {RELEASE_LOG_FILE}: {e}"
            )
            return False


def add_release_to_queue(metadata, release_dir_path):
    """Adds release information to the JSON queue file."""
    queue_entry = {
        "release_id": metadata.release_id,
        "artist_name": metadata.artist_name,
        "release_directory": str(release_dir_path.resolve()),
        "queued_at": datetime.utcnow().isoformat(),
    }

    with file_lock:
        try:
            queue_data = []
            if (
                os.path.exists(RELEASE_QUEUE_FILE)
                and os.path.getsize(RELEASE_QUEUE_FILE) > 0
            ):
                try:
                    with open(RELEASE_QUEUE_FILE, "r") as f:
                        queue_data = json.load(f)
                    if not isinstance(queue_data, list):
                        logger.warning(
                            f"Queue file {RELEASE_QUEUE_FILE} is not a list. Overwriting."
                        )
                        queue_data = []
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Error decoding queue file {RELEASE_QUEUE_FILE}, will overwrite: {e}"
                    )
                    queue_data = []

            queue_data.append(queue_entry)

            with open(RELEASE_QUEUE_FILE, "w") as f:
                json.dump(queue_data, f, indent=4)
            logger.info(
                f"Added release {metadata.release_id} to queue file: {RELEASE_QUEUE_FILE}"
            )
            return True
        except IOError as e:
            logger.error(
                f"Failed to read/write release queue file {RELEASE_QUEUE_FILE}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error updating queue file {RELEASE_QUEUE_FILE}: {e}"
            )
            return False


def log_learning_entry(metadata, prompts, feedback_file_path):
    """Appends a learning entry to the artist evolution log file."""
    if not EVOLUTION_LOG_FILE:
        logger.warning("EVOLUTION_LOG_FILE not set. Skipping learning log entry.")
        return False

    log_entry = (
        f"## Learning Entry: {datetime.utcnow().isoformat()}\n"
        f"- **Release ID:** {metadata.release_id}\n"
        f"- **Artist ID:** {metadata.artist_id}\n"
        f"- **Artist Name:** {metadata.artist_name}\n"
        f"- **Genre:** {metadata.genre}\n"
        f"- **Generation Run ID:** {metadata.generation_run_id}\n"
        f"- **Suno Prompt:** `{prompts.suno_prompt}`\n"
        f"- **Video Keywords:** `{prompts.video_keywords}`\n"
        f"- **Cover Prompt:** `{prompts.cover_prompt}`\n"
        f"- **Metadata File:** `../output/releases/{Path(metadata.release_id).name}/metadata.json`\n"  # Relative path assumption
        f"- **Prompts File:** `../output/releases/{Path(metadata.release_id).name}/prompts_used.json`\n"
        f"- **Feedback File:** `../output/releases/{Path(metadata.release_id).name}/{Path(feedback_file_path).name}`\n"
        f"---\n\n"
    )

    with file_lock:
        try:
            with open(EVOLUTION_LOG_FILE, "a") as f:
                f.write(log_entry)
            logger.info(
                f"Appended learning entry for release {metadata.release_id} to: {EVOLUTION_LOG_FILE}"
            )
            return True
        except IOError as e:
            logger.error(
                f"Failed to append to evolution log file {EVOLUTION_LOG_FILE}: {e}"
            )
            return False


# --- Main Processing Function --- #


def process_approved_run(run_id):
    """Processes an approved run: gathers assets, creates metadata, logs, and queues."""
    logger.info(f"--- Starting Release Chain for Run ID: {run_id} ---")
    run_status_filepath = Path(RUN_STATUS_DIR) / f"run_{run_id}.json"

    # 1. Load and Validate Run Data
    try:
        if not run_status_filepath.exists():
            logger.error(f"Run status file not found: {run_status_filepath}")
            return False
        with open(run_status_filepath, "r") as f:
            run_data = json.load(f)

        if run_data.get("status") != "approved":
            logger.warning(
                f"Run {run_id} status is not 'approved' ({run_data.get('status')}). Skipping release."
            )
            return False

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding run status file {run_status_filepath}: {e}")
        return False
    except IOError as e:
        logger.error(f"Error reading run status file {run_status_filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading run data for {run_id}: {e}")
        return False

    # 2. Prepare Release Info
    artist_name = run_data.get("artist_name", "Unknown Artist")
    artist_slug = generate_artist_slug(artist_name)
    date_str = datetime.utcnow().strftime(
        "%Y%m%d%H%M%S"
    )  # Added time for more uniqueness
    release_id = f"{artist_slug}_{date_str}_{run_id[:4]}"
    track_url = run_data.get("track_url")
    video_url = run_data.get("video_url")

    # 3. Create Release Directory
    release_dir_path = create_release_directory(artist_slug, date_str)
    if not release_dir_path:
        return False

    # 4. Gather Assets (Placeholders)
    audio_filename = f"{release_id}_audio.mp3"
    video_filename = f"{release_id}_video.mp4"
    cover_filename = f"{release_id}_cover.png"  # Changed to png

    audio_save_path = release_dir_path / "audio" / audio_filename
    video_save_path = release_dir_path / "video" / video_filename
    cover_save_path = release_dir_path / "cover" / cover_filename

    if not track_url or not download_asset(track_url, audio_save_path):
        logger.error(f"Failed to download or save audio asset for run {run_id}.")
        return False
    if not video_url or not download_asset(video_url, video_save_path):
        logger.error(f"Failed to download or save video asset for run {run_id}.")
        return False
    if not generate_cover_art(run_data, cover_save_path):
        logger.error(f"Failed to generate cover art for run {run_id}.")
        return False

    # 5. Analyze Track (Placeholder)
    track_structure = analyze_track_structure(audio_save_path)

    # 6. Get Prompts
    prompts_data = get_prompts_from_run_data(run_data)

    # 7. Create and Save Metadata & Prompts
    metadata = None
    prompts = None
    try:
        metadata = ReleaseMetadata(
            release_id=release_id,
            artist_name=artist_name,
            artist_id=run_data.get("artist_id"),
            genre=run_data.get("genre"),
            release_date=datetime.utcnow().date().isoformat(),
            track_title=f"{artist_name} - Track {run_id[:4]}",
            audio_file=str(Path("audio") / audio_filename),
            video_file=str(Path("video") / video_filename),
            cover_file=str(Path("cover") / cover_filename),
            generation_run_id=run_id,
            track_structure_summary=track_structure,
            visuals_source=run_data.get("video_source", "N/A"),
            llm_summary="Placeholder LLM summary of the track/release.",
        )
        if not save_metadata_file(metadata, release_dir_path / "metadata.json"):
            return False

        prompts = PromptsUsed(
            generation_run_id=run_id,
            suno_prompt=prompts_data.get("suno_prompt"),
            video_keywords=prompts_data.get("video_keywords"),
            cover_prompt=prompts_data.get("cover_prompt"),
            # TODO: Add fields for full prompt chain if available
        )
        if not save_prompts_file(prompts, release_dir_path / "prompts_used.json"):
            return False

    except Exception as e:
        logger.error(f"Error creating or saving metadata/prompts for run {run_id}: {e}")
        return False

    # 8. Create Feedback Placeholder
    feedback_filepath = release_dir_path / "feedback_score.json"
    if not create_feedback_placeholder(feedback_filepath):
        logger.warning(
            f"Failed to create feedback placeholder for {release_id}, but continuing."
        )

    # 9. Log and Queue
    if not log_release_to_markdown(metadata, release_dir_path):
        logger.warning(
            f"Failed to log release {release_id} to markdown, but continuing."
        )
    if not add_release_to_queue(metadata, release_dir_path):
        logger.error(
            f"Failed to add release {release_id} to queue. Release process incomplete."
        )
        return False

    # 10. Log Learning Entry
    if not log_learning_entry(metadata, prompts, feedback_filepath):
        logger.warning(
            f"Failed to log learning entry for release {release_id}, but continuing."
        )

    logger.info(
        f"--- Successfully Completed Release Chain for Run ID: {run_id} -> Release ID: {release_id} ---"
    )
    return True


# --- Example Usage (if run directly) --- #
if __name__ == "__main__":
    logger.info("Running release_chain.py directly for testing.")
    test_run_id = "test_direct_run_phase8"
    dummy_run_data = {
        "run_id": test_run_id,
        "status": "approved",
        "artist_id": 101,
        "artist_name": "Phase Eight Test",
        "genre": "ambient-tech",
        "track_id": "dummy_track_456",
        "track_url": "http://example.com/audio_p8.mp3",
        "video_url": "http://example.com/video_p8.mp4",
        "video_source": "pexels_test",
        "suno_prompt": "An ambient tech track for Phase 8 testing",
        "video_keywords": ["phase8", "test", "ambient"],
        "make_instrumental": False,
    }
    dummy_status_path = Path(RUN_STATUS_DIR) / f"run_{test_run_id}.json"
    try:
        with open(dummy_status_path, "w") as f:
            json.dump(dummy_run_data, f, indent=4)
        logger.info(f"Created dummy run status file: {dummy_status_path}")

        success = process_approved_run(test_run_id)

        if success:
            logger.info(f"Direct test run {test_run_id} processed successfully.")
            date_str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            artist_slug = generate_artist_slug(dummy_run_data["artist_name"])
            release_id = f"{artist_slug}_{date_str}_{test_run_id[:4]}"
            release_dir = Path(RELEASES_DIR) / f"{artist_slug}_{date_str}"
            logger.info(f"Check output in: {release_dir}")
            logger.info(f"Check log: {RELEASE_LOG_FILE}")
            logger.info(f"Check queue: {RELEASE_QUEUE_FILE}")
            logger.info(f"Check evolution log: {EVOLUTION_LOG_FILE}")
        else:
            logger.error(f"Direct test run {test_run_id} failed.")

    except Exception as e:
        logger.critical(f"Error during direct test run: {e}")
    finally:
        if dummy_status_path.exists():
            logger.info(
                f"Kept dummy run status file for inspection: {dummy_status_path}"
            )
        pass
