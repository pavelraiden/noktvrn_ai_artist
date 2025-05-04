#!/usr/bin/env python3

import logging
import os
import sys
import time
import uuid
import json
import asyncio
import random
import requests  # Added for API calls
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
    from llm_orchestrator.orchestrator import (
        LLMOrchestrator,
        LLMOrchestratorError,
    )
    from services.artist_db_service import (
        add_artist,
        get_artist,
        get_all_artists,
        update_artist,
        update_artist_performance_db,
        initialize_database as initialize_artist_db,
    )

    # Import the lifecycle manager
    from services.artist_lifecycle_manager import ArtistLifecycleManager

    # Import the voice service
    from services.voice_service import VoiceService, VoiceServiceError

    # Import the beat service
    from services.beat_service import BeatService

    # Import the lyrics service
    from services.lyrics_service import LyricsService, LyricsServiceError

    # Import the production service
    from services.production_service import (
        ProductionService,
        ProductionServiceError,
    )

    # from services.trend_analysis_service import TrendAnalysisService
except ImportError as e:
    logging.error(
        f"Failed to import core modules, release_chain, orchestrator, "
        f"or services: {e}. Exiting."
    )
    sys.exit(1)

# --- Configuration ---
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "batch_runner.log")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RUN_STATUS_DIR = os.path.join(OUTPUT_DIR, "run_status")
MAX_APPROVAL_WAIT_TIME = int(os.getenv("MAX_APPROVAL_WAIT_TIME", 300))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
REFLECTION_LLM_PRIMARY = os.getenv(
    "REFLECTION_LLM_PRIMARY", "deepseek:deepseek-chat"
)
REFLECTION_LLM_FALLBACKS = os.getenv(
    "REFLECTION_LLM_FALLBACKS", "gemini:gemini-pro"
).split(",")
REFLECTION_MAX_TOKENS = int(os.getenv("REFLECTION_MAX_TOKENS", 500))
REFLECTION_TEMPERATURE = float(os.getenv("REFLECTION_TEMPERATURE", 0.6))
ARTIST_RETIREMENT_THRESHOLD = int(
    os.getenv("RETIREMENT_CONSECUTIVE_REJECTIONS", 5)
)
ARTIST_CREATION_PROBABILITY = float(
    os.getenv("ARTIST_CREATION_PROBABILITY", 0.05)
)
LIFECYCLE_CHECK_INTERVAL_MINUTES = int(
    os.getenv("LIFECYCLE_CHECK_INTERVAL_MINUTES", 60 * 6)
)

# --- API Keys ---
# AIMLAPI_KEY is loaded within BeatService
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
# ELEVENLABS_API_KEY is loaded within VoiceService
# REPLICATE_API_TOKEN is loaded within AltMusicClient (via BeatService)

# --- API Endpoints ---
# AIMLAPI_MUSIC_ENDPOINT is used within BeatService
PEXELS_API_VIDEO_ENDPOINT = "https://api.pexels.com/videos/search"
PIXABAY_API_VIDEO_ENDPOINT = "https://pixabay.com/api/videos/"

# --- Music Model Configuration ---
# MUSIC_MODELS_ORDER is handled within BeatService

# --- A/B Testing Configuration ---
AB_TESTING_ENABLED = os.getenv("AB_TESTING_ENABLED", "False").lower() == "true"
AB_TEST_VARIATIONS = {
    "music_prompt_prefix": [
        "A dreamy {genre} track",
        "An experimental {genre} piece",
        "A high-energy {genre} anthem",
    ]
}
AB_TEST_PARAMETER = "music_prompt_prefix"

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
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Log key configuration status
# API Key warnings are now handled within respective services (BeatService, # VoiceService, etc.)
if not PEXELS_API_KEY:
    logger.warning(
        "PEXELS_API_KEY not found in environment variables. "
        "Pexels video search will fail."
    )
if not PIXABAY_API_KEY:
    logger.warning(
        "PIXABAY_API_KEY not found in environment variables. "
        "Pixabay video search will fail."
    )

logger.info(f"Log level set to: {LOG_LEVEL}")
logger.info(f"Max approval wait time: {MAX_APPROVAL_WAIT_TIME}s")
logger.info(f"Approval poll interval: {POLL_INTERVAL}s")
logger.info(f"Reflection LLM Primary: {REFLECTION_LLM_PRIMARY}")
logger.info(f"Reflection LLM Fallbacks: {REFLECTION_LLM_FALLBACKS}")
# logger.info(f"Music Models Order: {MUSIC_MODELS_ORDER}") # Handled in
# BeatService
logger.info(
    f"Artist Retirement Threshold "
    f"(Consecutive Rejections): {ARTIST_RETIREMENT_THRESHOLD}"
)
logger.info(f"Artist Creation Probability: {ARTIST_CREATION_PROBABILITY}")
logger.info(
    f"Lifecycle Check Interval: {LIFECYCLE_CHECK_INTERVAL_MINUTES} minutes"
)
logger.info(f"A/B Testing Enabled: {AB_TESTING_ENABLED}")
if AB_TESTING_ENABLED:
    logger.info(f"A/B Testing Parameter: {AB_TEST_PARAMETER}")
    logger.info(
        f"A/B Testing Variations: {AB_TEST_VARIATIONS.get(AB_TEST_PARAMETER)}"
    )

