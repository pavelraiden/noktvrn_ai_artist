#!/usr/bin/env python3

import logging
import os
import sys
import time
import uuid
import json
import asyncio
import random
import requests # Added for API calls
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
ARTIST_RETIREMENT_THRESHOLD = int(os.getenv("RETIREMENT_CONSECUTIVE_REJECTIONS", 5))
ARTIST_CREATION_PROBABILITY = float(os.getenv("ARTIST_CREATION_PROBABILITY", 0.05))
LIFECYCLE_CHECK_INTERVAL_MINUTES = int(os.getenv("LIFECYCLE_CHECK_INTERVAL_MINUTES", 60 * 6))

# --- API Keys ---
# FIX: Use SUNO_API_KEY as fallback for AIMLAPI_KEY
AIMLAPI_KEY = os.getenv("AIMLAPI_KEY") or os.getenv("SUNO_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# --- API Endpoints ---
AIMLAPI_MUSIC_ENDPOINT = "https://api.aimlapi.com/v2/generate/audio" # v2 endpoint for music
PEXELS_API_VIDEO_ENDPOINT = "https://api.pexels.com/videos/search"
PIXABAY_API_VIDEO_ENDPOINT = "https://pixabay.com/api/videos/"

# --- Music Model Configuration ---
MUSIC_MODEL_PRIMARY = os.getenv("MUSIC_MODEL_PRIMARY", "stable-audio")
MUSIC_MODEL_FALLBACKS_STR = os.getenv("MUSIC_MODEL_FALLBACKS", "minimax-music,music-01")
MUSIC_MODEL_FALLBACKS = [m.strip() for m in MUSIC_MODEL_FALLBACKS_STR.split(",") if m.strip()]
MUSIC_MODELS_ORDER = [MUSIC_MODEL_PRIMARY] + MUSIC_MODEL_FALLBACKS

# --- A/B Testing Configuration ---
AB_TESTING_ENABLED = os.getenv("AB_TESTING_ENABLED", "False").lower() == "true"
AB_TEST_VARIATIONS = {
    "music_prompt_prefix": [
        "A dreamy {genre} track",
        "An experimental {genre} piece",
        "A high-energy {genre} anthem"
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
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Log key configuration status
if not AIMLAPI_KEY:
    logger.warning("AIMLAPI_KEY (or SUNO_API_KEY) not found in environment variables. Music generation will fail.")
if not PEXELS_API_KEY:
    logger.warning("PEXELS_API_KEY not found in environment variables. Pexels video search will fail.")
if not PIXABAY_API_KEY:
    logger.warning("PIXABAY_API_KEY not found in environment variables. Pixabay video search will fail.")

logger.info(f"Log level set to: {LOG_LEVEL}")
logger.info(f"Max approval wait time: {MAX_APPROVAL_WAIT_TIME}s")
logger.info(f"Approval poll interval: {POLL_INTERVAL}s")
logger.info(f"Reflection LLM Primary: {REFLECTION_LLM_PRIMARY}")
logger.info(f"Reflection LLM Fallbacks: {REFLECTION_LLM_FALLBACKS}")
logger.info(f"Music Models Order: {MUSIC_MODELS_ORDER}")
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
        logger.info("Artist database is empty. Adding seed artists from file if available.")
        seed_file_path = os.path.join(PROJECT_ROOT, "data", "artists", "seed_artists.json")
        if os.path.exists(seed_file_path):
            try:
                with open(seed_file_path, "r") as f:
                    seed_artists = json.load(f)
                for artist_data in seed_artists:
                    # Check if artist already exists before adding
                    if not get_artist(artist_data["artist_id"]):
                        add_artist(artist_data)
                        logger.info(f"Added seed artist: {artist_data['name']}")
                    else:
                        logger.info(f"Seed artist {artist_data['name']} already exists, skipping.")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading or parsing seed file {seed_file_path}: {e}. Continuing without seeding.")
        else:
            logger.warning(f"Seed file {seed_file_path} not found. Adding a single default artist.")
            default_artist_data = {
                "artist_id": "1",
                "name": "Synthwave Dreamer",
                "genre": "synthwave",
                "style_notes": "Prefers dreamy melodies, moderate tempo, avoids harsh sounds.",
                "llm_config": {"model": "default-llm", "temperature": 0.7},
                "created_at": datetime.utcnow().isoformat(),
                "status": "Active"
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
    last_lifecycle_check_time = datetime.min
except Exception as e:
    logger.critical(f"Failed to initialize Artist Lifecycle Manager: {e}. Exiting.")
    sys.exit(1)

def create_new_artist_profile():
    logger.info("Attempting to create a new artist profile...")
    new_id = str(uuid.uuid4())
    new_artist_data = {
        "artist_id": new_id,
        "name": f"Generated Artist {new_id[:4]}",
        "genre": random.choice(["electronic", "ambient", "lofi", "hyperpop", "cinematic"]),
        "style_notes": "Experimental, evolving style. Focus on atmospheric textures.",
        "llm_config": {"model": REFLECTION_LLM_PRIMARY, "temperature": round(random.uniform(0.5, 0.9), 2)},
        "created_at": datetime.utcnow().isoformat(),
        "status": "Candidate",
        "autopilot_enabled": False
    }
    added_id = add_artist(new_artist_data)
    if added_id:
        logger.info(f"Successfully created new artist {new_artist_data['artist_id']}. Selecting it (will run as Candidate).")
        return get_artist(added_id)
    else:
        logger.error(f"Failed to add newly created artist {new_id} to the database.")
        return None

def run_global_lifecycle_check_if_needed():
    global last_lifecycle_check_time
    now = datetime.utcnow()
    if now - last_lifecycle_check_time >= timedelta(minutes=LIFECYCLE_CHECK_INTERVAL_MINUTES):
        logger.info("Running global artist lifecycle check...")
        try:
            all_artists = get_all_artists()
            logger.info(f"Evaluating lifecycle for {len(all_artists)} artists...")
            for artist in all_artists:
                lifecycle_manager.evaluate_artist_lifecycle(artist["artist_id"])
            last_lifecycle_check_time = now
            logger.info(f"Finished lifecycle check. Evaluated {len(all_artists)} artists.")
        except Exception as e:
            logger.error(f"Error during global lifecycle check: {e}", exc_info=True)
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
            logger.warning("Failed to create a new artist. Proceeding with existing pool.")
            selectable_artists = get_all_artists(status_filter="Active") + get_all_artists(status_filter="Candidate")
            if not selectable_artists:
                 logger.error("No active or candidate artists available and failed to create a new one. Cannot proceed.")
                 return None

    if not selectable_artists:
        logger.error("No active or candidate artists found in the database.")
        return None

    # Prioritize candidates, then least recent active artists
    sorted_artists = sorted(
        selectable_artists,
        key=lambda a: (a["status"] != "Candidate", datetime.fromisoformat(a["last_run_at"]) if a["last_run_at"] else datetime.min)
    )
    selected_artist = sorted_artists[0]
    logger.info(f"Selected artist {selected_artist['artist_id']} ({selected_artist['name']}), Status: {selected_artist['status']}")
    return selected_artist

def get_adapted_parameters(artist_profile):
    genre = artist_profile.get("genre", "synthwave")
    style_notes = artist_profile.get("style_notes", "standard synthwave")
    ab_test_info = {"enabled": False, "parameter": None, "variation_index": None, "variation_value": None}

    base_music_prompt = f"upbeat tempo, inspired by {style_notes}"
    base_params = {
        "music_style": genre, # Generic style param
        "video_keywords": [genre, "retro", "neon", "dreamy"],
        "make_instrumental": False, # Note: May not be supported by all models
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
            logger.info(f"A/B Test: Applying variation {chosen_index} ('{chosen_variation}') for parameter '{AB_TEST_PARAMETER}'.")

            if AB_TEST_PARAMETER == "music_prompt_prefix":
                prompt_prefix = chosen_variation.format(genre=genre)
                base_params["music_prompt"] = f"{prompt_prefix}, {base_music_prompt}"
            else:
                 logger.warning(f"A/B test parameter '{AB_TEST_PARAMETER}' not handled. Using default.")
                 base_params["music_prompt"] = f"A dreamy {genre} track, {base_music_prompt}"
        else:
            logger.warning(f"A/B testing enabled but no variations defined for '{AB_TEST_PARAMETER}'. Using default.")
            base_params["music_prompt"] = f"A dreamy {genre} track, {base_music_prompt}"
    else:
        base_params["music_prompt"] = f"A dreamy {genre} track, {base_music_prompt}"

    base_params["ab_test_info"] = ab_test_info
    return base_params

# --- Real Generation Functions --- #
def generate_track(music_params):
    """Generates a track using aimlapi.com music models with fallback."""
    logger.info(f"Generating track with aimlapi.com using params: {music_params}")
    if not AIMLAPI_KEY:
        logger.error("AIMLAPI_KEY (or SUNO_API_KEY) is missing. Cannot generate track.")
        return None

    headers = {
        "Authorization": f"Bearer {AIMLAPI_KEY}",
        "Content-Type": "application/json"
    }

    for model_name in MUSIC_MODELS_ORDER:
        logger.info(f"Attempting music generation with model: {model_name}")
        payload = {
            "model": model_name,
            "prompt": music_params.get("music_prompt", "upbeat electronic track"),
            # Add model-specific parameters here if needed based on future research
            # e.g., minimax-music might have different options than stable-audio
        }
        # Conditionally add make_instrumental if needed and supported by the specific model
        # For now, assume it's not universally supported by v2 endpoint
        # if model_name == "some_model_that_supports_it" and music_params.get("make_instrumental") is not None:
        #     payload["make_instrumental"] = music_params.get("make_instrumental")

        try:
            response = requests.post(AIMLAPI_MUSIC_ENDPOINT, headers=headers, json=payload, timeout=180)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            result = response.json()
            logger.debug(f"aimlapi.com API Response (Model: {model_name}): {result}")

            # Extract track URL and ID - Adjust based on actual v2 API response structure
            # Assuming v2 response structure like: { "generation_id": "...", "audio_url": "..." }
            audio_url = result.get("audio_url")
            track_id = result.get("generation_id") or str(uuid.uuid4()) # Use generation_id if available

            if audio_url:
                logger.info(f"Successfully generated track with aimlapi.com model '{model_name}': ID={track_id}, URL={audio_url}")
                return {"track_id": track_id, "track_url": audio_url, "model_used": model_name}
            else:
                logger.error(f"aimlapi.com API call successful (Model: '{model_name}') but no audio_url found in response: {result}")

        except requests.exceptions.RequestException as e:
            logger.error(f"aimlapi.com API call failed for model '{model_name}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from aimlapi.com (Model: '{model_name}'): {e}. Response text: {response.text}")

    logger.error("All aimlapi.com music models failed. Cannot generate track.")
    return None

def select_video(video_params):
    """Selects a video using Pexels first, then Pixabay as fallback."""
    logger.info(f"Selecting video with params: {video_params}")
    query = " ".join(video_params.get("video_keywords", ["abstract"])) # Join keywords for search
    orientation = "landscape" # Default or adapt based on params
    size = "medium" # Default or adapt based on params

    # --- Try Pexels --- #
    if PEXELS_API_KEY:
        logger.info(f"Searching Pexels for video with query: '{query}', orientation: {orientation}, size: {size}")
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": query,
            "orientation": orientation,
            "size": size,
            "per_page": 10 # Fetch a few options
        }
        try:
            response = requests.get(PEXELS_API_VIDEO_ENDPOINT, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            videos = data.get("videos", [])
            if videos:
                logger.info(f"Found {len(videos)} videos on Pexels. Selecting one.")
                selected_video = random.choice(videos)
                logger.info(f"Selected Pexels video: ID={selected_video['id']}, URL={selected_video['video_files'][0]['link']}")
                return {"video_id": selected_video["id"], "video_url": selected_video["video_files"][0]["link"], "source": "pexels"}
            else:
                logger.warning(f"No videos found on Pexels for query: '{query}'")
        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from Pexels: {e}. Response text: {response.text}")
    else:
        logger.warning("PEXELS_API_KEY missing. Skipping Pexels search.")

    # --- Try Pixabay (Fallback) --- #
    if PIXABAY_API_KEY:
        logger.info(f"Searching Pixabay for video with query: '{query}', orientation: {orientation}")
        params = {
            "key": PIXABAY_API_KEY,
            "q": query,
            "orientation": orientation,
            "video_type": "film", # Or "animation"
            "per_page": 10
        }
        try:
            response = requests.get(PIXABAY_API_VIDEO_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            videos = data.get("hits", [])
            if videos:
                logger.info(f"Found {len(videos)} videos on Pixabay. Selecting one.")
                selected_video = random.choice(videos)
                logger.info(f"Selected Pixabay video: ID={selected_video['id']}, URL={selected_video['videos']['medium']['url']}")
                return {"video_id": selected_video["id"], "video_url": selected_video["videos"]["medium"]["url"], "source": "pixabay"}
            else:
                logger.warning(f"No videos found on Pixabay for query: '{query}'")
        except requests.exceptions.RequestException as e:
            logger.error(f"Pixabay API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from Pixabay: {e}. Response text: {response.text}")
    else:
        logger.warning("PIXABAY_API_KEY missing. Skipping Pixabay search.")

    logger.error("Failed to select video from both Pexels and Pixabay.")
    return None

# --- LLM Reflection --- #
def perform_reflection(artist_profile, track_info, video_info):
    if not llm_orchestrator:
        logger.warning("LLM Orchestrator not initialized. Skipping reflection.")
        return None

    logger.info(f"Performing reflection for artist {artist_profile['name']} (ID: {artist_profile['artist_id']})")

    prompt = f"""
    Artist Profile:
    Name: {artist_profile.get('name')}
    Genre: {artist_profile.get('genre')}
    Style Notes: {artist_profile.get('style_notes')}

    Generated Track:
    ID: {track_info.get('track_id') if track_info else 'N/A'}
    URL: {track_info.get('track_url') if track_info else 'N/A'}
    Model Used: {track_info.get('model_used') if track_info else 'N/A'}

    Selected Video:
    ID: {video_info.get('video_id') if video_info else 'N/A'}
    URL: {video_info.get('video_url') if video_info else 'N/A'}
    Source: {video_info.get('source') if video_info else 'N/A'}

    Reflect on this generated content. Does it align with the artist's profile? Suggest improvements or alternative directions for the next generation. Keep the reflection concise (max {REFLECTION_MAX_TOKENS} tokens).
    """

    try:
        reflection_result = llm_orchestrator.generate_text(
            prompt=prompt,
            max_tokens=REFLECTION_MAX_TOKENS,
            temperature=REFLECTION_TEMPERATURE,
            llm_config=artist_profile.get("llm_config") # Use artist-specific config if available
        )
        logger.info(f"LLM Reflection result for artist {artist_profile['artist_id']}: {reflection_result}")
        return reflection_result
    except LLMOrchestratorError as e:
        logger.error(f"LLM reflection failed for artist {artist_profile['artist_id']}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during LLM reflection for artist {artist_profile['artist_id']}: {e}", exc_info=True)
        return None

# --- Preview and Approval --- #
def generate_preview_data(run_id, artist_profile, track_info, video_info, reflection_result, params):
    preview = {
        "run_id": run_id,
        "artist_id": artist_profile["artist_id"],
        "artist_name": artist_profile.get("name", "Unknown Artist"),
        "track_url": track_info.get("track_url") if track_info else None,
        "video_url": video_info.get("video_url") if video_info else None,
        "reflection": reflection_result,
        "parameters_used": params,
        "timestamp": datetime.utcnow().isoformat()
    }
    logger.info(f"Generated preview data for run {run_id}, artist {artist_profile['artist_id']}")
    return preview

def send_for_approval(preview_data):
    run_id = preview_data["run_id"]
    release_id = str(uuid.uuid4()) # Generate a unique ID for this potential release
    preview_data["release_id"] = release_id # Add release_id to data

    logger.info(f"Sending preview to Telegram for run {run_id}, release_id {release_id}")
    try:
        send_preview_to_telegram(preview_data, release_id) # Pass release_id
        # Create status file indicating pending
        status_file = os.path.join(RUN_STATUS_DIR, f"{run_id}.status")
        with open(status_file, "w") as f:
            json.dump({"status": "pending", "release_id": release_id}, f)
        return True, release_id
    except Exception as e:
        logger.error(f"Failed to send preview to Telegram for run {run_id}: {e}")
        return False, None

def wait_for_approval(run_id):
    logger.info(f"Waiting for approval for run {run_id} (up to {MAX_APPROVAL_WAIT_TIME}s)...")
    start_time = time.time()
    status_file = os.path.join(RUN_STATUS_DIR, f"{run_id}.status")

    while time.time() - start_time < MAX_APPROVAL_WAIT_TIME:
        logger.info(f"Checking approval status for run {run_id}...")
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    status_data = json.load(f)
                    status = status_data.get("status")
                    release_id = status_data.get("release_id") # Get release_id from status file
                    if status == "approved":
                        logger.info(f"Run {run_id} approved by user.")
                        return True, release_id
                    elif status == "rejected":
                        logger.info(f"Run {run_id} rejected by user.")
                        return False, release_id
                    elif status == "pending":
                        logger.debug(f"Run {run_id} still pending...")
                    else:
                        logger.warning(f"Approval status for run {run_id} is unknown or invalid: {status}")
                        # Treat unknown status as rejection for safety
                        return False, release_id
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Error reading approval status file for run {run_id}: {e}")
                # Wait and retry in case of temporary file access issue
        else:
            logger.debug(f"Status file for run {run_id} not found yet.")

        time.sleep(POLL_INTERVAL)

    logger.warning(f"Approval timed out for run {run_id} after {MAX_APPROVAL_WAIT_TIME} seconds.")
    # Attempt to read release_id one last time if file exists
    release_id = None
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as f:
                status_data = json.load(f)
                release_id = status_data.get("release_id")
        except Exception:
            pass # Ignore errors here, just trying to get release_id
    return False, release_id # Timeout is considered a rejection

# --- Release Processing --- #
def process_release(run_id, release_id, preview_data):
    logger.info(f"Processing approved run {run_id} with release_id {release_id}")
    try:
        # Pass the full preview_data which now includes release_id
        process_approved_run(preview_data)
        logger.info(f"Successfully processed release for run {run_id}")
    except Exception as e:
        logger.error(f"Error processing approved run {run_id}: {e}")

# --- Artist State Update --- #
def update_artist_status(artist_id: str, new_status: str) -> bool:
    try:
        logger.info(f"Updating artist {artist_id} status to '{new_status}'")
        update_artist(artist_id, {"status": new_status})
    except Exception as e:
        logger.error(f"Failed to update artist {artist_id} status: {e}")

# FIX: This function was removed as its logic is now inside update_artist_performance_db
# def update_artist_performance(artist_id, run_id, approved, track_info, video_info, reflection_result, params, ab_test_info):
#     try:
#         logger.info(f"Updating performance history for artist {artist_id} (Run ID: {run_id}, Approved: {approved})")
#         performance_data = {
#             "run_id": run_id,
#             "timestamp": datetime.utcnow().isoformat(),
#             "approved": approved,
#             "track_info": track_info,
#             "video_info": video_info,
#             "reflection_result": reflection_result,
#             "parameters_used": params,
#             "ab_test_info": ab_test_info
#         }
#         # FIX: Pass correct arguments to update_artist_performance_db
#         update_artist_performance_db(artist_id, run_id, 'approved' if approved else 'rejected', ARTIST_RETIREMENT_THRESHOLD)
#     except Exception as e:
#         logger.error(f"Failed to update performance history for artist {artist_id}: {e}")

# --- Main Batch Runner Loop --- #
def run_batch():
    logger.info("Starting AI Artist Batch Runner...")
    cycle_count = 0
    while True: # Loop indefinitely or until stopped
        cycle_count += 1
        logger.info(f"Starting batch run cycle {cycle_count}...")
        run_id = str(uuid.uuid4())
        artist_profile = None # Ensure artist_profile is defined in this scope
        approved = False
        release_id = None
        track_info = None
        video_info = None
        reflection_result = None
        params = None
        ab_test_info = {"enabled": False}
        run_status = 'unknown' # Track run outcome for DB update

        try:
            artist_profile = select_next_artist()
            if not artist_profile:
                logger.error("No artist selected, skipping cycle.")
                time.sleep(60) # Wait before trying again
                continue

            artist_id = artist_profile["artist_id"]
            logger.info(f"Processing artist: {artist_profile['name']} (ID: {artist_profile['artist_id']}, Status: {artist_profile['status']})")

            # 1. Get Parameters (including A/B test variations if enabled)
            params = get_adapted_parameters(artist_profile)
            ab_test_info = params.get("ab_test_info", {"enabled": False})
            logger.info(f"Generated parameters: {params}")

            # 2. Generate Track
            track_info = generate_track(params)
            if not track_info:
                logger.error(f"Failed to generate track for artist {artist_id}. Skipping cycle.")
                run_status = 'generation_failed_track'
                # FIX: Call update_artist_performance_db directly with correct args
                update_artist_performance_db(artist_id, run_id, run_status, ARTIST_RETIREMENT_THRESHOLD)
                lifecycle_manager.evaluate_artist_lifecycle(artist_id) # Evaluate after failure
                continue
            logger.info(f"Generated track: {track_info}")

            # 3. Select Video
            video_info = select_video(params)
            if not video_info:
                logger.error(f"Failed to select video for artist {artist_id}. Skipping cycle.")
                run_status = 'generation_failed_video'
                # FIX: Call update_artist_performance_db directly with correct args
                update_artist_performance_db(artist_id, run_id, run_status, ARTIST_RETIREMENT_THRESHOLD)
                lifecycle_manager.evaluate_artist_lifecycle(artist_id) # Evaluate after failure
                continue
            logger.info(f"Selected video: {video_info}")

            # 4. Perform Reflection
            reflection_result = perform_reflection(artist_profile, track_info, video_info)
            logger.info(f"Generated reflection: {reflection_result}") # Log even if None

            # 5. Generate Preview Data
            preview_data = generate_preview_data(run_id, artist_profile, track_info, video_info, reflection_result, params)
            logger.info(f"Generated preview data: {preview_data}")

            # 6. Send for Approval & Wait
            sent_ok, generated_release_id = send_for_approval(preview_data)
            if sent_ok:
                approved, release_id = wait_for_approval(run_id)
                if not release_id:
                    release_id = generated_release_id # Use the one generated if wait timed out but we have it
            else:
                logger.error(f"Failed to send run {run_id} for approval. Marking as rejected.")
                approved = False
                release_id = generated_release_id # Keep track of the ID even if sending failed

            # Determine final run status for DB update
            run_status = 'approved' if approved else 'rejected'

            # 7. Update Artist Performance History (using the correct function call)
            # FIX: Call update_artist_performance_db directly with correct args
            update_artist_performance_db(artist_id, run_id, run_status, ARTIST_RETIREMENT_THRESHOLD)

            # 8. Process Release if Approved
            if approved and release_id:
                process_release(run_id, release_id, preview_data)
                # If artist was a Candidate, promote to Active after first approval
                # This logic is now handled within update_artist_performance_db
                # if artist_profile.get("status") == "Candidate":
                #     logger.info(f"Promoting candidate artist {artist_id} to Active after first approval.")
                #     update_artist_status(artist_id, "Active")
                #     # Reload profile to reflect status change for logging
                #     artist_profile = get_artist(artist_id)

            # 9. Update Artist Lifecycle (based on approval/rejection)
            # This is now implicitly handled by update_artist_performance_db and subsequent get_artist calls
            # lifecycle_manager.evaluate_artist_lifecycle(artist_id)
            # Reload profile to get potentially updated status for logging
            artist_profile = get_artist(artist_id) # Reload to get latest status after DB update

            logger.info(f"Run {run_id} completed. Artist: {artist_profile.get('name', 'N/A')}, Status: {artist_profile.get('status', 'N/A')}, Approved: {approved}")

            # Clean up status file
            status_file = os.path.join(RUN_STATUS_DIR, f"{run_id}.status")
            if os.path.exists(status_file):
                os.remove(status_file)

        except Exception as e:
            logger.error(f"Error during batch run cycle {cycle_count} for artist {artist_profile.get('artist_id', 'N/A') if artist_profile else 'N/A'}: {e}", exc_info=True)
            # Attempt to update performance as failure if artist context available
            if artist_profile and run_id:
                try:
                    # FIX: Call update_artist_performance_db directly with correct args
                    update_artist_performance_db(artist_profile["artist_id"], run_id, 'error', ARTIST_RETIREMENT_THRESHOLD)
                    # lifecycle_manager.evaluate_artist_lifecycle(artist_profile["artist_id"])
                except Exception as inner_e:
                    logger.error(f"Failed to record performance/lifecycle update after cycle error: {inner_e}")

        logger.info(f"Batch run cycle {cycle_count} finished.")
        # Add a delay between cycles if needed
        time.sleep(5)

if __name__ == "__main__":
    try:
        run_batch()
    except KeyboardInterrupt:
        logger.info("Batch runner stopped by user.")
    except Exception as e:
        logger.critical(f"Unhandled critical error in batch runner: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Batch runner finished.")

