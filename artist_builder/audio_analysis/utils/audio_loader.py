"""
Audio Loader Utility Module

This module provides utilities for loading and preprocessing audio files
for feature extraction and analysis.
"""

import os
import numpy as np
import librosa


def load_audio(file_path, sr=22050, mono=True, duration=None, offset=0.0):
    """
    Load an audio file using librosa.

    Args:
        file_path (str): Path to the audio file
        sr (int, optional): Target sampling rate. Defaults to 22050.
        mono (bool, optional): Whether to convert to mono. Defaults to True.
        duration (float, optional): Duration to load in seconds. Defaults to None (full file).
        offset (float, optional): Start reading after this time (in seconds). Defaults to 0.0.

    Returns:
        tuple: (audio_data, sampling_rate)
            - audio_data (np.ndarray): Audio time series
            - sampling_rate (int): Sampling rate of the audio

    Raises:
        FileNotFoundError: If the audio file does not exist
        Exception: If there's an error loading the audio file
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        y, sr = librosa.load(
            file_path, 
            sr=sr, 
            mono=mono, 
            duration=duration, 
            offset=offset
        )
        
        return y, sr
    
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"Error loading audio file {file_path}: {str(e)}")


def trim_silence(y, sr, threshold_db=20, frame_length=2048, hop_length=512):
    """
    Trim leading and trailing silence from an audio signal.

    Args:
        y (np.ndarray): Audio time series
        sr (int): Sampling rate
        threshold_db (float, optional): Threshold in decibels. Defaults to 20.
        frame_length (int, optional): Frame length for silence detection. Defaults to 2048.
        hop_length (int, optional): Hop length for silence detection. Defaults to 512.

    Returns:
        np.ndarray: Trimmed audio time series
    """
    return librosa.effects.trim(
        y, 
        top_db=threshold_db, 
        frame_length=frame_length, 
        hop_length=hop_length
    )[0]


def normalize_audio(y):
    """
    Normalize audio to the range [-1, 1].

    Args:
        y (np.ndarray): Audio time series

    Returns:
        np.ndarray: Normalized audio time series
    """
    if np.max(np.abs(y)) > 0:
        return y / np.max(np.abs(y))
    return y


def resample_audio(y, orig_sr, target_sr):
    """
    Resample audio to a target sampling rate.

    Args:
        y (np.ndarray): Audio time series
        orig_sr (int): Original sampling rate
        target_sr (int): Target sampling rate

    Returns:
        np.ndarray: Resampled audio time series
    """
    return librosa.resample(y, orig_sr=orig_sr, target_sr=target_sr)


def get_audio_duration(file_path):
    """
    Get the duration of an audio file in seconds.

    Args:
        file_path (str): Path to the audio file

    Returns:
        float: Duration of the audio file in seconds

    Raises:
        FileNotFoundError: If the audio file does not exist
        Exception: If there's an error getting the duration
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        duration = librosa.get_duration(filename=file_path)
        return duration
    
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"Error getting duration of audio file {file_path}: {str(e)}")


def split_into_segments(y, sr, segment_duration=30):
    """
    Split audio into fixed-length segments.

    Args:
        y (np.ndarray): Audio time series
        sr (int): Sampling rate
        segment_duration (int, optional): Duration of each segment in seconds. Defaults to 30.

    Returns:
        list: List of audio segments as numpy arrays
    """
    segment_length = segment_duration * sr
    num_segments = int(np.ceil(len(y) / segment_length))
    segments = []
    
    for i in range(num_segments):
        start = i * segment_length
        end = min(start + segment_length, len(y))
        segment = y[start:end]
        
        # Pad the last segment if it's shorter than segment_length
        if len(segment) < segment_length:
            segment = np.pad(segment, (0, segment_length - len(segment)), 'constant')
        
        segments.append(segment)
    
    return segments