# --- Initialize Artist Database ---
try:
    initialize_artist_db()
    if not get_all_artists():
        logger.info(
            "Artist database is empty. "
            "Adding seed artists from file if available."
        )
        seed_file_path = os.path.join(
            PROJECT_ROOT, "data", "artists", "seed_artists.json"
        )
        if os.path.exists(seed_file_path):
            try:
                with open(seed_file_path, "r") as f:
                    seed_artists = json.load(f)
                for artist_data in seed_artists:
                    # Check if artist already exists before adding
                    if not get_artist(artist_data["artist_id"]):
                        added_id = add_artist(artist_data)
                        if added_id:
                            # Corrected f-string
                            logger.info(
                                f"Added seed artist: {artist_data['name']}"
                            )
                            # TODO: Optionally generate voice for seed artists
                            # here?
                        else:
                            # Corrected f-string
                            logger.error(
                                f"Failed to add seed artist "
                                f"{artist_data['name']}"
                            )
                    else:
                        # Corrected f-string
                        logger.info(
                            f"Seed artist {artist_data['name']} "
                            f"already exists, skipping."
                        )
            except (json.JSONDecodeError, IOError) as e:
                logger.error(
                    f"Error reading or parsing seed file {seed_file_path}: "
                    f"{e}. Continuing without seeding."
                )
        else:
            logger.warning(
                f"Seed file {seed_file_path} not found. "
                f"Adding a single default artist."
            )
            default_artist_data = {
                "artist_id": "1",
                "name": "Synthwave Dreamer",
                "genre": "synthwave",
                "style_notes": "Prefers dreamy melodies, moderate tempo, "
                + "avoids harsh sounds.",
                "llm_config": {"model": "default-llm", "temperature": 0.7},
                "created_at": datetime.utcnow().isoformat(),
                "status": "Active",
                "voice_url": None,  # Ensure seed/default artists have this field
            }
            added_id = add_artist(default_artist_data)
            if added_id:
                logger.info(
                    f"Added default artist {default_artist_data['name']}"
                )
                # TODO: Optionally generate voice for default artist here?
            else:
                # Corrected f-string
                logger.error(
                    f"Failed to add default artist "
                    f"{default_artist_data['name']}"
                )
except Exception as e:
    logger.critical(
        f"Failed to initialize or populate artist database: {e}. Exiting."
    )
    sys.exit(1)

# --- Initialize Services ---
try:
    llm_orchestrator = LLMOrchestrator(
        primary_model=REFLECTION_LLM_PRIMARY,
        fallback_models=REFLECTION_LLM_FALLBACKS,
        enable_auto_discovery=False,
    )
except Exception as e:
    logger.error(
        f"Failed to initialize LLM Orchestrator: {e}. "
        f"Reflection/Creation disabled. Exiting."
    )
    llm_orchestrator = None

try:
    lifecycle_manager = ArtistLifecycleManager()
    last_lifecycle_check_time = datetime.min
except Exception as e:
    logger.critical(
        f"Failed to initialize Artist Lifecycle Manager: {e}. Exiting."
    )
    sys.exit(1)

try:
    voice_service = VoiceService()
except Exception as e:
    logger.error(
        f"Failed to initialize Voice Service: {e}. "
        f"Voice generation disabled."
    )
    voice_service = None

try:
    beat_service = BeatService()
except Exception as e:
    logger.error(
        f"Failed to initialize Beat Service:             {e}. Music generation/analysis disabled."
    )
    beat_service = None

try:
    lyrics_service = (
        LyricsService()
    )  # Assumes orchestrator is passed or accessible
except Exception as e:
    logger.error(
        f"Failed to initialize Lyrics Service: {e}. Lyrics generation             disabled."
    )
    lyrics_service = None

try:
    production_service = ProductionService()
except Exception as e:
    logger.error(
        f"Failed to initialize Production Service:             {e}. Audio post-processing disabled."
    )
    production_service = None


