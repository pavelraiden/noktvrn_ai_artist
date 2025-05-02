"""
Utility functions for audio feature extraction.

This module provides helper functions used by the FeatureExtractor class
to compute specific audio features like tempograms, chromagrams, etc.
"""

import numpy as np
import librosa
from scipy.stats import mode


def compute_tempogram(y, sr, hop_length=512):
    """Compute tempogram for tempo analysis."""
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    tempogram = librosa.feature.tempogram(
        onset_envelope=oenv, sr=sr, hop_length=hop_length
    )
    return tempogram


def compute_chromagram(y, sr, hop_length=512):
    """Compute chromagram for key detection."""
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
    return chroma


def estimate_key(chroma, sr):
    """
    Estimate the key from a chromagram using a simple template matching approach.

    Args:
        chroma (np.ndarray): Chromagram
        sr (int): Sample rate (unused in this simple version, but kept for potential future use)

    Returns:
        tuple: (estimated_key, estimated_mode, key_strength)
    """
    # Aggregate chroma features across time
    chroma_agg = np.sum(chroma, axis=1)
    chroma_norm = chroma_agg / np.sum(chroma_agg)  # Normalize

    # Define major and minor key profiles (Krumhansl-Schmuckler)
    major_profile = np.array(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    )
    minor_profile = np.array(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    )
    major_profile /= np.sum(major_profile)
    minor_profile /= np.sum(minor_profile)

    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    correlations = []

    # Calculate correlation with major and minor profiles for each possible key
    for i in range(12):
        # Major key correlation
        major_corr = np.corrcoef(chroma_norm, np.roll(major_profile, i))[0, 1]
        correlations.append((major_corr, f"{keys[i]} Major"))

        # Minor key correlation
        minor_corr = np.corrcoef(chroma_norm, np.roll(minor_profile, i))[0, 1]
        correlations.append((minor_corr, f"{keys[i]} Minor"))

    # Find the best correlation
    correlations.sort(key=lambda x: x[0], reverse=True)

    best_corr, best_key_mode = correlations[0]
    best_key, best_mode = best_key_mode.split()

    # Simple key strength estimation (difference between best and second best correlation)
    key_strength = (
        correlations[0][0] - correlations[1][0]
        if len(correlations) > 1
        else correlations[0][0]
    )

    # Normalize strength (optional, simple scaling)
    key_strength = max(0, min(1, key_strength * 2))  # Scale to roughly 0-1 range

    return (
        best_key,
        best_mode,
        key_strength,
        correlations[:5],
    )  # Return top 5 candidates


def detect_rhythm_patterns(onset_env, sr, hop_length=512):
    """
    Detect characteristic rhythm patterns (placeholder).
    This is a complex task and requires more advanced algorithms.
    This placeholder returns basic onset information.
    """
    # Basic onset detection
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)

    # Placeholder for more complex pattern analysis
    patterns = {
        "onset_count": len(onset_times),
        "avg_inter_onset_interval": (
            np.mean(np.diff(onset_times)) if len(onset_times) > 1 else 0
        ),
    }
    return patterns


def calculate_tempo_stability(tempogram):
    """
    Calculate tempo stability based on the tempogram.
    A simple measure could be the concentration around the dominant tempo.
    """
    # Find the dominant tempo bin for each time frame
    dominant_tempo_indices = np.argmax(tempogram, axis=0)

    # Calculate the mode (most frequent dominant tempo bin)
    tempo_mode, count = mode(dominant_tempo_indices)

    # Stability: fraction of frames where the dominant tempo is the modal tempo
    stability = count / tempogram.shape[1] if tempogram.shape[1] > 0 else 0

    return float(stability)
