# Service for post-processing audio (humanization, smoothing)

import logging
import os
import requests
import tempfile
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize

logger = logging.getLogger(__name__)

# --- Helper Functions --- #


def _download_audio(audio_url: str) -> tuple[str | None, str | None]:
    """Downloads audio from a URL to a temporary file, preserving extension."""
    try:
        response = requests.get(audio_url, stream=True, timeout=60)
        response.raise_for_status()

        # Try to guess extension from URL
        file_extension = os.path.splitext(audio_url)[1]
        if not file_extension or len(file_extension) > 5:  # Basic check
            # Guess from content type if possible
            content_type = response.headers.get("content-type")
            if content_type == "audio/mpeg":
                file_extension = ".mp3"
            elif content_type == "audio/wav":
                file_extension = ".wav"
            elif content_type == "audio/ogg":
                file_extension = ".ogg"
            else:
                file_extension = ".audio"  # Fallback generic extension

        with tempfile.NamedTemporaryFile(
            suffix=file_extension, delete=False
        ) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            logger.info(f"Audio downloaded temporarily to: {tmp_file.name}")
            return tmp_file.name, file_extension
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download audio from {audio_url}: {e}")
        return None, None
    except IOError as e:
        logger.error(
            f"Failed to write downloaded audio to temporary file: {e}"
        )
        return None, None


def _generate_noise_file(
    duration_ms: int, volume_db: float = -40.0
) -> str | None:
    """Generates a temporary white noise file."""
    try:
        sample_rate = 44100
        num_samples = int(sample_rate * duration_ms / 1000)
        noise = np.random.random(num_samples) * 2 - 1  # -1 to 1
        # Convert numpy array to AudioSegment
        noise_segment = AudioSegment(
            noise.tobytes(),
            frame_rate=sample_rate,
            sample_width=noise.dtype.itemsize,
            channels=1,
        )
        # Adjust volume
        noise_segment = noise_segment + volume_db

        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp_file:
            noise_segment.export(tmp_file.name, format="wav")
            logger.info(f"Generated temporary noise file: {tmp_file.name}")
            return tmp_file.name
    except Exception as e:
        logger.error(f"Failed to generate noise file: {e}")
        return None


# --- Production Service --- #


class ProductionServiceError(Exception):
    """Custom exception for ProductionService errors."""