def create_new_artist_profile():
    logger.info("Attempting to create a new artist profile...")
    new_id = str(uuid.uuid4())
    artist_name = f"Generated Artist {new_id[:4]}"
    new_artist_data = {
        "artist_id": new_id,
        "name": artist_name,
        "genre": random.choice(
            ["electronic", "ambient", "lofi", "hyperpop", "cinematic"]
        ),
        "style_notes": "Experimental, evolving style. Focus on atmospheric textures.",
        "llm_config": {
            "model": REFLECTION_LLM_PRIMARY,
            "temperature": round(random.uniform(0.5, 0.9), 2),
        },
        "created_at": datetime.utcnow().isoformat(),
        "status": "Candidate",
        "autopilot_enabled": False,
        "voice_url": None,  # Initialize voice_url as None
    }
    added_id = add_artist(new_artist_data)
    if added_id:
        # Corrected f-string
        logger.info(
            f"Successfully created new artist {added_id} ('{artist_name}'). Now                 generating voice sample..."
        )
        if voice_service:
            try:
                sample_text = (
                    f"Hello, I am {artist_name}. This is a sample of my voice."
                )
                voice_url = voice_service.generate_artist_voice(
                    artist_name, sample_text
                )
                if voice_url:
                    logger.info(
                        f"Generated voice sample URL for artist {added_id}:                             {voice_url}"
                    )
                    # Update the artist record with the voice URL
                    update_success = update_artist(
                        added_id, {"voice_url": voice_url}
                    )
                    if update_success:
                        logger.info(
                            f"Successfully saved voice URL for artist                                 {added_id}."
                        )
                    else:
                        logger.error(
                            f"Failed to save voice URL for artist {added_id}."
                        )
                else:
                    logger.error(
                        f"Voice generation failed for artist {added_id}."
                    )
            except VoiceServiceError as e:
                logger.error(
                    f"Error generating voice for artist {added_id}: {e}"
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error during voice generation for artist                         {added_id}: {e}",
                    exc_info=True,
                )
        else:
            logger.warning(
                f"Voice service not available,                     skipping voice generation for artist {added_id}."
            )

        # Return the full artist profile after potential voice update
        return get_artist(added_id)
    else:
        logger.error(
            f"Failed to add newly created artist {new_id} to the database."
        )
        return None


def run_global_lifecycle_check_if_needed():
    global last_lifecycle_check_time
    now = datetime.utcnow()
    if now - last_lifecycle_check_time >= timedelta(
        minutes=LIFECYCLE_CHECK_INTERVAL_MINUTES
    ):
        logger.info("Running global artist lifecycle check...")
        try:
            all_artists = get_all_artists()
            logger.info(
                f"Evaluating lifecycle for {len(all_artists)} artists..."
            )
            for artist in all_artists:
                lifecycle_manager.evaluate_artist_lifecycle(
                    artist["artist_id"]
                )
            last_lifecycle_check_time = now
            logger.info(
                f"Finished lifecycle check. Evaluated {len(all_artists)}                     artists."
            )
        except Exception as e:
            logger.error(
                f"Error during global lifecycle check: {e}", exc_info=True
            )
    else:
        logger.debug("Skipping global lifecycle check (interval not reached).")


def select_next_artist():
    logger.info("Selecting next artist...")
    run_global_lifecycle_check_if_needed()
    active_artists = get_all_artists(status_filter="Active")
    candidate_artists = get_all_artists(status_filter="Candidate")

    selectable_artists = active_artists + candidate_artists

    create_new = random.random() < ARTIST_CREATION_PROBABILITY

    if create_new or not selectable_artists:
        logger.info("Triggering new artist creation...")
        new_artist = create_new_artist_profile()
        if new_artist:
            return new_artist
        else:
            logger.warning(
                "Failed to create a new artist. Proceeding with existing pool."
            )
            selectable_artists = get_all_artists(
                status_filter="Active"
            ) + get_all_artists(status_filter="Candidate")
            if not selectable_artists:
                logger.error(
                    "No active or candidate artists available and failed to                         create a new one. Cannot proceed."
                )
                return None

    if not selectable_artists:
        logger.error("No active or candidate artists found in the database.")
        return None

    # Prioritize candidates, then least recent active artists
    sorted_artists = sorted(
        selectable_artists,
        key=lambda a: (
            a["status"] != "Candidate",
            (
                datetime.fromisoformat(a["last_run_at"])
                if a["last_run_at"]
                else datetime.min
            ),
        ),
    )
    selected_artist = sorted_artists[0]
    # Corrected f-string
    logger.info(
        f"Selected artist {selected_artist['artist_id']}             ('{selected_artist['name']}'), Status: {selected_artist['status']}"
    )
    return selected_artist


