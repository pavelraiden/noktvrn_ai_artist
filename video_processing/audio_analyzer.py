# Audio analysis functions using librosa

import logging
import librosa
import soundfile as sf
import numpy as np
import requests
import tempfile
import os

logger = logging.getLogger(__name__)


class AudioAnalysisError(Exception):
    """Custom exception for audio analysis errors."""

    pass


def _download_audio(audio_url: str) -> str | None:
    """Downloads audio from a URL to a temporary file."""
    try:
        response = requests.get(audio_url, stream=True, timeout=60)
        response.raise_for_status()

        # Create a temporary file
        # Note: Ensure the temp file has an appropriate extension if
        # librosa/soundfile needs it.
        # Using .wav as a common intermediate format.
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            logger.info(f"Audio downloaded temporarily to: {tmp_file.name}")
            return tmp_file.name
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download audio from {audio_url}: {e}")
        return None
    except IOError as e:
        logger.error(
            f"Failed to write downloaded audio to temporary file: {e}"
        )
        return None


def analyze_audio(audio_path_or_url: str) -> dict | None:
    """Analyzes an audio file (local path or URL) to extract tempo and         duration.

    Args:
        audio_path_or_url: Local path or URL to the audio file.

    Returns:
        A dictionary containing {"tempo": float, "duration":             float} or None if analysis fails.
    """
    local_path = None
    downloaded = False

    if audio_path_or_url.startswith("http://") or audio_path_or_url.startswith(
        "https://"
    ):
        logger.info(
            f"Downloading audio for analysis from: {audio_path_or_url}"
        )
        local_path = _download_audio(audio_path_or_url)
        if not local_path:
            return None
        downloaded = True
    elif audio_path_or_url.startswith("file://"):
        local_path = audio_path_or_url[7:]  # Remove "file://"
        if not os.path.exists(local_path):
            logger.error(f"Local audio file not found: {local_path}")
            return None
    elif os.path.exists(audio_path_or_url):
        local_path = audio_path_or_url
    else:
        logger.error(
            f"Invalid audio path or URL provided: {audio_path_or_url}"
        )
        return None

    try:
        logger.info(f"Analyzing audio file: {local_path}")
        # Load audio file using soundfile (more robust for different formats)
        # and convert to mono if needed
        y, sr = sf.read(local_path)
        if y.ndim > 1:
            y = np.mean(y, axis=1)  # Convert to mono by averaging channels

        # Get duration
        duration = len(y) / sr

        # Estimate tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo)  # Ensure tempo is float

        logger.info(
            f"Analysis complete: Duration={duration:.2f}s, Tempo={tempo:                .2f} BPM"
        )
        return {"tempo": tempo, "duration": duration}

    except Exception as e:
        logger.error(
            f"Error analyzing audio file {local_path}: {e}", exc_info=True
        )
        raise AudioAnalysisError(f"Failed to analyze audio: {e}") from e
    finally:
        # Clean up temporary file if downloaded
        if downloaded and local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
                logger.info(f"Cleaned up temporary audio file: {local_path}")
            except OSError as e:
                logger.warning(
                    f"Failed to clean up temporary audio file {local_path}:                         {e}"
                )


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test with a known URL (replace with a valid, accessible audio URL for     # real testing)
    # test_url = "https://example.com/some_audio.mp3" # Replace this
    # Using the mock URL for         structure test
    test_url = "https://example.com/mock-beat.mp3"

    # Test with a local file (create a dummy file or use a real one)
    # dummy_file = "/tmp/dummy_audio.wav"
    # import soundfile as sf
    # import numpy as np
    # sr_dummy = 22050
    # duration_dummy = 5
    # y_dummy = np.sin(2 * np.pi * 440.0 * np.arange(sr_dummy * duration_dummy)     # / sr_dummy)
    # sf.write(dummy_file, y_dummy, sr_dummy)
    # test_local = dummy_file

    print(f"--- Testing URL Analysis ({test_url}) ---")
    # This will fail download unless mock URL is replaced or server allows
    # download
    analysis_result_url = analyze_audio(test_url)
    if analysis_result_url:
        print(f"URL Analysis Result: {analysis_result_url}")
    else:
        print("URL Analysis failed (as expected for mock URL download).")

    # print(f"--- Testing Local File Analysis ({test_local}) ---")
    # analysis_result_local = analyze_audio(test_local)
    # if analysis_result_local:
    #     print(f"Local Analysis Result: {analysis_result_local}")
    # else:
    #     print("Local Analysis failed.")
    # # Clean up dummy file
    # if os.path.exists(dummy_file):
    #     os.remove(dummy_file)