class ProductionService:
    def __init__(self):
        # Configuration for effects can be added here
        self.noise_level_db = -45.0  # Very subtle background noise

    def humanize_audio(self, audio_url: str) -> str | None:
        """Applies subtle effects to make audio sound less sterile.

        Current effects:
        - Normalization
        - Subtle background noise overlay

        Placeholder for future effects:
        - Timing jitter
        - Reverb
        - EQ

        Args:
            audio_url: URL of the input audio file.

        Returns:
            URL/path of the processed audio file, or None if failed.
        """
        logger.info(f"Starting audio humanization for: {audio_url}")
        local_path = None
        noise_path = None
        processed_path = None
        downloaded = False

        try:
            # 1. Download Audio
            local_path, file_extension = _download_audio(audio_url)
            if not local_path:
                raise ProductionServiceError("Failed to download input audio.")
            downloaded = True

            # 2. Load Audio
            logger.info(f"Loading audio file: {local_path}")
            # Explicitly specify format if needed, otherwise pydub tries to
            # guess
            try:
                audio = AudioSegment.from_file(local_path)
            except Exception as load_err:
                # Try common formats if guessing failed
                try:
                    audio = AudioSegment.from_mp3(local_path)
                except Exception as e:
                    logger.warning(f"Could not load {local_path} as MP3: {e}")
                try:
                    audio = AudioSegment.from_wav(local_path)
                except Exception as e:
                    logger.warning(f"Could not load {local_path} as WAV: {e}")
                if "audio" not in locals():  # If still not loaded
                    raise ProductionServiceError(
                        f"Could not load audio file {local_path}: {load_err}"
                    ) from load_err

            # --- Apply Effects --- #

            # 3. Normalization
            logger.info("Applying normalization...")
            processed_audio = normalize(audio)

            # 4. Add Subtle Background Noise
            logger.info(
                f"Generating and adding background noise (level:                     {self.noise_level_db} dB)..."
            )
            noise_path = _generate_noise_file(
                duration_ms=len(processed_audio), volume_db=self.noise_level_db
            )
            if noise_path:
                try:
                    noise = AudioSegment.from_wav(noise_path)
                    # Ensure noise is same length as audio
                    if len(noise) > len(processed_audio):
                        noise = noise[: len(processed_audio)]
                    elif len(noise) < len(processed_audio):
                        # Loop or pad noise - simple padding for now
                        silence_needed = len(processed_audio) - len(noise)
                        noise += AudioSegment.silent(duration=silence_needed)

                    processed_audio = processed_audio.overlay(noise)
                    logger.info("Background noise added.")
                except Exception as noise_err:
                    logger.warning(
                        f"Failed to load or overlay noise file {noise_path}:                             {noise_err}. Skipping noise addition."
                    )
            else:
                logger.warning(
                    "Failed to generate noise file. Skipping noise addition."
                )

            # --- Placeholder for Future Effects --- #
            # TODO: Implement Timing Jitter (complex, requires             # slicing/shifting)
            # logger.info("Applying timing jitter... (Placeholder)")

            # TODO: Implement Reverb (likely requires ffmpeg or external             # library)
            # logger.info("Applying reverb... (Placeholder)")

            # TODO: Implement EQ (requires ffmpeg or external library)
            # logger.info("Applying EQ... (Placeholder)")

            # 5. Export Processed Audio
            output_format = (
                file_extension.lstrip(".") if file_extension else "mp3"
            )
            if output_format not in ["mp3", "wav", "ogg", "flac"]:
                # Rewritten line 165 again, removing the newline completely
                log_message = f"Original format '{output_format}' not ideal for                     export, defaulting to mp3."
                logger.warning(log_message)
                output_format = "mp3"

            with tempfile.NamedTemporaryFile(
                suffix=f".{output_format}", delete=False
            ) as tmp_out_file:
                processed_path = tmp_out_file.name
                logger.info(
                    f"Exporting processed audio to: {processed_path} (format:                         {output_format})"
                )
                processed_audio.export(processed_path, format=output_format)

            # Return mock file URL for local testing
            mock_cloud_url = f"file://{processed_path}"
            logger.info(
                f"Humanization complete. Returning mock file URL:                     {mock_cloud_url}"
            )
            return mock_cloud_url

        except Exception as e:
            logger.error(
                f"Error during audio humanization: {e}", exc_info=True
            )
            # Raise or return None based on desired error handling
            # raise ProductionServiceError(f"Humanization failed: {e}") from e
            return None
        finally:
            # Clean up temporary files
            if downloaded and local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    logger.debug(f"Cleaned up input file: {local_path}")
                except OSError as e:
                    logger.warning(
                        f"Failed to clean up input file {local_path}: {e}"
                    )
            if noise_path and os.path.exists(noise_path):
                try:
                    os.remove(noise_path)
                    logger.debug(f"Cleaned up noise file: {noise_path}")
                except OSError as e:
                    logger.warning(
                        f"Failed to clean up noise file {noise_path}: {e}"
                    )
            # Note: The final processed file (processed_path) is NOT deleted
            # here,
            # as its path is returned. The caller needs to manage it or upload
            # it.


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # load_dotenv() # If using .env
    production_service = ProductionService()

    # Test with the mock beat URL (will likely fail download unless server     # allows)
    # Replace with a real, accessible audio URL for proper testing
    test_audio_url = "https://example.com/mock-beat.mp3"

    print(f"--- Testing Audio Humanization ({test_audio_url}) ---")
    humanized_url = production_service.humanize_audio(test_audio_url)

    if humanized_url:
        print(f"Humanized audio mock URL: {humanized_url}")
        # You can try opening the file path directly if running locally:
        # print(f"Local path: {humanized_url[7:]}")
    else:
        print(
            "Audio humanization failed (check logs for details,                 download might have failed)."
        )
