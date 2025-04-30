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
        logging.error(f"Failed to import schemas: {e}. Ensure schemas.py is accessible.")
        sys.exit(1)

# --- Configuration ---
LOG_LEVEL = os.getenv("RELEASE_CHAIN_LOG_LEVEL", "INFO").upper()
OUTPUT_BASE_DIR = os.getenv("OUTPUT_BASE_DIR", os.path.join(PROJECT_ROOT, "output"))
RELEASES_DIR = os.getenv("RELEASES_DIR", os.path.join(OUTPUT_BASE_DIR, "releases"))
RUN_STATUS_DIR = os.getenv("RUN_STATUS_DIR", os.path.join(OUTPUT_BASE_DIR, "run_status"))
RELEASE_LOG_FILE = os.getenv("RELEASE_LOG_FILE", os.path.join(OUTPUT_BASE_DIR, "release_log.md"))
RELEASE_QUEUE_FILE = os.getenv("RELEASE_QUEUE_FILE", os.path.join(OUTPUT_BASE_DIR, "release_queue.json"))

# Ensure directories exist
os.makedirs(RELEASES_DIR, exist_ok=True)
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
        logging.StreamHandler(sys.stdout) # Add file handler if needed
    ]
)
logger = logging.getLogger(__name__)

# --- File Lock for Concurrent Writes --- #
file_lock = threading.Lock()

# --- Helper Functions --- #

def generate_artist_slug(artist_name):
    """Generates a filesystem-safe slug from the artist name."""
    if not artist_name:
        return "unknown_artist"
    # Remove special characters, replace spaces with underscores, lowercase
    slug = ".join(c for c in artist_name if c.isalnum() or c.isspace())
    slug = slug.strip().replace(" ", "_").lower()
    # Ensure slug is not empty after cleaning
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
    logger.info(f"Simulating cover art generation for artist {artist_info.get(\"name\")} to {save_path}")
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(f"Placeholder cover art for {artist_info.get(\"name\")}\n")
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
    return {
        "suno_prompt": run_data.get("suno_prompt", "N/A"),
        "video_keywords": run_data.get("video_keywords", []), # Assuming keywords are a list
        "cover_prompt": "Placeholder cover prompt based on genre/mood" # Placeholder
    }

# --- Metadata and File Saving --- #

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

# --- Logging and Queueing --- #

def log_release_to_markdown(metadata, release_dir_path):
    """Appends a summary of the release to the markdown log file."""
    log_entry = (
        f"### Release: {metadata.release_id}\n"
        f"- **Artist:** {metadata.artist_name}\n"
        f"- **Date:** {metadata.release_date}\n"
        f"- **Genre:** {metadata.genre or \"N/A\"}\n"
        f"- **Track:** {metadata.track_title or \"N/A\"}\n"
        f"- **Directory:** `{release_dir_path}`\n"
        f"- **Run ID:** {metadata.generation_run_id}\n"
        f"---\n\n"
    )
    
    with file_lock: # Ensure only one thread/process writes at a time
        try:
            with open(RELEASE_LOG_FILE, "a") as f:
                f.write(log_entry)
            logger.info(f"Appended release {metadata.release_id} to log file: {RELEASE_LOG_FILE}")
            return True
        except IOError as e:
            logger.error(f"Failed to append to release log file {RELEASE_LOG_FILE}: {e}")
            return False

