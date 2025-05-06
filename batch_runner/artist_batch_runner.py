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


# Define custom exception for initialization errors
class BatchRunnerInitializationError(Exception):
    pass


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
    # Raise specific error instead of sys.exit
    raise BatchRunnerInitializationError(
        f"Failed to import core modules, release_chain, orchestrator, "
        f"or services: {e}"
    )

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
        logging.StreamHandler(sys.stdout),  # Keep stdout for visibility
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
    logger.critical(f"Failed to initialize or populate artist database: {e}.")
    # Raise specific error instead of sys.exit
    raise BatchRunnerInitializationError(
        f"Failed to initialize or populate artist database: {e}"
    )

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
        f"Reflection/Creation disabled."
    )
    llm_orchestrator = None  # Allow continuation without LLM features

try:
    lifecycle_manager = ArtistLifecycleManager()
    last_lifecycle_check_time = datetime.min
except Exception as e:
    logger.critical(f"Failed to initialize Artist Lifecycle Manager: {e}.")
    # Raise specific error instead of sys.exit
    raise BatchRunnerInitializationError(
        f"Failed to initialize Artist Lifecycle Manager: {e}"
    )

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
        f"Failed to initialize Beat Service: {e}. Music generation/analysis disabled."
    )
    beat_service = None

try:
    lyrics_service = (
        LyricsService()
    )  # Assumes orchestrator is passed or accessible
except Exception as e:
    logger.error(
        f"Failed to initialize Lyrics Service: {e}. Lyrics generation disabled."
    )
    lyrics_service = None

try:
    production_service = ProductionService()
except Exception as e:
    logger.error(
        f"Failed to initialize Production Service: {e}. Audio post-processing disabled."
    )
    production_service = None


