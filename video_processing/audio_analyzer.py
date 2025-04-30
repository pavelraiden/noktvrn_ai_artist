import librosa
import numpy as np
import logging

logger = logging.getLogger(__name__)

class AudioAnalysisError(Exception):
    """Custom exception for audio analysis errors."""
    pass

def analyze_audio_features(audio_path: str) -> dict:
    """Analyzes an audio file to extract features like tempo and energy.

    Args:
        audio_path: The absolute path to the audio file.

    Returns:
        A dictionary containing extracted features:
        {
            'tempo': float,      # Estimated tempo in beats per minute (BPM)
            'energy': float,     # Root Mean Square (RMS) energy (proxy for loudness/intensity)
            'duration': float    # Duration of the audio in seconds
        }

    Raises:
        AudioAnalysisError: If the audio file cannot be loaded or analyzed.
    """
    logger.info(f"Starting audio analysis for: {audio_path}")
    try:
        # Load the audio file
        y, sr = librosa.load(audio_path, sr=None) # sr=None preserves original sample rate
        logger.debug(f"Audio loaded successfully. Sample rate: {sr}, Duration: {len(y)/sr:.2f}s")

        # Estimate tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        logger.debug(f"Estimated tempo: {tempo:.2f} BPM")

        # Calculate RMS energy
        rms = librosa.feature.rms(y=y)[0]
        # Use mean RMS as a single energy value
        energy = np.mean(rms)
        logger.debug(f"Calculated mean RMS energy: {energy:.4f}")

        # Get duration
        duration = librosa.get_duration(y=y, sr=sr)
        logger.debug(f"Calculated duration: {duration:.2f} seconds")

        analysis_results = {
            'tempo': float(tempo),
            'energy': float(energy),
            'duration': float(duration)
        }
        logger.info(f"Audio analysis completed for: {audio_path}")
        return analysis_results

    except FileNotFoundError:
        logger.error(f"Audio file not found at path: {audio_path}")
        raise AudioAnalysisError(f"Audio file not found: {audio_path}")
    except Exception as e:
        logger.error(f"Error during audio analysis for {audio_path}: {e}", exc_info=True)
        raise AudioAnalysisError(f"Failed to analyze audio file {audio_path}: {e}")

# Example usage (for testing purposes)
if __name__ == '__main__':
    # Configure basic logging for testing
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a dummy audio file for testing (requires numpy and soundfile)
    # In a real scenario, you'd use an actual audio file path.
    try:
        import soundfile as sf
        sr_test = 22050
        duration_test = 5 # seconds
        frequency_test = 440 # Hz (A4 note)
        t_test = np.linspace(0., duration_test, int(sr_test * duration_test))
        amplitude_test = np.iinfo(np.int16).max * 0.5
        data_test = amplitude_test * np.sin(2. * np.pi * frequency_test * t_test)
        dummy_file = '/tmp/test_audio.wav'
        sf.write(dummy_file, data_test.astype(np.int16), sr_test)
        logger.info(f"Created dummy audio file: {dummy_file}")

        # Analyze the dummy file
        features = analyze_audio_features(dummy_file)
        print(f"\nAnalyzed Features:\n{features}")

    except ImportError:
        logger.warning("Skipping dummy audio file creation and test - soundfile not installed.")
    except AudioAnalysisError as e:
        print(f"\nAnalysis failed: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during testing: {e}")

