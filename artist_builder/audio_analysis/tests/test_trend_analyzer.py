"""
Unit tests for the trend_analyzer module.

This module contains tests for the TrendAnalyzer class and its methods.
"""

import os
import unittest
import json
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

# Import the module to test
from ..trend_analyzer import TrendAnalyzer


class TestTrendAnalyzer(unittest.TestCase):
    """Test cases for the TrendAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a TrendAnalyzer instance without trend data
        self.analyzer = TrendAnalyzer()

        # Create sample feature data for testing
        self.sample_features1 = {
            "temporal": {"tempo": 120.0},
            "high_level": {
                "energy_level": 0.7,
                "danceability": 0.8,
                "mood_valence": "positive",
                "mood_arousal": "high",
            },
            "harmonic": {"key": "C"},
        }
        self.sample_features2 = {
            "temporal": {"tempo": 130.0},
            "high_level": {
                "energy_level": 0.8,
                "danceability": 0.9,
                "mood_valence": "positive",
                "mood_arousal": "high",
            },
            "harmonic": {"key": "G"},
        }
        self.sample_features3 = {
            "temporal": {"tempo": 110.0},
            "high_level": {
                "energy_level": 0.6,
                "danceability": 0.7,
                "mood_valence": "neutral",
                "mood_arousal": "medium",
            },
            "harmonic": {"key": "C"},
        }
        self.features_collection = [
            self.sample_features1,
            self.sample_features2,
            self.sample_features3,
        ]

        # Create sample trend history
        self.trend_history = [
            {
                "time_period": "2024-Q1",
                "timestamp": "2024-03-31T00:00:00",
                "tempo": {"mean": 115.0},
                "energy": {"mean": 0.65},
                "danceability": {"mean": 0.75},
                "key": {"most_common": "C"},
                "mood": {"most_common_valence": "positive"},
            },
            {
                "time_period": "2024-Q2",
                "timestamp": "2024-06-30T00:00:00",
                "tempo": {"mean": 120.0},
                "energy": {"mean": 0.7},
                "danceability": {"mean": 0.8},
                "key": {"most_common": "G"},
                "mood": {"most_common_valence": "positive"},
            },
            {
                "time_period": "2024-Q3",
                "timestamp": "2024-09-30T00:00:00",
                "tempo": {"mean": 125.0},
                "energy": {"mean": 0.75},
                "danceability": {"mean": 0.85},
                "key": {"most_common": "G"},
                "mood": {"most_common_valence": "positive"},
            },
        ]

    def test_identify_current_trends(self):
        """Test identification of current trends."""
        # Test with sample features collection
        trends = self.analyzer.identify_current_trends(
            self.features_collection, time_period="test_period"
        )

        # Check that the result has the expected structure
        self.assertIsInstance(trends, dict)
        self.assertIn("time_period", trends)
        self.assertEqual(trends["time_period"], "test_period")
        self.assertIn("timestamp", trends)
        self.assertIn("sample_size", trends)
        self.assertEqual(trends["sample_size"], 3)

        # Check specific trend metrics
        self.assertIn("tempo", trends)
        self.assertIn("mean", trends["tempo"])
        self.assertAlmostEqual(trends["tempo"]["mean"], 120.0)

        self.assertIn("energy", trends)
        self.assertIn("mean", trends["energy"])
        self.assertAlmostEqual(trends["energy"]["mean"], 0.7)

        self.assertIn("key", trends)
        self.assertIn("most_common", trends["key"])
        self.assertEqual(trends["key"]["most_common"], "C")

        # Test with empty collection
        empty_trends = self.analyzer.identify_current_trends([])
        self.assertIn("status", empty_trends)
        self.assertEqual(empty_trends["status"], "error")

    def test_calculate_distribution(self):
        """Test the _calculate_distribution helper function."""
        values = [50, 70, 80, 100, 110, 130, 160]
        bins = [60, 90, 120, 150]
        distribution = self.analyzer._calculate_distribution(values, bins)

        # Check that the result is a dictionary
        self.assertIsInstance(distribution, dict)

        # Check expected percentages
        self.assertAlmostEqual(distribution["<60"], 1 / 7)
        self.assertAlmostEqual(distribution["60-90"], 2 / 7)
        self.assertAlmostEqual(distribution["90-120"], 2 / 7)
        self.assertAlmostEqual(distribution["120-150"], 1 / 7)
        self.assertAlmostEqual(distribution[">150"], 1 / 7)

        # Test with empty values
        empty_distribution = self.analyzer._calculate_distribution([], bins)
        self.assertEqual(empty_distribution, {})

    def test_count_occurrences(self):
        """Test the _count_occurrences helper function."""
        values = ["C", "G", "C", "A", "G", "C"]
        occurrences = self.analyzer._count_occurrences(values)

        # Check that the result is a dictionary
        self.assertIsInstance(occurrences, dict)

        # Check expected percentages
        self.assertAlmostEqual(occurrences["C"], 3 / 6)
        self.assertAlmostEqual(occurrences["G"], 2 / 6)
        self.assertAlmostEqual(occurrences["A"], 1 / 6)

        # Test with empty values
        empty_occurrences = self.analyzer._count_occurrences([])
        self.assertEqual(empty_occurrences, {})

    def test_track_trend_evolution(self):
        """Test tracking of trend evolution."""
        # Initialize analyzer with history
        self.analyzer.trend_history = self.trend_history[:2]  # Start with 2 periods

        # Add a new trend
        new_trend = self.trend_history[2]
        evolution = self.analyzer.track_trend_evolution(new_trend)

        # Check that the result has the expected structure
        self.assertIsInstance(evolution, dict)
        self.assertIn("status", evolution)
        self.assertEqual(evolution["status"], "success")
        self.assertIn("evolution_analysis", evolution)
        self.assertIn("current_trend", evolution)

        # Check evolution analysis for tempo
        tempo_evolution = evolution["evolution_analysis"]["tempo"]
        self.assertIn("values", tempo_evolution)
        self.assertEqual(len(tempo_evolution["values"]), 3)
        self.assertIn("change", tempo_evolution)
        self.assertEqual(tempo_evolution["change"]["direction"], "increasing")

        # Test with insufficient history
        self.analyzer.trend_history = [self.trend_history[0]]
        limited_evolution = self.analyzer.track_trend_evolution(self.trend_history[0])
        self.assertEqual(limited_evolution["status"], "limited")

    def test_calculate_change(self):
        """Test the _calculate_change helper function."""
        # Test increasing trend
        increasing = [10, 12, 15]
        change = self.analyzer._calculate_change(increasing)
        self.assertEqual(change["direction"], "increasing")
        self.assertAlmostEqual(change["magnitude"], 5.0)
        self.assertAlmostEqual(change["rate"], 2.5)

        # Test decreasing trend
        decreasing = [20, 18, 15]
        change = self.analyzer._calculate_change(decreasing)
        self.assertEqual(change["direction"], "decreasing")
        self.assertAlmostEqual(change["magnitude"], -5.0)
        self.assertAlmostEqual(change["rate"], -2.5)

        # Test stable trend
        stable = [10, 10.1, 10.2]
        change = self.analyzer._calculate_change(stable)
        self.assertEqual(change["direction"], "stable")

        # Test with insufficient data
        insufficient = [10]
        change = self.analyzer._calculate_change(insufficient)
        self.assertEqual(change["direction"], "stable")
        self.assertEqual(change["magnitude"], 0.0)

    def test_calculate_stability(self):
        """Test the _calculate_stability helper function."""
        # Test stable sequence
        stable = ["C", "C", "C", "C"]
        stability = self.analyzer._calculate_stability(stable)
        self.assertTrue(stability["is_stable"])
        self.assertEqual(stability["changes"], 0)
        self.assertEqual(stability["most_frequent"], "C")

        # Test unstable sequence
        unstable = ["C", "G", "A", "C"]
        stability = self.analyzer._calculate_stability(unstable)
        self.assertFalse(stability["is_stable"])
        self.assertEqual(stability["changes"], 3)
        self.assertEqual(stability["most_frequent"], "C")

        # Test with insufficient data
        insufficient = ["C"]
        stability = self.analyzer._calculate_stability(insufficient)
        self.assertTrue(stability["is_stable"])
        self.assertEqual(stability["changes"], 0)
        self.assertEqual(stability["most_frequent"], "C")

    def test_predict_future_trends(self):
        """Test prediction of future trends."""
        # Initialize analyzer with history
        self.analyzer.trend_history = self.trend_history

        # Predict future trends
        predictions = self.analyzer.predict_future_trends(prediction_periods=2)

        # Check that the result has the expected structure
        self.assertIsInstance(predictions, dict)
        self.assertIn("status", predictions)
        self.assertEqual(predictions["status"], "success")
        self.assertIn("predictions", predictions)

        # Check predictions structure
        preds = predictions["predictions"]
        self.assertIn("tempo", preds)
        self.assertIn("energy", preds)
        self.assertIn("danceability", preds)
        self.assertIn("prediction_periods", preds)
        self.assertEqual(preds["prediction_periods"], 2)
        self.assertIn("confidence", preds)

        # Check that predictions are lists of the correct length
        self.assertEqual(len(preds["tempo"]), 2)
        self.assertEqual(len(preds["energy"]), 2)
        self.assertEqual(len(preds["danceability"]), 2)

        # Test with insufficient history
        self.analyzer.trend_history = self.trend_history[:2]
        insufficient_predictions = self.analyzer.predict_future_trends()
        self.assertEqual(insufficient_predictions["status"], "error")

    def test_predict_future_values(self):
        """Test the _predict_future_values helper function."""
        # Test linear trend
        history = [10, 12, 14]
        predictions = self.analyzer._predict_future_values(history, periods=2)
        self.assertAlmostEqual(predictions[0], 16.0)
        self.assertAlmostEqual(predictions[1], 18.0)

        # Test constant trend
        history = [10, 10, 10]
        predictions = self.analyzer._predict_future_values(history, periods=1)
        self.assertAlmostEqual(predictions[0], 10.0)

        # Test with insufficient data
        history = [10]
        predictions = self.analyzer._predict_future_values(history, periods=1)
        self.assertEqual(predictions[0], 10.0)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_init_with_trend_data(self, mock_json_load, mock_file_open):
        """Test initialization with trend data."""
        # Mock the trend data
        mock_trend_data = {
            "current_trends": {"tempo": {"mean": 120.0}},
            "trend_history": self.trend_history,
        }
        mock_json_load.return_value = mock_trend_data

        # Create a TrendAnalyzer with trend data
        analyzer = TrendAnalyzer(trend_data_path="dummy_path.json")

        # Check that the trend data was loaded
        self.assertEqual(analyzer.trend_data, mock_trend_data["current_trends"])
        self.assertEqual(analyzer.trend_history, mock_trend_data["trend_history"])

        # Check that the file was opened
        mock_file_open.assert_called_once_with("dummy_path.json", "r")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_trend_data(self, mock_json_dump, mock_file_open):
        """Test saving trend data."""
        # Set some trend data
        self.analyzer.trend_data = {"tempo": {"mean": 125.0}}
        self.analyzer.trend_history = self.trend_history

        # Test saving trend data
        result = self.analyzer.save_trend_data("dummy_path.json")

        # Check that the result is True
        self.assertTrue(result)

        # Check that the file was opened
        mock_file_open.assert_called_once_with("dummy_path.json", "w")

        # Check that json.dump was called
        mock_json_dump.assert_called_once()

        # Check the structure of the saved data
        saved_data = mock_json_dump.call_args[0][0]
        self.assertIn("current_trends", saved_data)
        self.assertIn("trend_history", saved_data)
        self.assertIn("last_updated", saved_data)


if __name__ == "__main__":
    unittest.main()
