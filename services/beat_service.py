# Service for handling beat/music generation and analysis

import logging
import time
import requests
import uuid

# Assuming these clients/services exist and are importable
# Need to structure imports based on actual project layout
from api_clients.alt_music_client import AltMusicClient, AltMusicClientError # Using the mockable client
# from api_clients.suno_client import SunoClient # Or wherever the primary client logic resides
from video_processing.audio_analyzer import analyze_audio, AudioAnalysisError

logger = logging.getLogger(__name__)

# Placeholder for primary client logic (replace with actual import/instantiation)
# This might involve refactoring music generation from batch_runner
class MockPrimaryMusicClient:
    def __init__(self):
        self.api_key = os.getenv("AIMLAPI_KEY") or os.getenv("SUNO_API_KEY")
        if not self.api_key:
            logger.warning("Primary music API key (AIMLAPI_KEY/SUNO_API_KEY) not found.")

    def generate_music_with_retry(self, prompt: str, models: list, retries: int = 3, initial_delay: int = 2) -> dict | None:
        logger.info(f"MockPrimaryClient: Attempting generation for prompt: {prompt}")
        # Simulate failure to trigger fallback in BeatService
        logger.warning("MockPrimaryClient: Simulating failure.")
        return None

import os # Add missing import
primary_music_client = MockPrimaryMusicClient() # Replace with actual client
alt_music_client = AltMusicClient()

class BeatServiceError(Exception):
    """Custom exception for BeatService errors."""
    pass

class BeatService:
    def __init__(self):
        # Clients are instantiated outside for now
        self.primary_client = primary_music_client
        self.alt_client = alt_music_client
        # Define retry/fallback parameters
        self.music_models_order = ["primary_model"] + ["alt_model"] # Simplified model list
        self.retries = 3
        self.initial_delay = 2

    def generate_and_analyze_beat(self, prompt: str) -> dict | None:
        """Generates a music track using primary/fallback APIs and analyzes it.

        Args:
            prompt: The prompt for music generation.

        Returns:
            A dictionary containing track_url, tempo, duration, and model_used, or None if failed.
        """
        track_info = None
        logger.info("Attempting to generate beat...")

        # --- Attempt 1: Primary Client with Retry --- #
        # This logic should ideally be within the primary client itself
        if self.primary_client and self.primary_client.api_key:
            logger.info("Trying primary music client...")
            # Assuming primary client has retry logic internally or we wrap it here
            # track_info = self.primary_client.generate_music_with_retry(prompt, self.music_models_order, self.retries, self.initial_delay)
            # Using the mock client which simulates failure:
            track_info = self.primary_client.generate_music_with_retry(prompt, [], self.retries, self.initial_delay)

        # --- Attempt 2: Fallback Client --- #
        if not track_info:
            logger.warning("Primary music generation failed or skipped. Trying alternative client...")
            try:
                # Alt client doesn't have retry logic in this example, but could be added
                alt_track_url = self.alt_client.generate_music(prompt)
                if alt_track_url:
                    track_info = {
                        "track_id": str(uuid.uuid4()), # Generate mock ID
                        "track_url": alt_track_url,
                        "model_used": "alternative/mock"
                    }
                    logger.info(f"Successfully generated track via alternative client: {alt_track_url}")
                else:
                    logger.error("Alternative music generation also failed.")
            except AltMusicClientError as e:
                logger.error(f"Error using alternative music client: {e}")
            except Exception as e:
                 logger.error(f"Unexpected error during alternative music generation: {e}", exc_info=True)

        # --- Analysis --- #
        if track_info and track_info.get("track_url"):
            logger.info(f"Beat generated ({track_info[
'model_used
']}). Analyzing tempo and duration...")
            try:
                analysis = analyze_audio(track_info["track_url"])
                if analysis:
                    track_info.update(analysis) # Add tempo and duration to track_info
                    logger.info(f"Analysis complete: Tempo={analysis[
'tempo
']:.2f}, Duration={analysis[
'duration
']:.2f}s")
                    return track_info
                else:
                    logger.error("Audio analysis failed after successful generation.")
                    # Decide how to handle: return partial info or None?
                    # Returning None for now as analysis is crucial for next step.
                    return None
            except AudioAnalysisError as e:
                logger.error(f"Audio analysis failed: {e}")
                return None
            except Exception as e:
                 logger.error(f"Unexpected error during audio analysis: {e}", exc_info=True)
                 return None
        else:
            logger.error("Failed to generate beat from any source.")
            return None

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # load_dotenv() # If using .env
    beat_service = BeatService()
    test_prompt = "Upbeat electronic track with a retro vibe."
    result = beat_service.generate_and_analyze_beat(test_prompt)

    if result:
        print("--- Beat Generation and Analysis Result ---")
        print(f"Track URL: {result.get(
'track_url
')}")
        print(f"Model Used: {result.get(
'model_used
')}")
        print(f"Tempo (BPM): {result.get(
'tempo
')}")
        print(f"Duration (s): {result.get(
'duration
')}")
    else:
        print("Beat generation and analysis failed.")

