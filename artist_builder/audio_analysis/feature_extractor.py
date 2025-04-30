"""
Feature Extractor Module for Audio Analysis

This module provides functionality to extract musical features from audio files.
It uses librosa and other libraries for comprehensive audio analysis.

Features extracted include:
- Temporal features (BPM, beat positions, rhythm patterns)
- Spectral features (centroid, bandwidth, contrast, rolloff, MFCCs)
- Harmonic features (key and scale, chord progression)
- Structural features (segment boundaries, section identification)
- High-level features (energy level, mood classification, danceability)
"""

import os
import numpy as np
import librosa
import librosa.display
from typing import Dict, List, Tuple, Union, Optional

from .utils.audio_loader import load_audio, normalize_audio, trim_silence
from .utils.feature_utils import (
    compute_tempogram, 
    compute_chromagram, 
    estimate_key, 
    detect_rhythm_patterns,
    calculate_tempo_stability
)


class FeatureExtractor:
    """
    Class for extracting musical features from audio files.
    """
    
    def __init__(self, sr: int = 22050, n_fft: int = 2048, hop_length: int = 512):
        """
        Initialize the FeatureExtractor with audio processing parameters.
        
        Args:
            sr (int): Sampling rate for audio processing
            n_fft (int): FFT window size
            hop_length (int): Number of samples between successive frames
        """
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
    
    def extract_features(self, filepath: str, preprocess: bool = True) -> Dict:
        """
        Extract musical features from an audio file.
        
        Args:
            filepath (str): Path to the audio file to analyze
            preprocess (bool): Whether to preprocess the audio (normalize, trim silence)
            
        Returns:
            dict: Dictionary containing extracted features
        """
        try:
            # Load audio file
            y, sr = load_audio(filepath, sr=self.sr)
            
            # Preprocess if requested
            if preprocess:
                y = normalize_audio(y)
                y = trim_silence(y, sr)
            
            # Extract enhanced features
            bpm_info = self.extract_bpm(y, sr)
            key_info = self.extract_key(y, sr)
            tempo_analysis = self.analyze_tempo(y, sr)
            spectrogram_features = self.extract_spectrogram_features(y, sr)
            
            # Extract features
            features = {
                "status": "success",
                "filepath": filepath,
                "duration": len(y) / sr,
                "temporal": {
                    "tempo": bpm_info["tempo"],
                    "tempo_confidence": bpm_info["confidence"],
                    "beat_positions": bpm_info["beat_positions"],
                    "tempo_stability": tempo_analysis["stability"],
                    "rhythm_patterns": tempo_analysis["patterns"],
                    "onset_count": bpm_info["onset_count"],
                    "onset_density": bpm_info["onset_density"],
                    "beat_regularity": bpm_info["beat_regularity"]
                },
                "harmonic": {
                    "key": key_info["key"],
                    "mode": key_info["mode"],
                    "key_strength": key_info["strength"],
                    "alternative_keys": key_info["alternatives"],
                    "chroma_features": key_info["chroma_features"],
                    "tonnetz_mean": key_info["tonnetz_mean"],
                    "harmonic_ratio": key_info["harmonic_ratio"]
                },
                "spectral": {
                    "centroid_mean": spectrogram_features["centroid"]["mean"],
                    "centroid_std": spectrogram_features["centroid"]["std"],
                    "bandwidth_mean": spectrogram_features["bandwidth"]["mean"],
                    "bandwidth_std": spectrogram_features["bandwidth"]["std"],
                    "contrast_mean": spectrogram_features["contrast"]["mean"],
                    "rolloff_mean": spectrogram_features["rolloff"]["mean"],
                    "rolloff_std": spectrogram_features["rolloff"]["std"],
                    "mfcc_means": spectrogram_features["mfcc"]["means"],
                    "mfcc_stds": spectrogram_features["mfcc"]["stds"],
                    "flatness_mean": spectrogram_features["flatness"]["mean"]
                },
                "high_level": {
                    "energy_level": self._calculate_energy_level(y),
                    "danceability": self._estimate_danceability(bpm_info, tempo_analysis),
                    "mood_valence": self._estimate_mood_valence(y, sr, spectrogram_features),
                    "mood_arousal": self._estimate_mood_arousal(y, sr, spectrogram_features),
                    "energy_mean": spectrogram_features["energy"]["mean"],
                    "energy_std": spectrogram_features["energy"]["std"],
                    "zcr_mean": spectrogram_features["zcr"]["mean"],
                    "zcr_std": spectrogram_features["zcr"]["std"]
                }
            }
            
            return features
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "filepath": filepath
            }
    
    def extract_bpm(self, y: np.ndarray, sr: int) -> Dict:
        """
        Extract accurate BPM using multiple algorithms and ensemble approach.
        
        Args:
            y (np.ndarray): Audio time series
            sr (int): Sample rate
            
        Returns:
            dict: BPM information including tempo, confidence, and stability metrics
        """
        # Compute onset strength envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        
        # Method 1: Standard beat tracking
        tempo1, beat_frames1 = librosa.beat.beat_track(
            onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
        )
        
        # Method 2: Dynamic programming beat tracker
        tempo2, beat_frames2 = librosa.beat.beat_track(
            onset_envelope=onset_env, sr=sr, hop_length=self.hop_length, 
            tightness=100  # Higher tightness for more consistent beats
        )
        
        # Method 3: Tempogram-based estimation
        tempogram = compute_tempogram(y, sr, self.hop_length)
        tempo_max_bin = np.argmax(np.mean(tempogram, axis=1))
        # Convert bin index to BPM (librosa tempogram bins are logarithmically spaced)
        tempo3 = librosa.core.tempo_frequencies(tempogram.shape[0])[tempo_max_bin]
        
        # Ensemble approach: take the median of the three estimates
        tempo_estimates = [tempo1, tempo2, tempo3]
        ensemble_tempo = np.median(tempo_estimates)
        
        # Calculate confidence based on agreement between methods
        # Simple approach: higher confidence if estimates are close
        tempo_std = np.std(tempo_estimates)
        max_std = 20  # Maximum expected standard deviation
        confidence = max(0, 1 - (tempo_std / max_std))
        
        # Get beat positions
        beat_times = librosa.frames_to_time(beat_frames1, sr=sr, hop_length=self.hop_length)
        
        # Onset detection
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=self.hop_length)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
        
        # Calculate beat regularity
        beat_intervals = np.diff(beat_times)
        beat_regularity = 1.0 - min(1.0, np.std(beat_intervals) / np.mean(beat_intervals) if len(beat_intervals) > 0 else 0)
        
        return {
            "tempo": float(ensemble_tempo),
            "confidence": float(confidence),
            "beat_positions": beat_times.tolist(),
            "beat_regularity": float(beat_regularity),
            "onset_count": len(onset_times),
            "onset_density": len(onset_times) / (len(y) / sr)
        }
    
    def extract_key(self, y: np.ndarray, sr: int) -> Dict:
        """
        Extract key and scale information using chromagram analysis.
        
        Args:
            y (np.ndarray): Audio time series
            sr (int): Sample rate
            
        Returns:
            dict: Key information including tonic, mode, key strength, and alternative keys
        """
        # Compute chromagram
        chroma = compute_chromagram(y, sr, self.hop_length)
        
        # Estimate key using the utility function
        key, mode, key_strength, alternatives = estimate_key(chroma, sr)
        
        # Format alternative keys
        alt_keys = [{"key": alt[1].split()[0], "mode": alt[1].split()[1], "correlation": float(alt[0])} 
                   for alt in alternatives]
        
        # Compute tonal centroid (tonnetz)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        
        # Harmonic-percussive source separation for harmonic content analysis
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        harmonic_ratio = np.sum(y_harmonic**2) / (np.sum(y_harmonic**2) + np.sum(y_percussive**2) + 1e-8)
        
        # Compute mean chroma vector for feature storage
        chroma_mean = np.mean(chroma, axis=1).tolist()
        
        return {
            "key": key,
            "mode": mode.lower(),  # Lowercase for consistency
            "strength": float(key_strength),
            "alternatives": alt_keys,
            "chroma_features": chroma_mean,
            "tonnetz_mean": [float(np.mean(tonnetz[i])) for i in range(tonnetz.shape[0])],
            "harmonic_ratio": float(harmonic_ratio)
        }
    
    def analyze_tempo(self, y: np.ndarray, sr: int) -> Dict:
        """
        Perform detailed tempo analysis beyond basic BPM.
        
        Args:
            y (np.ndarray): Audio time series
            sr (int): Sample rate
            
        Returns:
            dict: Tempo analysis including stability, patterns, and groove metrics
        """
        # Compute onset strength envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        
        # Compute tempogram
        tempogram = compute_tempogram(y, sr, self.hop_length)
        
        # Calculate tempo stability
        stability = calculate_tempo_stability(tempogram)
        
        # Detect rhythm patterns
        patterns = detect_rhythm_patterns(onset_env, sr, self.hop_length)
        
        # Analyze groove (microtiming deviations)
        # This is a placeholder for more sophisticated groove analysis
        beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=self.hop_length)[1]
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)
        
        # Simple groove metric: variation in onset strength at beat positions
        if len(beat_frames) > 0:
            beat_strengths = onset_env[beat_frames]
            groove_intensity = float(np.std(beat_strengths) / np.mean(beat_strengths) if np.mean(beat_strengths) > 0 else 0)
        else:
            groove_intensity = 0.0
        
        # Detect tempo changes
        # Simple approach: divide the track into segments and check for tempo changes
        if len(y) > sr * 10:  # Only for tracks longer than 10 seconds
            num_segments = min(4, int(len(y) / (sr * 5)))  # 5-second segments, max 4 segments
            segment_tempos = []
            
            for i in range(num_segments):
                start = int(i * len(y) / num_segments)
                end = int((i + 1) * len(y) / num_segments)
                segment = y[start:end]
                segment_tempo = librosa.beat.tempo(onset_envelope=librosa.onset.onset_strength(
                    y=segment, sr=sr, hop_length=self.hop_length), sr=sr, hop_length=self.hop_length)[0]
                segment_tempos.append(float(segment_tempo))
            
            tempo_changes = {
                "detected": np.std(segment_tempos) > 5.0,  # Threshold for significant change
                "segments": segment_tempos
            }
        else:
            tempo_changes = {"detected": False, "segments": []}
        
        return {
            "stability": float(stability),
            "patterns": patterns,
            "groove_intensity": groove_intensity,
            "tempo_changes": tempo_changes
        }
    
    def extract_spectrogram_features(self, y: np.ndarray, sr: int) -> Dict:
        """
        Extract features from spectrogram representation.
        
        Args:
            y (np.ndarray): Audio time series
            sr (int): Sample rate
            
        Returns:
            dict: Spectrogram features including spectral statistics and temporal evolution
        """
        # Compute the spectrogram
        S = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
        
        # Spectral centroid
        centroid = librosa.feature.spectral_centroid(S=S, sr=sr, hop_length=self.hop_length)[0]
        
        # Spectral bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(S=S, sr=sr, hop_length=self.hop_length)[0]
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(S=S, sr=sr, hop_length=self.hop_length)
        
        # Spectral rolloff
        rolloff = librosa.feature.spectral_rolloff(S=S, sr=sr, hop_length=self.hop_length)[0]
        
        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
        
        # Spectral flatness
        flatness = librosa.feature.spectral_flatness(y=y, hop_length=self.hop_length)[0]
        
        # RMS energy
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
        
        # Temporal evolution: detect significant changes in spectral content
        # Simple approach: standard deviation of frame-to-frame differences
        frame_diffs = np.diff(np.mean(S, axis=0))
        spectral_flux = np.std(frame_diffs)
        
        # Detect structural boundaries (experimental)
        # This uses novelty detection to find points of significant change
        mfcc_novelty = librosa.onset.onset_strength(
            y=None, sr=sr, 
            S=librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr, hop_length=self.hop_length)),
            detrend=True
        )
        
        # Find peaks in novelty curve (potential boundaries)
        peaks = librosa.util.peak_pick(mfcc_novelty, pre_max=20, post_max=20, pre_avg=20, post_avg=20, delta=0.2, wait=10)
        boundaries = librosa.frames_to_time(peaks, sr=sr, hop_length=self.hop_length)
        
        return {
            "centroid": {
                "mean": float(np.mean(centroid)),
                "std": float(np.std(centroid))
            },
            "bandwidth": {
                "mean": float(np.mean(bandwidth)),
                "std": float(np.std(bandwidth))
            },
            "contrast": {
                "mean": [float(np.mean(contrast[i])) for i in range(contrast.shape[0])]
            },
            "rolloff": {
                "mean": float(np.mean(rolloff)),
                "std": float(np.std(rolloff))
            },
            "mfcc": {
                "means": [float(np.mean(mfccs[i])) for i in range(mfccs.shape[0])],
                "stds": [float(np.std(mfccs[i])) for i in range(mfccs.shape[0])]
            },
            "flatness": {
                "mean": float(np.mean(flatness))
            },
            "energy": {
                "mean": float(np.mean(rms)),
                "std": float(np.std(rms))
            },
            "zcr": {
                "mean": float(np.mean(zcr)),
                "std": float(np.std(zcr))
            },
            "temporal_evolution": {
                "spectral_flux": float(spectral_flux),
                "boundaries": boundaries.tolist() if len(boundaries) > 0 else []
            }
        }
    
    def _calculate_energy_level(self, y: np.ndarray) -> float:
        """
        Calculate normalized energy level of the audio.
        
        Args:
            y (np.ndarray): Audio time series
            
        Returns:
            float: Normalized energy level (0-1)
        """
        # RMS energy
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        
        # Normalize to 0-1 range
        energy_level = np.mean(rms) / np.max([np.max(rms), 1e-8])
        
        return float(energy_level)
    
    def _estimate_danceability(self, bpm_info: Dict, tempo_analysis: Dict) -> float:
        """
        Estimate danceability based on tempo and rhythm features.
        
        Args:
            bpm_info (dict): BPM information from extract_bpm
            tempo_analysis (dict): Tempo analysis from analyze_tempo
            
        Returns:
            float: Estimated danceability (0-1)
        """
        # Factors that contribute to danceability:
        # 1. Tempo in dance range (90-130 BPM)
        tempo = bpm_info["tempo"]
        tempo_factor = 1.0 - min(1.0, abs(tempo - 110) / 40)  # Peaks at 110 BPM
        
        # 2. Beat regularity
        regularity_factor = bpm_info["beat_regularity"]
        
        # 3. Tempo stability
        stability_factor = tempo_analysis["stability"]
        
        # 4. Onset density (not too sparse, not too dense)
        density = bpm_info["onset_density"]
        density_factor = 1.0 - min(1.0, abs(density - 2.0) / 2.0)  # Peaks at 2 onsets per second
        
        # Combine factors (weighted average)
        danceability = (
            0.3 * tempo_factor + 
            0.3 * regularity_factor + 
            0.2 * stability_factor + 
            0.2 * density_factor
        )
        
        return float(danceability)
    
    def _estimate_mood_valence(self, y: np.ndarray, sr: int, spectrogram_features: Dict) -> str:
        """
        Estimate mood valence (positive/negative/neutral) based on audio features.
        
        Args:
            y (np.ndarray): Audio time series
            sr (int): Sample rate
            spectrogram_features (dict): Spectrogram features
            
        Returns:
            str: Estimated mood valence
        """
        # Extract key features that correlate with mood valence
        
        # 1. Mode (major/minor) from key detection
        key_info = self.extract_key(y, sr)
        is_major = key_info["mode"] == "major"
        
        # 2. Energy level
        energy = self._calculate_energy_level(y)
        
        # 3. Spectral centroid (brightness)
        brightness = spectrogram_features["centroid"]["mean"] / (sr/2)  # Normalize by Nyquist frequency
        
        # 4. Spectral flatness (tonal vs. noisy)
        flatness = spectrogram_features["flatness"]["mean"]
        
        # Calculate valence score (simple model)
        valence_score = (
            (0.3 * (1.0 if is_major else 0.0)) +  # Major keys are more positive
            (0.3 * energy) +                      # Higher energy is more positive
            (0.3 * brightness) +                  # Brighter sound is more positive
            (0.1 * (1.0 - flatness))              # More tonal (less noisy) is more positive
        )
        
        # Map score to categories
        if valence_score > 0.6:
            return "positive"
        elif valence_score < 0.4:
            return "negative"
        else:
            return "neutral"
    
    def _estimate_mood_arousal(self, y: np.ndarray, sr: int, spectrogram_features: Dict) -> str:
        """
        Estimate mood arousal (high/medium/low) based on audio features.
        
        Args:
            y (np.ndarray): Audio time series
            sr (int): Sample rate
            spectrogram_features (dict): Spectrogram features
            
        Returns:
            str: Estimated mood arousal
        """
        # Extract key features that correlate with arousal
        
        # 1. Energy level
        energy = self._calculate_energy_level(y)
        
        # 2. Tempo
        bpm_info = self.extract_bpm(y, sr)
        tempo = bpm_info["tempo"]
        tempo_factor = min(1.0, tempo / 180.0)  # Normalize to 0-1, capping at 180 BPM
        
        # 3. Onset density
        density = bpm_info["onset_density"]
        density_factor = min(1.0, density / 4.0)  # Normalize to 0-1, capping at 4 onsets per second
        
        # 4. Spectral centroid (brightness)
        brightness = spectrogram_features["centroid"]["mean"] / (sr/2)  # Normalize by Nyquist frequency
        
        # Calculate arousal score (simple model)
        arousal_score = (
            (0.4 * energy) +        # Higher energy is more arousing
            (0.3 * tempo_factor) +  # Faster tempo is more arousing
            (0.2 * density_factor) + # More onsets is more arousing
            (0.1 * brightness)      # Brighter sound is more arousing
        )
        
        # Map score to categories
        if arousal_score > 0.6:
            return "high"
        elif arousal_score < 0.4:
            return "low"
        else:
            return "medium"
