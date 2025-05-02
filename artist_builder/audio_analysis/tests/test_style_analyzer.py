"""
Unit tests for the style_analyzer module.

This module contains tests for the StyleAnalyzer class and its methods.
"""

import os
import unittest
import json
from unittest.mock import patch, MagicMock, mock_open

# Import the module to test
from ..style_analyzer import StyleAnalyzer


class TestStyleAnalyzer(unittest.TestCase):
    """Test cases for the StyleAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a StyleAnalyzer instance without reference data
        self.analyzer = StyleAnalyzer()

        # Create sample feature data for testing
        self.sample_features = {
            "temporal": {
                "tempo": 120.5,
                "beat_count": 100,
                "beat_regularity": 0.05,
                "onset_count": 150,
                "onset_density": 0.8,
            },
            "spectral": {
                "centroid_mean": 2500.0,
                "centroid_std": 500.0,
                "bandwidth_mean": 1800.0,
                "bandwidth_std": 300.0,
                "contrast_mean": [0.8, 0.6, 0.4, 0.3, 0.2, 0.1],
                "rolloff_mean": 4000.0,
                "rolloff_std": 800.0,
                "mfcc_means": [
                    10.0,
                    5.0,
                    2.0,
                    1.0,
                    0.5,
                    0.2,
                    0.1,
                    0.05,
                    0.02,
                    0.01,
                    0.005,
                    0.002,
                    0.001,
                ],
                "mfcc_stds": [
                    2.0,
                    1.0,
                    0.5,
                    0.2,
                    0.1,
                    0.05,
                    0.02,
                    0.01,
                    0.005,
                    0.002,
                    0.001,
                    0.0005,
                    0.0002,
                ],
            },
            "harmonic": {
                "key": "C",
                "key_strength": 0.7,
                "chroma_mean": [
                    0.8,
                    0.2,
                    0.6,
                    0.1,
                    0.7,
                    0.3,
                    0.1,
                    0.9,
                    0.2,
                    0.5,
                    0.1,
                    0.4,
                ],
                "chroma_std": [
                    0.2,
                    0.1,
                    0.15,
                    0.05,
                    0.18,
                    0.12,
                    0.08,
                    0.22,
                    0.1,
                    0.14,
                    0.06,
                    0.13,
                ],
                "tonnetz_mean": [0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
                "harmonic_ratio": 0.6,
            },
            "high_level": {
                "energy_mean": 0.7,
                "energy_std": 0.2,
                "energy_level": 0.7,
                "zcr_mean": 0.3,
                "zcr_std": 0.1,
                "flatness_mean": 0.2,
                "danceability": 0.8,
                "mood_valence": "positive",
                "mood_arousal": "high",
            },
        }

        # Create a second sample with different features
        self.sample_features2 = {
            "temporal": {
                "tempo": 90.0,
                "beat_count": 80,
                "beat_regularity": 0.1,
                "onset_count": 100,
                "onset_density": 0.5,
            },
            "spectral": {
                "centroid_mean": 1500.0,
                "centroid_std": 300.0,
                "bandwidth_mean": 1200.0,
                "bandwidth_std": 200.0,
                "contrast_mean": [0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
                "rolloff_mean": 3000.0,
                "rolloff_std": 600.0,
                "mfcc_means": [
                    8.0,
                    4.0,
                    1.5,
                    0.8,
                    0.4,
                    0.15,
                    0.08,
                    0.04,
                    0.015,
                    0.008,
                    0.004,
                    0.0015,
                    0.0008,
                ],
                "mfcc_stds": [
                    1.5,
                    0.8,
                    0.4,
                    0.15,
                    0.08,
                    0.04,
                    0.015,
                    0.008,
                    0.004,
                    0.0015,
                    0.0008,
                    0.0004,
                    0.0001,
                ],
            },
            "harmonic": {
                "key": "A",
                "key_strength": 0.6,
                "chroma_mean": [
                    0.5,
                    0.3,
                    0.4,
                    0.2,
                    0.5,
                    0.4,
                    0.2,
                    0.6,
                    0.3,
                    0.8,
                    0.2,
                    0.3,
                ],
                "chroma_std": [
                    0.15,
                    0.12,
                    0.13,
                    0.08,
                    0.15,
                    0.14,
                    0.09,
                    0.16,
                    0.12,
                    0.2,
                    0.08,
                    0.1,
                ],
                "tonnetz_mean": [0.4, 0.3, 0.25, 0.15, 0.08, 0.05],
                "harmonic_ratio": 0.7,
            },
            "high_level": {
                "energy_mean": 0.4,
                "energy_std": 0.15,
                "energy_level": 0.4,
                "zcr_mean": 0.2,
                "zcr_std": 0.08,
                "flatness_mean": 0.15,
                "danceability": 0.5,
                "mood_valence": "neutral",
                "mood_arousal": "medium",
            },
        }

        # Create sample trend features for testing
        self.trend_features = [self.sample_features, self.sample_features2]

    def test_classify_genre(self):
        """Test genre classification."""
        # Test with electronic music features
        electronic_features = self.sample_features.copy()
        electronic_features["temporal"]["tempo"] = 130
        electronic_features["spectral"]["centroid_mean"] = 3000

        result = self.analyzer.classify_genre(electronic_features)

        # Check that the result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn("primary_genre", result)
        self.assertIn("confidence", result)
        self.assertIn("all_genres", result)

        # Check that confidence is between 0 and 1
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

        # Check that all_genres is a list of dictionaries
        self.assertIsInstance(result["all_genres"], list)
        if result["all_genres"]:
            self.assertIsInstance(result["all_genres"][0], dict)
            self.assertIn("genre", result["all_genres"][0])
            self.assertIn("confidence", result["all_genres"][0])

        # Test with classical music features
        classical_features = self.sample_features.copy()
        classical_features["harmonic"]["harmonic_ratio"] = 0.9

        result = self.analyzer.classify_genre(classical_features)

        # Check that the result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn("primary_genre", result)

        # Test with empty features
        empty_features = {}
        result = self.analyzer.classify_genre(empty_features)

        # Check that the result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn("primary_genre", result)
        self.assertEqual(result["primary_genre"], "Unknown")

    def test_calculate_similarity(self):
        """Test similarity calculation between tracks."""
        # Calculate similarity between identical features
        similarity = self.analyzer.calculate_similarity(
            self.sample_features, self.sample_features
        )

        # Similarity to self should be 1.0
        self.assertEqual(similarity, 1.0)

        # Calculate similarity between different features
        similarity = self.analyzer.calculate_similarity(
            self.sample_features, self.sample_features2
        )

        # Similarity should be between 0 and 1
        self.assertGreaterEqual(similarity, 0)
        self.assertLessEqual(similarity, 1)

        # Similarity should be less than 1.0 for different features
        self.assertLess(similarity, 1.0)

        # Test with empty features
        similarity = self.analyzer.calculate_similarity({}, {})
        self.assertEqual(similarity, 0.0)

    def test_identify_style_elements(self):
        """Test identification of style elements."""
        # Test with sample features
        style_elements = self.analyzer.identify_style_elements(self.sample_features)

        # Check that the result has the expected structure
        self.assertIsInstance(style_elements, dict)
        self.assertIn("tempo_class", style_elements)
        self.assertIn("energy_class", style_elements)
        self.assertIn("mood", style_elements)
        self.assertIn("complexity", style_elements)
        self.assertIn("instrumentation", style_elements)

        # Check that tempo_class is one of the expected values
        self.assertIn(style_elements["tempo_class"], ["Slow", "Medium", "Fast"])

        # Check that energy_class is one of the expected values
        self.assertIn(style_elements["energy_class"], ["Low", "Medium", "High"])

        # Test with different features
        style_elements2 = self.analyzer.identify_style_elements(self.sample_features2)

        # Check that the result has the expected structure
        self.assertIsInstance(style_elements2, dict)

        # Test with empty features
        style_elements_empty = self.analyzer.identify_style_elements({})
        self.assertIsInstance(style_elements_empty, dict)

    def test_analyze_trend_compatibility(self):
        """Test trend compatibility analysis."""
        # Test with sample features and trend features
        compatibility = self.analyzer.analyze_trend_compatibility(
            self.sample_features, self.trend_features
        )

        # Check that the result has the expected structure
        self.assertIsInstance(compatibility, dict)
        self.assertIn("compatibility_score", compatibility)
        self.assertIn("matching_aspects", compatibility)
        self.assertIn("non_matching_aspects", compatibility)
        self.assertIn("recommendation", compatibility)

        # Check that compatibility_score is between 0 and 1
        self.assertGreaterEqual(compatibility["compatibility_score"], 0)
        self.assertLessEqual(compatibility["compatibility_score"], 1)

        # Check that matching_aspects and non_matching_aspects are lists
        self.assertIsInstance(compatibility["matching_aspects"], list)
        self.assertIsInstance(compatibility["non_matching_aspects"], list)

        # Test with empty trend features
        compatibility_empty = self.analyzer.analyze_trend_compatibility(
            self.sample_features, []
        )
        self.assertIsInstance(compatibility_empty, dict)
        self.assertIn("compatibility_score", compatibility_empty)
        self.assertEqual(compatibility_empty["compatibility_score"], 0.0)

        # Test with empty features
        compatibility_empty2 = self.analyzer.analyze_trend_compatibility(
            {}, self.trend_features
        )
        self.assertIsInstance(compatibility_empty2, dict)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_init_with_reference_data(self, mock_json_load, mock_file_open):
        """Test initialization with reference data."""
        # Mock the reference data
        mock_reference_data = {
            "Electronic": [self.sample_features],
            "Classical": [self.sample_features2],
        }
        mock_json_load.return_value = mock_reference_data

        # Create a StyleAnalyzer with reference data
        analyzer = StyleAnalyzer(reference_data_path="dummy_path.json")

        # Check that the reference data was loaded
        self.assertEqual(analyzer.reference_data, mock_reference_data)

        # Check that the file was opened
        mock_file_open.assert_called_once_with("dummy_path.json", "r")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.path.exists")
    def test_save_as_reference(self, mock_exists, mock_json_dump, mock_file_open):
        """Test saving features as reference."""
        # Mock os.path.exists to return False
        mock_exists.return_value = False

        # Test saving features as reference
        result = self.analyzer.save_as_reference(
            self.sample_features, "Electronic", "dummy_path.json"
        )

        # Check that the result is True
        self.assertTrue(result)

        # Check that the file was opened
        mock_file_open.assert_called_once_with("dummy_path.json", "w")

        # Check that json.dump was called
        mock_json_dump.assert_called_once()

        # Mock os.path.exists to return True and test updating existing reference
        mock_exists.return_value = True
        mock_json_dump.reset_mock()
        mock_file_open.reset_mock()

        # Mock json.load to return existing reference data
        with patch("json.load") as mock_json_load:
            mock_json_load.return_value = {"Electronic": [self.sample_features2]}

            # Test updating existing reference
            result = self.analyzer.save_as_reference(
                self.sample_features, "Electronic", "dummy_path.json"
            )

            # Check that the result is True
            self.assertTrue(result)

            # Check that the file was opened twice (once for reading, once for writing)
            self.assertEqual(mock_file_open.call_count, 2)

            # Check that json.dump was called
            mock_json_dump.assert_called_once()


if __name__ == "__main__":
    unittest.main()