def add_release_to_queue(metadata, release_dir_path):
    """Adds release information to the JSON queue file."""
    queue_entry = {
        "release_id": metadata.release_id,
        "artist_name": metadata.artist_name,
        "release_directory": str(release_dir_path.resolve()), # Store absolute path
        "queued_at": datetime.utcnow().isoformat()
    }
    
    with file_lock:
        try:
            queue_data = []
            if os.path.exists(RELEASE_QUEUE_FILE) and os.path.getsize(RELEASE_QUEUE_FILE) > 0:
                try:
                    with open(RELEASE_QUEUE_FILE, "r") as f:
                        queue_data = json.load(f)
                    if not isinstance(queue_data, list):
                        logger.warning(f"Queue file {RELEASE_QUEUE_FILE} is not a list. Overwriting.")
                        queue_data = []
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding queue file {RELEASE_QUEUE_FILE}, will overwrite: {e}")
                    queue_data = []
            
            queue_data.append(queue_entry)
            
            with open(RELEASE_QUEUE_FILE, "w") as f:
                json.dump(queue_data, f, indent=4)
            logger.info(f"Added release {metadata.release_id} to queue file: {RELEASE_QUEUE_FILE}")
            return True
        except IOError as e:
            logger.error(f"Failed to read/write release queue file {RELEASE_QUEUE_FILE}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating queue file {RELEASE_QUEUE_FILE}: {e}")
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
            logger.warning(f"Run {run_id} status is not \"approved\" ({run_data.get(\"status\")}). Skipping release.")
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
    date_str = datetime.utcnow().strftime("%Y%m%d")
    release_id = f"{artist_slug}_{date_str}_{run_id[:4]}" # Unique ID for the release
    track_url = run_data.get("track_url")
    video_url = run_data.get("video_url")

    # 3. Create Release Directory
    release_dir_path = create_release_directory(artist_slug, date_str)
    if not release_dir_path:
        return False # Error already logged

    # 4. Gather Assets (Placeholders)
    audio_filename = f"{release_id}_audio.mp3" # Example filename
    video_filename = f"{release_id}_video.mp4"
    cover_filename = f"{release_id}_cover.jpg"
    
    audio_save_path = release_dir_path / "audio" / audio_filename
    video_save_path = release_dir_path / "video" / video_filename
    cover_save_path = release_dir_path / "cover" / cover_filename

    if not track_url or not download_asset(track_url, audio_save_path):
        logger.error(f"Failed to download or save audio asset for run {run_id}.")
        # Consider cleanup? For now, just fail.
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

    # 7. Create and Save Metadata
    try:
        metadata = ReleaseMetadata(
            release_id=release_id,
            artist_name=artist_name,
            artist_id=run_data.get("artist_id"),
            genre=run_data.get("genre"),
            release_date=datetime.utcnow().date(),
            track_title=f"{artist_name} - Track {run_id[:4]}", # Placeholder title
            audio_file=str(Path("audio") / audio_filename), # Relative path within release dir
            video_file=str(Path("video") / video_filename),
            cover_file=str(Path("cover") / cover_filename),
            generation_run_id=run_id,
            track_structure_summary=track_structure,
            visuals_source=run_data.get("video_source", "N/A"),
            llm_summary="Placeholder LLM summary of the track/release." # Placeholder
        )
        if not save_metadata_file(metadata, release_dir_path / "metadata.json"):
            return False

        prompts = PromptsUsed(
            generation_run_id=run_id,
            suno_prompt=prompts_data.get("suno_prompt"),
            video_keywords=prompts_data.get("video_keywords"),
            cover_prompt=prompts_data.get("cover_prompt")
        )
        if not save_prompts_file(prompts, release_dir_path / "prompts_used.json"):
            return False
            
    except Exception as e: # Catch potential Pydantic validation errors too
        logger.error(f"Error creating or saving metadata/prompts for run {run_id}: {e}")
        return False

    # 8. Log and Queue
    if not log_release_to_markdown(metadata, release_dir_path):
        logger.warning(f"Failed to log release {release_id} to markdown, but continuing.")
    if not add_release_to_queue(metadata, release_dir_path):
        logger.error(f"Failed to add release {release_id} to queue. Release process incomplete.")
        return False

    logger.info(f"--- Successfully Completed Release Chain for Run ID: {run_id} -> Release ID: {release_id} ---")
    return True

# --- Example Usage (if run directly) --- #
if __name__ == "__main__":
    logger.info("Running release_chain.py directly for testing.")
    # Create a dummy approved run file for testing
    test_run_id = "test_direct_run"
    dummy_run_data = {
        "run_id": test_run_id,
        "status": "approved",
        "artist_id": 99,
        "artist_name": "Direct Test Artist",
        "genre": "test-pop",
        "track_id": "dummy_track_123",
        "track_url": "http://example.com/audio.mp3",
        "video_url": "http://example.com/video.mp4",
        "video_source": "test_source",
        "suno_prompt": "A test pop track",
        "video_keywords": ["test", "pop"],
        "make_instrumental": False
    }
    dummy_status_path = Path(RUN_STATUS_DIR) / f"run_{test_run_id}.json"
    try:
        with open(dummy_status_path, "w") as f:
            json.dump(dummy_run_data, f, indent=4)
        logger.info(f"Created dummy run status file: {dummy_status_path}")
        
        # Process the dummy run
        success = process_approved_run(test_run_id)
        
        if success:
            logger.info(f"Direct test run {test_run_id} processed successfully.")
            # Verify output files exist (optional)
            date_str = datetime.utcnow().strftime("%Y%m%d")
            artist_slug = generate_artist_slug(dummy_run_data["artist_name"])
            release_dir = Path(RELEASES_DIR) / f"{artist_slug}_{date_str}"
            logger.info(f"Check output in: {release_dir}")
            logger.info(f"Check log: {RELEASE_LOG_FILE}")
            logger.info(f"Check queue: {RELEASE_QUEUE_FILE}")
        else:
            logger.error(f"Direct test run {test_run_id} failed.")
            
    except Exception as e:
        logger.critical(f"Error during direct test run: {e}")
    finally:
        # Clean up dummy file
        if dummy_status_path.exists():
            # os.remove(dummy_status_path)
            logger.info(f"Kept dummy run status file for inspection: {dummy_status_path}")
        pass

