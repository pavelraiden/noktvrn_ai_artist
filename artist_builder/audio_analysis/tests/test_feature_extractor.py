"""
Unit tests for the feature_extractor module.

This module contains tests for the FeatureExtractor class and its methods.
"""

import os
import unittest
import numpy as np
import json
from unittest.mock import patch, MagicMock

# Import the module to test
from ..feature_extractor import FeatureExtractor
from ..utils.audio_loader import load_audio


class TestFeatureExtractor(unittest.TestCase):
    """Test cases for the FeatureExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FeatureExtractor(sr=22050, n_fft=2048, hop_length=512)

        # Create a mock audio signal for testing
        self.mock_audio = np.sin(
            2 * np.pi * 440 * np.arange(0, 3, 1 / 22050)
        )  # 3 seconds of 440 Hz sine wave
        self.mock_sr = 22050

    @patch("librosa.load")
    def test_extract_features_structure(self, mock_load):
        """Test that extract_features returns the expected structure."""
        # Mock the load_audio function to return our test signal
        mock_load.return_value = (self.mock_audio, self.mock_sr)

        # Call the function with a dummy filepath
        features = self.extractor.extract_features("dummy_path.wav")

        # Check that the result is a dictionary with the expected keys
        self.assertIsInstance(features, dict)
        self.assertIn("filepath", features)
        self.assertIn("duration", features)
        self.assertIn("temporal", features)
        self.assertIn("spectral", features)
        self.assertIn("harmonic", features)
        self.assertIn("high_level", features)

        # Check that each feature category is a dictionary
        self.assertIsInstance(features["temporal"], dict)
        self.assertIsInstance(features["spectral"], dict)
        self.assertIsInstance(features["harmonic"], dict)
        self.assertIsInstance(features["high_level"], dict)

    @patch("librosa.load")
    def test_extract_temporal_features(self, mock_load):
        """Test extraction of temporal features."""
        # Mock the load_audio function to return our test signal
        mock_load.return_value = (self.mock_audio, self.mock_sr)

        # Call the function with a dummy filepath
        features = self.extractor.extract_features("dummy_path.wav")

        # Check temporal features
        temporal = features["temporal"]
        self.assertIn("tempo", temporal)
        self.assertIn("beat_count", temporal)
        self.assertIn("beat_regularity", temporal)
        self.assertIn("onset_count", temporal)
        self.assertIn("onset_density", temporal)

        # Check that tempo is a reasonable value
        self.assertGreaterEqual(temporal["tempo"], 0)
        self.assertLessEqual(temporal["tempo"], 300)  # Most music is under 300 BPM

    @patch("librosa.load")
    def test_extract_spectral_features(self, mock_load):
        """Test extraction of spectral features."""
        # Mock the load_audio function to return our test signal
        mock_load.return_value = (self.mock_audio, self.mock_sr)

        # Call the function with a dummy filepath
        features = self.extractor.extract_features("dummy_path.wav")

        # Check spectral features
        spectral = features["spectral"]
        self.assertIn("centroid_mean", spectral)
        self.assertIn("bandwidth_mean", spectral)
        self.assertIn("contrast_mean", spectral)
        self.assertIn("rolloff_mean", spectral)
        self.assertIn("mfcc_means", spectral)

        # Check that centroid is a reasonable value
        self.assertGreaterEqual(spectral["centroid_mean"], 0)

        # Check that MFCCs are a list of the expected length
        self.assertEqual(len(spectral["mfcc_means"]), 13)  # Default n_mfcc=13

    @patch("librosa.load")
    def test_extract_harmonic_features(self, mock_load):
        """Test extraction of harmonic features."""
        # Mock the load_audio function to return our test signal
        mock_load.return_value = (self.mock_audio, self.mock_sr)

        # Call the function with a dummy filepath
        features = self.extractor.extract_features("dummy_path.wav")

        # Check harmonic features
        harmonic = features["harmonic"]
        self.assertIn("key", harmonic)
        self.assertIn("key_strength", harmonic)
        self.assertIn("chroma_mean", harmonic)
        self.assertIn("tonnetz_mean", harmonic)
        self.assertIn("harmonic_ratio", harmonic)

        # Check that key is one of the expected values
        self.assertIn(
            harmonic["key"],
            ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        )

        # Check that key_strength is between 0 and 1
        self.assertGreaterEqual(harmonic["key_strength"], 0)
        self.assertLessEqual(harmonic["key_strength"], 1)

    @patch("librosa.load")
    def test_extract_high_level_features(self, mock_load):
        """Test extraction of high-level features."""
        # Mock the load_audio function to return our test signal
        mock_load.return_value = (self.mock_audio, self.mock_sr)

        # Call the function with a dummy filepath
        features = self.extractor.extract_features("dummy_path.wav")

        # Check high-level features
        high_level = features["high_level"]
        self.assertIn("energy_mean", high_level)
        self.assertIn("energy_level", high_level)
        self.assertIn("zcr_mean", high_level)
        self.assertIn("flatness_mean", high_level)
        self.assertIn("danceability", high_level)
        self.assertIn("mood_valence", high_level)
        self.assertIn("mood_arousal", high_level)

        # Check that energy_level is between 0 and 1
        self.assertGreaterEqual(high_level["energy_level"], 0)
        self.assertLessEqual(high_level["energy_level"], 1)

        # Check that mood_valence is one of the expected values
        self.assertIn(high_level["mood_valence"], ["positive", "neutral", "negative"])

        # Check that mood_arousal is one of the expected values
        self.assertIn(high_level["mood_arousal"], ["high", "medium", "low"])

    @patch("librosa.load")
    def test_error_handling(self, mock_load):
        """Test error handling when file doesn't exist or can't be processed."""
        # Mock the load_audio function to raise an exception
        mock_load.side_effect = Exception("Test error")

        # Call the function with a dummy filepath
        features = self.extractor.extract_features("nonexistent_file.wav")

        # Check that the result indicates an error
        self.assertIn("status", features)
        self.assertEqual(features["status"], "error")
        self.assertIn("message", features)
        self.assertIn("filepath", features)

    def test_is_major_key(self):
        """Test the _is_major_key method."""
        # Create a simple C major scale
        c_major = np.zeros(12)
        for note in [0, 2, 4, 5, 7, 9, 11]:  # C major scale degrees
            c_major[note] = 1.0

        # Create a simple A minor scale
        a_minor = np.zeros(12)
        for note in [9, 11, 0, 2, 4, 5, 7]:  # A minor scale degrees
            a_minor[note] = 1.0

        # Mock the chroma_cqt function to return our test scales
        with patch("librosa.feature.chroma_cqt") as mock_chroma:
            # Test C major
            mock_chroma.return_value = np.array([c_major])
            is_major = self.extractor._is_major_key(self.mock_audio, self.mock_sr)
            self.assertTrue(is_major)

            # Test A minor
            mock_chroma.return_value = np.array([a_minor])
            is_major = self.extractor._is_major_key(self.mock_audio, self.mock_sr)
            self.assertFalse(is_major)


if __name__ == "__main__":
    unittest.main()