def get_adapted_parameters(artist_profile):
    genre = artist_profile.get("genre", "synthwave")
    style_notes = artist_profile.get("style_notes", "standard synthwave")
    ab_test_info = {
        "enabled": False,
        "parameter": None,
        "variation_index": None,
        "variation_value": None,
    }

    base_music_prompt = f"upbeat tempo, inspired by {style_notes}"
    base_params = {
        "music_style": genre,  # Generic style param
        "video_keywords": [genre, "retro", "neon", "dreamy"],
        "make_instrumental": False,  # Note: May not be supported by all models
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
            # Corrected f-string
            logger.info(
                f"A/B Test: Applying variation {chosen_index}                     ('{chosen_variation}') for parameter                     '{AB_TEST_PARAMETER}'."
            )

            if AB_TEST_PARAMETER == "music_prompt_prefix":
                prompt_prefix = chosen_variation.format(genre=genre)
                base_params["music_prompt"] = (
                    f"{prompt_prefix}, {base_music_prompt}"
                )
            else:
                # Corrected f-string
                logger.warning(
                    f"A/B test parameter '{AB_TEST_PARAMETER}' not handled.                         Using default."
                )
                base_params["music_prompt"] = (
                    f"A dreamy {genre} track, {base_music_prompt}"
                )
        else:
            # Corrected f-string
            logger.warning(
                f"A/B testing enabled but no variations defined for                     '{AB_TEST_PARAMETER}'. Using default."
            )
            base_params["music_prompt"] = (
                f"A dreamy {genre} track, {base_music_prompt}"
            )
    else:
        base_params["music_prompt"] = (
            f"A dreamy {genre} track, {base_music_prompt}"
        )

    base_params["ab_test_info"] = ab_test_info
    return base_params


# --- Video Selection (Moved from individual generation functions) --- #
def select_video(video_params):
    """Selects a video using Pexels or Pixabay API with fallback."""
    logger.info(
        f"Selecting video using keywords: {video_params.get('video_keywords')}"
    )
    query = " ".join(video_params.get("video_keywords", ["abstract"]))

    # Try Pexels first
    if PEXELS_API_KEY:
        logger.info("Attempting video search with Pexels...")
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 5, "orientation": "portrait"}
        try:
            response = requests.get(
                PEXELS_API_VIDEO_ENDPOINT,
                headers=headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            results = response.json()
            videos = results.get("videos", [])
            if videos:
                selected_pexels_video = random.choice(videos)
                # Find the highest quality portrait video file URL
                video_files = selected_pexels_video.get("video_files", [])
                best_video_url = None
                max_height = 0
                for vf in video_files:
                    if (
                        vf.get("height")
                        and vf["height"] > max_height
                        and vf.get("link")
                    ):
                        # Basic check for portrait-like aspect ratio if width
                        # available
                        if vf.get("width") and vf["height"] > vf["width"]:
                            max_height = vf["height"]
                            best_video_url = vf["link"]
                        elif not vf.get(
                            "width"
                        ):  # If width unknown, accept based on height
                            max_height = vf["height"]
                            best_video_url = vf["link"]

                if best_video_url:
                    video_id = selected_pexels_video.get("id")
                    logger.info(
                        f"Selected video from Pexels: ID={video_id},                             URL={best_video_url}"
                    )
                    return {
                        "video_id": video_id,
                        "video_url": best_video_url,
                        "source": "Pexels",
                    }
                else:
                    logger.warning(
                        "Found Pexels videos,                             but no suitable portrait video file link."
                    )
            else:
                logger.info("No videos found on Pexels for the query.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels API request failed: {e}")
        except Exception as e:
            logger.error(
                f"Error processing Pexels response: {e}", exc_info=True
            )

    # Fallback to Pixabay
    if PIXABAY_API_KEY:
        logger.info("Attempting video search with Pixabay...")
        params = {
            "key": PIXABAY_API_KEY,
            "q": query,
            "video_type": "film",
            "orientation": "vertical",
            "per_page": 5,
        }
        try:
            response = requests.get(
                PIXABAY_API_VIDEO_ENDPOINT, params=params, timeout=30
            )
            response.raise_for_status()
            results = response.json()
            videos = results.get("hits", [])
            if videos:
                selected_pixabay_video = random.choice(videos)
                # Find the highest quality video URL (assuming portrait)
                video_urls = selected_pixabay_video.get("videos", {})
                best_video_url = None
                max_height = 0
                # Pixabay structure: {"large": {url, w, h}, "medium": {...},                 # ...}
                for quality, details in video_urls.items():
                    if (
                        details.get("height")
                        and details["height"] > max_height
                        and details.get("url")
                    ):
                        max_height = details["height"]
                        best_video_url = details["url"]

                if best_video_url:
                    video_id = selected_pixabay_video.get("id")
                    logger.info(
                        f"Selected video from Pixabay: ID={video_id},                             URL={best_video_url}"
                    )
                    return {
                        "video_id": video_id,
                        "video_url": best_video_url,
                        "source": "Pixabay",
                    }
                else:
                    logger.warning(
                        "Found Pixabay videos, but no suitable video file                             link."
                    )
            else:
                logger.info("No videos found on Pixabay for the query.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Pixabay API request failed: {e}")
        except Exception as e:
            logger.error(
                f"Error processing Pixabay response: {e}", exc_info=True
            )

    logger.error("Failed to select a video from any source.")
    return None


# --- Run Status Management --- #
def save_run_status(run_id, status, data=None):
    """Saves the status of a run to a JSON file."""
    filepath = os.path.join(RUN_STATUS_DIR, f"{run_id}.json")
    try:
        status_data = {
            "run_id": run_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if data:
            status_data.update(data)
        with open(filepath, "w") as f:
            json.dump(status_data, f, indent=2)
        # Corrected f-string
        logger.debug(
            f"Saved run status '{status}' for run {run_id} to {filepath}"
        )
    except IOError as e:
        logger.error(f"Failed to save run status for {run_id}: {e}")


def load_run_status(run_id):
    """Loads the status of a run from its JSON file."""
    filepath = os.path.join(RUN_STATUS_DIR, f"{run_id}.json")
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        else:
            return None
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load run status for {run_id}: {e}")
        return None


def delete_run_status_file(run_id):
    """Deletes the status file for a completed or aborted run."""
    filepath = os.path.join(RUN_STATUS_DIR, f"{run_id}.json")
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted run status file for {run_id}.")
    except OSError as e:
        logger.error(f"Failed to delete run status file for {run_id}: {e}")


# --- Approval Workflow --- #
async def wait_for_approval(run_id, timeout):
    """Waits for the approval status file to indicate approval or rejection."""
    start_time = time.time()
    logger.info(
        f"Waiting for approval for run {run_id} (timeout: {timeout}s)..."
    )
    while time.time() - start_time < timeout:
        status_data = load_run_status(run_id)
        if status_data:
            status = status_data.get("status")
            if status == "approved":
                logger.info(f"Run {run_id} approved.")
                return "approved", status_data
            elif status == "rejected":
                logger.info(f"Run {run_id} rejected.")
                return "rejected", status_data
            elif status == "pending_approval":
                # Still waiting
                pass
            else:
                logger.warning(
                    f"Run {run_id} found with unexpected status:                         {status}. Assuming rejection."
                )
                return (
                    "rejected",
                    status_data,
                )  # Treat unexpected status as rejection
        else:
            # Status file might not exist yet or failed to load
            logger.debug(
                f"Run status file for {run_id} not found or invalid. Still                     waiting..."
            )

        await asyncio.sleep(POLL_INTERVAL)

    logger.warning(
        f"Timeout waiting for approval for run {run_id}. Assuming rejection."
    )
    return "rejected", None  # Timeout is treated as rejection


# --- Reflection and Adaptation --- #
def reflect_on_run(artist_profile, run_data, outcome):
    """Uses LLM to reflect on the run and suggest improvements for the artist
    profile."""
    # Corrected f-string
    logger.info(
        f"Reflecting on run {run_data.get('run_id')} for artist             {artist_profile.get('artist_id')} ('{artist_profile.get('name')}').             Outcome: {outcome}"
    )
    if not llm_orchestrator:
        logger.error(
            "LLM Orchestrator not available. Cannot perform reflection."
        )
        return None

    # Prepare context for the LLM
    # Corrected multi-line f-string with single quotes for .get()
    context = f"""Artist Profile:
Name: {artist_profile.get('name')}
Genre: {artist_profile.get('genre')}
Style Notes: {artist_profile.get('style_notes')}
LLM Config: {json.dumps(artist_profile.get('llm_config', {}))}
Status: {artist_profile.get('status')}
Consecutive Rejections: {artist_profile.get('consecutive_rejections', 0)}
Performance History (last 5):
    {json.dumps(artist_profile.get('performance_history', [])[-5:], indent=2)}
Voice URL: {artist_profile.get('voice_url', 'N/A')}

Run Details:
Run ID: {run_data.get('run_id')}
Parameters Used: {json.dumps(run_data.get('parameters_used', {}), indent=2)}
Generated Track URL: {run_data.get('track_url')}
Track Model Used: {run_data.get('track_model_used', 'N/A')}
Track Tempo (BPM): {run_data.get('tempo', 'N/A')}
Track Duration (s): {run_data.get('duration', 'N/A')}
Generated Lyrics:
{run_data.get('lyrics', 'N/A')[:200]}...
Selected Video URL: {run_data.get('video_url')}
Video Source: {run_data.get('video_source', 'N/A')}
Processed Audio URL: {run_data.get('processed_audio_url', 'N/A')}
Outcome: {outcome}

Task: Based on the artist profile and the details of the latest run,     suggest specific, actionable modifications to the artist's 'style_notes' or
    'llm_config' (like temperature or prompt adjustments) to improve future outcomes. Aim for subtle changes. If the outcome was 'approved', suggest refinements to maintain success or explore slight variations. If 'rejected', suggest changes to address potential reasons for rejection (e.g., if lyrics were generic, suggest adding more specific themes to style_notes; if music was poor, suggest adjusting style notes related to instrumentation or mood). Provide the suggestions ONLY as a JSON object with keys 'style_notes' and/or 'llm_config'. Example: {{"style_notes": "Maintain dreamy synthwave but add more prominent basslines."}} or {{"llm_config": {{"temperature": 0.65}}}}
"""

    try:
        response = llm_orchestrator.generate_text(
            prompt=context,
            model_name=REFLECTION_LLM_PRIMARY,
            max_tokens=REFLECTION_MAX_TOKENS,
            temperature=REFLECTION_TEMPERATURE,
            response_format={"type": "json_object"},
        )
        # Ensure response is stripped before potential logging in except block
        response_content = response.strip()
        suggestions = json.loads(response_content)
        logger.info(f"Reflection suggestions received: {suggestions}")
        return suggestions
    except LLMOrchestratorError as e:
        logger.error(f"LLM reflection failed: {e}")
        return None
    except json.JSONDecodeError as e:
        # Use response_content which is guaranteed to exist if json.loads fails
        logger.error(
            f"Failed to parse JSON reflection suggestions: {e}. Raw response: {response_content}"
        )
        return None
    except Exception as e:
        logger.error(f"Unexpected error during reflection: {e}", exc_info=True)
        return None


def apply_reflection_suggestions(artist_id, suggestions):
    """Applies the reflection suggestions to the artist profile in the
    database."""
    if not suggestions or not isinstance(suggestions, dict):
        logger.warning("No valid reflection suggestions to apply.")
        return False

    update_payload = {}
    if "style_notes" in suggestions and isinstance(
        suggestions["style_notes"], str
    ):
        update_payload["style_notes"] = suggestions["style_notes"]

    if "llm_config" in suggestions and isinstance(
        suggestions["llm_config"], dict
    ):
        # Merge suggestions with existing config to avoid overwriting other
        # keys
        current_artist = get_artist(artist_id)
        if current_artist:
            current_config = current_artist.get("llm_config", {})
            current_config.update(suggestions["llm_config"])
            update_payload["llm_config"] = current_config
        else:
            logger.warning(
                f"Cannot apply LLM config suggestions:                     Artist {artist_id} not found."
            )

    if not update_payload:
        # Corrected f-string
        logger.info(
            "Reflection suggestions did not contain valid fields to update (",
            "'style_notes' or 'llm_config').",
        )
        return False

    logger.info(
        f"Applying reflection suggestions to artist {artist_id}:             {update_payload}"
    )
    success = update_artist(artist_id, update_payload)
    if success:
        logger.info(
            f"Successfully applied reflection suggestions for artist                 {artist_id}."
        )
    else:
        logger.error(
            f"Failed to apply reflection suggestions for artist {artist_id}."
        )
    return success


# --- Main Pipeline --- #
async def run_artist_pipeline(artist_profile):
    """Runs the full generation pipeline for a single artist."""
    run_id = str(uuid.uuid4())
    artist_id = artist_profile["artist_id"]
    artist_name = artist_profile["name"]
    # Corrected f-string
    logger.info(
        f"--- Starting pipeline run {run_id} for artist {artist_id} ('{artist_name}') ---"
    )
    save_run_status(
        run_id, "started", {"artist_id": artist_id, "artist_name": artist_name}
    )

    run_data = {
        "run_id": run_id,
        "artist_id": artist_id,
        "artist_name": artist_name,
        "start_time": datetime.utcnow().isoformat(),
        "parameters_used": {},
        "track_id": None,
        "track_url": None,
        "track_model_used": None,
        "tempo": None,
        "duration": None,
        "lyrics": None,
        "video_id": None,
        "video_url": None,
        "video_source": None,
        "processed_audio_url": None,  # Added for humanized audio
        "telegram_message_id": None,
        "status": "running",
        "end_time": None,
        "outcome": None,  # approved, rejected, error, etc.
    }

    try:
        # 1. Get Adapted Parameters (including A/B testing)
        logger.info("Step 1: Adapting parameters...")
        params = get_adapted_parameters(artist_profile)
        run_data["parameters_used"] = params
        save_run_status(run_id, "parameters_adapted", {"parameters": params})
        logger.info(f"Adapted parameters: {params}")

        # 2. Generate & Analyze Track (using BeatService)
        logger.info("Step 2: Generating and analyzing track...")
        if not beat_service:
            raise Exception("Beat Service not initialized.")

        track_analysis_info = beat_service.generate_and_analyze_beat(
            params.get("music_prompt", "default prompt")
        )
        if not track_analysis_info or not track_analysis_info.get("track_url"):
            logger.error("Track generation or analysis failed.")
            run_data["status"] = "failed"
            run_data["outcome"] = "generation_failed_track"
            raise Exception("Track generation or analysis failed")

        run_data.update(
            {
                "track_id": track_analysis_info.get("track_id"),
                "track_url": track_analysis_info.get("track_url"),
                "track_model_used": track_analysis_info.get("model_used"),
                "tempo": track_analysis_info.get("tempo"),
                "duration": track_analysis_info.get("duration"),
            }
        )
        save_run_status(
            run_id,
            "track_generated_analyzed",
            {
                "track_url": run_data["track_url"],
                "track_model": run_data["track_model_used"],
                "tempo": run_data["tempo"],
                "duration": run_data["duration"],
            },
        )
        # Corrected f-string
        logger.info(
            f"Track generated: {run_data['track_url']} (Tempo:                 {run_data['tempo']:.2f}, Duration:                 {run_data['duration']:.2f}s)"
        )

        # 3. Generate Lyrics (using LyricsService)
        logger.info("Step 3: Generating lyrics...")
        if not lyrics_service:
            logger.warning(
                "Lyrics Service not initialized. Proceeding without lyrics."
            )
            run_data["lyrics"] = "(Lyrics service unavailable)"
        else:
            try:
                lyrics = lyrics_service.generate_lyrics(
                    base_prompt=params.get(
                        "music_prompt", "synthwave dreams"
                    ),  # Use music prompt as theme
                    genre=artist_profile.get("genre", "electronic"),
                    style_notes=artist_profile.get("style_notes", ""),
                    llm_config=artist_profile.get("llm_config", {}),
                    tempo=run_data["tempo"],
                    duration=run_data["duration"],
                )
                if not lyrics:
                    logger.warning(
                        "Lyrics generation failed or returned empty. Proceeding                             without lyrics."
                    )
                    run_data["lyrics"] = "(Lyrics generation failed)"
                else:
                    run_data["lyrics"] = lyrics
                    logger.info("Lyrics generated.")
            except LyricsServiceError as e:
                logger.error(f"Lyrics generation failed: {e}")
                run_data["lyrics"] = "(Lyrics generation error)"

        save_run_status(
            run_id,
            "lyrics_generated",
            {
                "lyrics_preview": (
                    run_data["lyrics"][:100] if run_data["lyrics"] else "N/A"
                )
            },
        )

        # 4. Select Video
        logger.info("Step 4: Selecting video...")
        video_info = select_video(params)
        if not video_info or not video_info.get("video_url"):
            # Non-critical? Decide if we proceed without video or fail.
            logger.warning("Video selection failed. Proceeding without video.")
            run_data["video_url"] = None
            run_data["video_source"] = None
            # run_data["status"] = "failed"
            # run_data["outcome"] = "selection_failed_video"
            # raise Exception("Video selection failed")
        else:
            run_data.update(
                {
                    "video_id": video_info.get("video_id"),
                    "video_url": video_info.get("video_url"),
                    "video_source": video_info.get("source"),
                }
            )
            # Corrected f-string
            logger.info(
                f"Video selected: {run_data['video_url']} (Source:                     {run_data['video_source']}) "
            )

        save_run_status(
            run_id,
            "video_selected",
            {
                "video_url": run_data["video_url"],
                "video_source": run_data["video_source"],
            },
        )

        # 5. Post-Process Audio (Humanization)
        logger.info("Step 5: Post-processing audio...")
        if not production_service:
            logger.warning(
                "Production Service not initialized. Skipping audio                     post-processing."
            )
        elif not run_data["track_url"]:
            logger.warning(
                "No track URL available. Skipping audio post-processing."
            )
        else:
            try:
                processed_audio_url = production_service.humanize_audio(
                    run_data["track_url"]
                )
                if processed_audio_url:
                    run_data["processed_audio_url"] = processed_audio_url
                    logger.info(
                        f"Audio post-processing complete:                             {processed_audio_url}"
                    )
                else:
                    logger.warning(
                        "Audio post-processing failed. Using original audio                             URL."
                    )
            except ProductionServiceError as e:
                logger.error(f"Audio post-processing failed: {e}")

        save_run_status(
            run_id,
            "audio_processed",
            {"processed_audio_url": run_data["processed_audio_url"]},
        )

        # 6. Send Preview for Approval (if Telegram configured)
        logger.info("Step 6: Sending preview for approval...")
        # Use processed audio if available, otherwise original
        preview_audio_url = (
            run_data["processed_audio_url"] or run_data["track_url"]
        )
        telegram_message_id = send_preview_to_telegram(
            run_id, run_data, preview_audio_url
        )

        if telegram_message_id:
            run_data["telegram_message_id"] = telegram_message_id
            save_run_status(
                run_id,
                "pending_approval",
                {"telegram_message_id": telegram_message_id},
            )
            logger.info(
                f"Preview sent to Telegram (Message ID:                     {telegram_message_id}). Waiting for approval..."
            )

            # 7. Wait for Approval
            approval_status, approval_data = await wait_for_approval(
                run_id, MAX_APPROVAL_WAIT_TIME
            )
            run_data["outcome"] = approval_status  # 'approved' or 'rejected'
            logger.info(f"Approval outcome: {approval_status}")

        else:
            logger.warning(
                "Telegram service not configured or failed to send preview.                     Skipping approval step and assuming rejection."
            )
            run_data["outcome"] = (
                "rejected"  # Treat as rejected if preview fails        # 8. Process based on outcome
            )
        # Corrected f-string
        outcome_str = run_data["outcome"]
        logger.info(f"Step 8: Processing outcome 	'{outcome_str}	'...")
        if run_data["outcome"] == "approved":
            logger.info(
                f"Run {run_id} approved. Proceeding to release chain..."
            )
            # Add run_data to the approval_data before processing
            if approval_data:
                approval_data["run_details"] = run_data
            else:
                # If timeout occurred but somehow status was approved
                # (unlikely), create basic data
                approval_data = {
                    "run_id": run_id,
                    "status": "approved",
                    "run_details": run_data,
                }
            process_approved_run(
                approval_data
            )  # Pass the approval data (which includes run_data)
            run_data["status"] = "completed"
        else:  # Rejected or timeout
            logger.info(
                f"Run {run_id} rejected or timed out. Skipping release."
            )
            run_data["status"] = "rejected"

        # 9. Update Artist Performance in DB
        logger.info("Step 9: Updating artist performance...")
        update_artist_performance_db(
            artist_id=artist_id,
            run_id=run_id,
            status=run_data["outcome"],  # Use the final outcome
            retirement_threshold=ARTIST_RETIREMENT_THRESHOLD,
        )

        # 10. Reflect on Run (if LLM available)
        if llm_orchestrator:
            logger.info("Step 10: Reflecting on run...")
            suggestions = reflect_on_run(
                artist_profile, run_data, run_data["outcome"]
            )
            if suggestions:
                apply_reflection_suggestions(artist_id, suggestions)
            else:
                logger.warning("Reflection did not produce valid suggestions.")
        else:
            logger.info(
                "Skipping reflection step (LLM Orchestrator not available)."
            )

    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}", exc_info=True)
        run_data["status"] = "failed"
        # If outcome wasn't set before error
        if not run_data["outcome"]:
            run_data["outcome"] = "error"
        # Attempt to update performance even on error
        try:
            update_artist_performance_db(
                artist_id=artist_id,
                run_id=run_id,
                status=run_data["outcome"],
                retirement_threshold=ARTIST_RETIREMENT_THRESHOLD,
            )
        except Exception as db_err:
            logger.error(
                f"Failed to update artist performance after error for run                     {run_id}: {db_err}"
            )

    finally:
        run_data["end_time"] = datetime.utcnow().isoformat()
        # Corrected f-string
        logger.info(
            f"--- Finished pipeline run {run_id} for artist {artist_id}. Final                 Status: {run_data['status']}, Outcome:                 {run_data['outcome']} ---"
        )
        # Save final status and clean up status file
        save_run_status(run_id, run_data["status"], run_data)
        # Optionally keep status files for rejected/failed runs for debugging
        if run_data["status"] == "completed":
            delete_run_status_file(run_id)
        # Log the full run data for debugging
        logger.debug(
            f"Full run data for {run_id}: {json.dumps(run_data, indent=2)}"
        )


async def main():
    logger.info("Starting AI Artist Batch Runner...")
    while True:
        try:
            artist = select_next_artist()
            if artist:
                await run_artist_pipeline(artist)
            else:
                logger.warning("No artist selected. Waiting before retry...")
                await asyncio.sleep(60)  # Wait a minute if no artist found

            # Add a short delay between runs
            await asyncio.sleep(5)

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down...")
            break
        except Exception as e:
            logger.critical(
                f"Unhandled exception in main loop: {e}", exc_info=True
            )
            logger.info("Restarting main loop after a delay...")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