def create_new_artist_profile():
    logger.info("Attempting to create a new artist profile...")
    if not llm_orchestrator:
        logger.error(
            "LLM Orchestrator not available. Cannot create new artist profile."
        )
        return None

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
            f"Successfully created new artist {added_id} ('{artist_name}'). Now generating voice sample..."
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
                        f"Generated voice sample URL for artist {added_id}: {voice_url}"
                    )
                    # Update the artist record with the voice URL
                    update_success = update_artist(
                        added_id, {"voice_url": voice_url}
                    )
                    if update_success:
                        logger.info(
                            f"Successfully saved voice URL for artist {added_id}."
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
                    f"Unexpected error during voice generation for artist {added_id}: {e}",
                    exc_info=True,
                )
        else:
            logger.warning(
                f"Voice service not available, skipping voice generation for artist {added_id}."
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
                f"Finished lifecycle check. Evaluated {len(all_artists)} artists."
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
            # Re-fetch selectable artists in case creation failed but pool exists
            selectable_artists = get_all_artists(
                status_filter="Active"
            ) + get_all_artists(status_filter="Candidate")
            if not selectable_artists:
                logger.error(
                    "No active or candidate artists available and failed to create a new one. Cannot proceed."
                )
                return None  # Indicate failure to select

    # Simple selection: Randomly pick from active/candidate artists
    # TODO: Implement more sophisticated selection logic (e.g., based on
    # performance, last run time)
    if selectable_artists:
        selected_artist = random.choice(selectable_artists)
        logger.info(
            f"Selected artist: {selected_artist['name']} (ID: {selected_artist['artist_id']})"
        )
        return selected_artist
    else:
        logger.error("No artists available for selection.")
        return None


async def generate_music_for_artist(artist):
    logger.info(f"Generating music for artist: {artist['name']}")
    run_id = str(uuid.uuid4())
    run_timestamp = datetime.utcnow().isoformat()
    run_status_file = os.path.join(RUN_STATUS_DIR, f"{run_id}.json")

    run_data = {
        "run_id": run_id,
        "artist_id": artist["artist_id"],
        "artist_name": artist["name"],
        "genre": artist["genre"],
        "timestamp": run_timestamp,
        "status": "pending_generation",
        "music_prompt": None,
        "music_url": None,
        "lyrics": None,
        "vocals_url": None,
        "final_audio_url": None,
        "preview_message_id": None,
        "approval_status": "pending",
        "error": None,
        "ab_test_variant": None,
    }

    # --- A/B Testing --- #
    music_prompt_prefix = "A {genre} track"
    if AB_TESTING_ENABLED and AB_TEST_PARAMETER == "music_prompt_prefix":
        variations = AB_TEST_VARIATIONS.get(
            AB_TEST_PARAMETER, [music_prompt_prefix]
        )
        chosen_variation = random.choice(variations)
        run_data["ab_test_variant"] = chosen_variation
        music_prompt_prefix = chosen_variation
        logger.info(
            f"A/B Test: Using music prompt prefix variation: ",
            f"'{chosen_variation}'",
        )
    # --- Generate Music Prompt --- #
    # Simple prompt based on genre and style notes
    music_prompt = (
        f"{music_prompt_prefix.format(genre=artist['genre'])}. "
        f"Style: {artist.get('style_notes', 'eclectic')}."
    )
    run_data["music_prompt"] = music_prompt
    logger.info(f"Generated music prompt: {music_prompt}")

    # --- Generate Beat --- #
    if not beat_service:
        run_data["status"] = "failed"
        run_data["error"] = "Beat service not available."
        logger.error(run_data["error"])
        save_run_status(run_data)
        return run_data

    try:
        logger.info("Generating beat...")
        beat_result = beat_service.generate_beat(music_prompt, run_id)
        if beat_result and beat_result.get("audio_url"):
            run_data["music_url"] = beat_result["audio_url"]
            run_data["status"] = "pending_lyrics"
            logger.info(f"Beat generated: {run_data['music_url']}")
        else:
            raise Exception(
                f"Beat generation failed or returned invalid result: {beat_result}"
            )
    except Exception as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Beat generation failed: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data

    # --- Generate Lyrics --- #
    if not lyrics_service:
        run_data["status"] = "failed"
        run_data["error"] = "Lyrics service not available."
        logger.error(run_data["error"])
        save_run_status(run_data)
        return run_data

    try:
        logger.info("Generating lyrics...")
        lyrics = await lyrics_service.generate_lyrics(
            artist["name"],
            artist["genre"],
            artist.get("style_notes", ""),
            run_data["music_url"],  # Pass music URL for context
        )
        if lyrics:
            run_data["lyrics"] = lyrics
            run_data["status"] = "pending_vocals"
            logger.info(f"Lyrics generated successfully.")
            # logger.debug(f"Generated Lyrics:\n{lyrics}") # Log full lyrics only if needed
        else:
            raise LyricsServiceError(
                "Lyrics generation returned empty result."
            )
    except LyricsServiceError as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Lyrics generation failed: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data
    except Exception as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Unexpected error during lyrics generation: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data

    # --- Generate Vocals --- #
    if not voice_service:
        run_data["status"] = "failed"
        run_data["error"] = "Voice service not available."
        logger.error(run_data["error"])
        save_run_status(run_data)
        return run_data

    artist_voice_url = artist.get("voice_url")
    if not artist_voice_url:
        # Attempt to generate voice on the fly if missing
        logger.warning(
            f"Voice URL missing for artist {artist['artist_id']}. Attempting generation..."
        )
        try:
            sample_text = f"Voice sample for {artist['name']}."
            artist_voice_url = voice_service.generate_artist_voice(
                artist["name"], sample_text
            )
            if artist_voice_url:
                logger.info(
                    f"Generated temporary voice URL: {artist_voice_url}"
                )
                # Optionally update the DB here, or just use the temp URL
                # update_artist(artist['artist_id'], {"voice_url": artist_voice_url})
            else:
                raise VoiceServiceError("On-the-fly voice generation failed.")
        except VoiceServiceError as e:
            run_data["status"] = "failed"
            run_data["error"] = (
                f"Vocal generation failed (voice setup error): {e}"
            )
            logger.error(run_data["error"], exc_info=True)
            save_run_status(run_data)
            return run_data
        except Exception as e:
            run_data["status"] = "failed"
            run_data["error"] = (
                f"Unexpected error during on-the-fly voice generation: {e}"
            )
            logger.error(run_data["error"], exc_info=True)
            save_run_status(run_data)
            return run_data

    try:
        logger.info("Generating vocals...")
        vocals_url = voice_service.generate_vocals(
            artist_voice_url, run_data["lyrics"], run_id
        )
        if vocals_url:
            run_data["vocals_url"] = vocals_url
            run_data["status"] = "pending_production"
            logger.info(f"Vocals generated: {vocals_url}")
        else:
            raise VoiceServiceError("Vocal generation returned empty result.")
    except VoiceServiceError as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Vocal generation failed: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data
    except Exception as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Unexpected error during vocal generation: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data

    # --- Production (Mixing Vocals and Beat) --- #
    if not production_service:
        run_data["status"] = "failed"
        run_data["error"] = "Production service not available."
        logger.error(run_data["error"])
        save_run_status(run_data)
        return run_data

    try:
        logger.info("Starting production (mixing vocals and beat)...")
        final_audio_path = production_service.mix_audio(
            run_data["music_url"],
            run_data["vocals_url"],
            run_id,
            artist["genre"],  # Pass genre for potential genre-specific mixing
        )
        if final_audio_path:
            # Assuming mix_audio returns a local path, needs upload/URL handling
            # TODO: Implement upload logic (e.g., to S3) and get public URL
            # For now, using placeholder URL based on local path
            run_data["final_audio_url"] = (
                f"file://{final_audio_path}"  # Placeholder
            )
            run_data["status"] = "pending_approval"
            logger.info(
                f"Production complete. Final audio at: {run_data['final_audio_url']}"
            )
        else:
            raise ProductionServiceError("Audio mixing returned empty result.")
    except ProductionServiceError as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Production failed: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data
    except Exception as e:
        run_data["status"] = "failed"
        run_data["error"] = f"Unexpected error during production: {e}"
        logger.error(run_data["error"], exc_info=True)
        save_run_status(run_data)
        return run_data

    # --- Send Preview for Approval --- #
    try:
        logger.info("Sending preview for approval...")
        preview_message_id = await send_preview_to_telegram(
            run_id,
            artist["name"],
            artist["genre"],
            run_data["final_audio_url"],  # Use final audio URL
            run_data["lyrics"],
            run_data["music_prompt"],
        )
        if preview_message_id:
            run_data["preview_message_id"] = preview_message_id
            logger.info(f"Preview sent. Message ID: {preview_message_id}")
        else:
            # Don't fail the whole run, just log a warning
            logger.warning("Failed to send preview to Telegram.")
            run_data["error"] = (
                run_data["error"] + "; " if run_data["error"] else ""
            ) + "Failed to send Telegram preview."
    except Exception as e:
        logger.error(f"Error sending preview: {e}", exc_info=True)
        run_data["error"] = (
            run_data["error"] + "; " if run_data["error"] else ""
        ) + f"Error sending Telegram preview: {e}"

    # Save final pending approval status
    save_run_status(run_data)
    logger.info(f"Run {run_id} completed generation, awaiting approval.")
    return run_data


def save_run_status(run_data):
    run_id = run_data["run_id"]
    run_status_file = os.path.join(RUN_STATUS_DIR, f"{run_id}.json")
    try:
        with open(run_status_file, "w") as f:
            json.dump(run_data, f, indent=4)
        logger.debug(f"Saved run status for {run_id} to {run_status_file}")
    except IOError as e:
        logger.error(f"Failed to save run status for {run_id}: {e}")


def load_run_status(run_id):
    run_status_file = os.path.join(RUN_STATUS_DIR, f"{run_id}.json")
    if os.path.exists(run_status_file):
        try:
            with open(run_status_file, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load run status for {run_id}: {e}")
            return None
    else:
        logger.warning(f"Run status file not found for {run_id}")
        return None


def check_approval_status(run_id):
    # In a real system, this would query an external source (API, DB, etc.)
    # For simulation, we check the run status file itself for manual updates
    # or rely on Telegram callback updates (handled elsewhere)
    run_data = load_run_status(run_id)
    if run_data:
        return run_data.get("approval_status", "pending")
    return "error"


async def reflect_on_run(run_data):
    logger.info(f"Reflecting on run {run_data['run_id']}...")
    if not llm_orchestrator:
        logger.warning("LLM Orchestrator not available, skipping reflection.")
        return

    artist_id = run_data["artist_id"]
    artist = get_artist(artist_id)
    if not artist:
        logger.error(f"Artist {artist_id} not found for reflection.")
        return

    prompt = f"""Analyze the outcome of the latest music generation run for artist '{artist['name']}' (ID: {artist_id}).

Run ID: {run_data['run_id']}
Genre: {run_data['genre']}
Music Prompt: {run_data['music_prompt']}
Approval Status: {run_data['approval_status']}
Error (if any): {run_data.get('error', 'None')}
Artist Style Notes: {artist.get('style_notes', 'N/A')}

Based on this run's outcome ({run_data['approval_status']}), provide concise suggestions for the artist's next run.
Focus on:
1. Adjusting the music prompt (e.g., different keywords, tempo, mood).
2. Modifying style notes (e.g., add/remove preferences).
3. Suggesting potential A/B tests if applicable (e.g., try different prompt structures, lyrical themes).

Keep the reflection brief and actionable. Output only the suggestions.
"""

    try:
        reflection = await llm_orchestrator.generate_text(
            prompt=prompt,
            max_tokens=REFLECTION_MAX_TOKENS,
            temperature=REFLECTION_TEMPERATURE,
        )
        if reflection:
            logger.info(
                f"Reflection generated for artist {artist_id}: {reflection}"
            )
            # Update artist profile with reflection (e.g., append to notes)
            current_notes = artist.get("style_notes", "")
            new_notes = f"{current_notes}\n\nReflection ({run_data['timestamp']}):\n{reflection}"
            update_artist(artist_id, {"style_notes": new_notes.strip()})
            logger.info(f"Updated style notes for artist {artist_id}.")
        else:
            logger.warning(
                f"Reflection generation returned empty result for artist {artist_id}."
            )
    except LLMOrchestratorError as e:
        logger.error(
            f"LLM Orchestrator error during reflection for artist {artist_id}: {e}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during reflection for artist {artist_id}: {e}",
            exc_info=True,
        )


async def wait_for_approval(run_id):
    logger.info(f"Waiting for approval for run {run_id}...")
    start_time = time.time()
    while time.time() - start_time < MAX_APPROVAL_WAIT_TIME:
        approval_status = check_approval_status(run_id)
        if approval_status in ["approved", "rejected"]:
            logger.info(
                f"Approval status received for run {run_id}: {approval_status}"
            )
            return approval_status
        elif approval_status == "error":
            logger.error(
                f"Error checking approval status for run {run_id}. Assuming rejection."
            )
            return "rejected"  # Treat error as rejection

        logger.debug(f"Still waiting for approval for run {run_id}...")
        await asyncio.sleep(POLL_INTERVAL)

    logger.warning(f"Approval timeout for run {run_id}. Assuming rejection.")
    return "rejected"  # Timeout is treated as rejection


async def main_loop():
    logger.info("Starting main batch runner loop...")
    while True:
        try:
            artist = select_next_artist()
            if not artist:
                logger.error(
                    "Failed to select an artist. Waiting before retry..."
                )
                await asyncio.sleep(
                    60
                )  # Wait a minute before retrying selection
                continue

            artist_id = artist["artist_id"]
            logger.info(
                f"Processing artist: {artist['name']} (ID: {artist_id})"
            )

            # Check if artist is on autopilot
            autopilot_enabled = artist.get("autopilot_enabled", False)
            logger.info(
                f"Autopilot enabled for {artist_id}: {autopilot_enabled}"
            )

            run_data = await generate_music_for_artist(artist)

            if run_data["status"] == "failed":
                logger.error(
                    f"Generation failed for artist {artist_id}. Run ID: {run_data['run_id']}. Error: {run_data['error']}"
                )
                # Update performance DB with failure
                update_artist_performance_db(
                    artist_id,
                    run_data["run_id"],
                    "failed",
                    run_data.get("ab_test_variant"),
                )
                # Reflect on the failure
                await reflect_on_run(run_data)
                # Evaluate lifecycle after failure
                lifecycle_manager.evaluate_artist_lifecycle(artist_id)
                await asyncio.sleep(5)  # Short pause after failure
                continue  # Move to next artist

            run_id = run_data["run_id"]

            if autopilot_enabled:
                approval_status = (
                    "approved"  # Autopilot approves automatically
                )
                logger.info(
                    f"Autopilot approved run {run_id} for artist {artist_id}."
                )
                # Update status file immediately
                run_data["approval_status"] = approval_status
                save_run_status(run_data)
            else:
                approval_status = await wait_for_approval(run_id)
                # Update status file with final approval status
                run_data["approval_status"] = approval_status
                save_run_status(run_data)

            # Update performance DB
            update_artist_performance_db(
                artist_id,
                run_id,
                approval_status,
                run_data.get("ab_test_variant"),
            )

            if approval_status == "approved":
                logger.info(
                    f"Run {run_id} approved. Proceeding to release chain..."
                )
                try:
                    release_result = await process_approved_run(run_data)
                    if release_result:
                        logger.info(
                            f"Release chain completed successfully for run {run_id}."
                        )
                    else:
                        logger.error(f"Release chain failed for run {run_id}.")
                except Exception as e:
                    logger.error(
                        f"Error during release chain processing for run {run_id}: {e}",
                        exc_info=True,
                    )
            else:
                logger.info(f"Run {run_id} was rejected.")

            # Reflect on the run outcome (approved or rejected)
            await reflect_on_run(run_data)

            # Evaluate artist lifecycle after run completion
            lifecycle_manager.evaluate_artist_lifecycle(artist_id)

            # Add a short delay before the next artist
            await asyncio.sleep(random.uniform(5, 15))

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down...")
            break
        except BatchRunnerInitializationError as e:
            logger.critical(
                f"Critical initialization error: {e}. Cannot continue."
            )
            break  # Exit loop on critical init errors
        except Exception as e:
            logger.error(f"Unhandled error in main loop: {e}", exc_info=True)
            logger.info(
                "Attempting to recover and continue after a short delay..."
            )
            await asyncio.sleep(30)  # Wait 30s after unexpected error

    logger.info("Batch runner loop finished.")


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except BatchRunnerInitializationError as e:
        # Log critical init errors that prevented startup
        logger.critical(
            f"Batch runner failed to start due to initialization error: {e}"
        )
        sys.exit(1)  # Exit with error code if startup fails critically
    except KeyboardInterrupt:
        logger.info("Batch runner stopped by user.")
    except Exception as e:
        logger.critical(
            f"Batch runner stopped due to unhandled exception: {e}",
            exc_info=True,
        )
        sys.exit(1)  # Exit with error code on unexpected crash
