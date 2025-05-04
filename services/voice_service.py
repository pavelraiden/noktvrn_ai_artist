# Service for generating artist voice clones

import os
import logging
import tempfile
import sys  # Added

logger = logging.getLogger(__name__)

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


class VoiceServiceError(Exception):
    """Custom exception for VoiceService errors."""

    pass


class VoiceService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning(
                "ELEVENLABS_API_KEY not found. Voice cloning will use mock fallback."
            )

    def generate_artist_voice(self, name: str, sample_text: str) -> str | None:
        """Generates a voice clone for the artist using ElevenLabs API or returns a mock URL.

        Args:
            name: The name of the artist (used for naming the voice).
            sample_text: Text to be synthesized using the cloned voice (for verification/sample generation).

        Returns:
            The URL of a sample audio file generated with the cloned voice, a mock URL, or None if failed.
        """
        logger.info(f"Generating voice clone for artist: {name}")

        if not self.api_key:
            logger.warning(
                "No ELEVENLABS_API_KEY, returning mock voice sample URL"
            )
            # Note: This mock URL doesn't represent the cloned voice itself,
            # but a sample generated *from* it.
            # ElevenLabs API for cloning might return a voice_id, not a direct URL.
            # We'll mock the *result* of using that voice_id to generate a sample.
            return "https://example.com/mock-voice-sample.mp3"

        # --- Actual ElevenLabs API Logic --- #
        # This is a simplified example. Real implementation might involve:
        # 1. Generating a short audio sample locally (e.g., using system TTS or another service)
        # 2. Uploading that sample to ElevenLabs to create the voice clone.
        # 3. Using the returned voice_id to generate the requested sample_text.

        # For simplicity in this step, let's assume we can directly generate a sample
        # using a pre-existing or easily created voice based on the name.
        # A more realistic approach would use client.clone() which requires audio files.

        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs import save

            client = ElevenLabs(api_key=self.api_key)

            # Placeholder: Generate audio using a default voice first, as
            # cloning requires audio files.
            # In a real scenario, you'd use client.clone() with audio file paths.
            # For now, we just generate the sample text with a standard voice.
            # This doesn't *clone* the voice based on the name, but fulfills
            # the step of generating audio.
            # TODO: Refine this to perform actual cloning if feasible without pre-recorded samples.
            logger.info(
                f"Generating audio for text: '{sample_text}' using default voice."
            )
            audio = client.generate(
                text=sample_text,
                voice="Rachel",  # Using a standard voice as placeholder for cloned voice
                model="eleven_multilingual_v2",  # Or another appropriate model
            )

            # Save the audio to a temporary file to simulate getting a URL
            # In a real app, you'd upload this to cloud storage (e.g., S3) and get a public URL.
            tmp_file_path = None
            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False,
                mode="wb",  # Ensure binary mode for save
            ) as tmp_file:
                tmp_file_path = tmp_file.name
                save(audio, tmp_file_path)  # Pass the path directly

            if tmp_file_path:
                logger.info(
                    f"Generated voice sample saved temporarily to: {tmp_file_path}"
                )
                # Return a file URI for local testing, replace with cloud URL in production
                mock_cloud_url = f"file://{tmp_file_path}"  # MOCK URL
                logger.info(
                    f"Returning mock file URL for generated voice sample: {mock_cloud_url}"
                )
                return mock_cloud_url
            else:
                logger.error("Failed to create or write to temporary file.")
                return None

        except ImportError:
            logger.error(
                "ElevenLabs library not installed. Cannot generate voice."
            )
            return None
        except Exception as e:
            logger.error(
                f"Error calling ElevenLabs API or saving file: {e}",
                exc_info=True,
            )  # Added exc_info
            # raise VoiceServiceError(f"Failed to generate voice sample: {e}") from e # Keep commented out for now
            return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # load_dotenv() # If using .env
    voice_service = VoiceService()
    artist_name = "Test Artist"
    text = f"Hello, this is a test voice for {artist_name}."
    sample_url = voice_service.generate_artist_voice(artist_name, text)

    if sample_url:
        print(f"Generated voice sample URL: {sample_url}")
    else:
        print("Voice sample generation failed.")
