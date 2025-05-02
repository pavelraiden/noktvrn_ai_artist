"""
Trend Analyzer Module for Audio Analysis

This module provides functionality to analyze musical trends based on
collections of audio features. It includes algorithms for trend identification,
evolution tracking, and prediction.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional
import json
import os
from datetime import datetime


class TrendAnalyzer:
    """
    Class for analyzing musical trends based on collections of audio features.
    """

    def __init__(self, trend_data_path: Optional[str] = None):
        """
        Initialize the TrendAnalyzer with optional trend data.

        Args:
            trend_data_path (str, optional): Path to trend data
        """
        self.trend_data = {}
        self.trend_history = []

        if trend_data_path and os.path.exists(trend_data_path):
            try:
                with open(trend_data_path, "r") as f:
                    data = json.load(f)
                    self.trend_data = data.get("current_trends", {})
                    self.trend_history = data.get("trend_history", [])
            except Exception as e:
                print(f"Warning: Could not load trend data: {str(e)}")

    def identify_current_trends(
        self, features_collection: List[Dict], time_period: str = "current"
    ) -> Dict:
        """
        Identify current trends from a collection of audio features.

        Args:
            features_collection (list): List of feature dictionaries from multiple tracks
            time_period (str): Time period label for the trends

        Returns:
            dict: Dictionary containing identified trends
        """
        if not features_collection:
            return {
                "status": "error",
                "message": "No features provided for trend analysis",
            }

        # Extract key features for trend analysis
        tempos = []
        energy_levels = []
        danceability_levels = []
        keys = []
        moods = []

        for features in features_collection:
            # Extract temporal features
            tempo = features.get("temporal", {}).get("tempo")
            if tempo is not None:
                tempos.append(tempo)

            # Extract energy level
            energy = features.get("high_level", {}).get("energy_level")
            if energy is not None:
                energy_levels.append(energy)

            # Extract danceability
            danceability = features.get("high_level", {}).get("danceability")
            if danceability is not None:
                danceability_levels.append(danceability)

            # Extract key
            key = features.get("harmonic", {}).get("key")
            if key is not None:
                keys.append(key)

            # Extract mood
            mood_valence = features.get("high_level", {}).get("mood_valence")
            mood_arousal = features.get("high_level", {}).get("mood_arousal")
            if mood_valence and mood_arousal:
                moods.append((mood_valence, mood_arousal))

        # Calculate trend metrics
        trends = {
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "sample_size": len(features_collection),
            "tempo": {
                "mean": float(np.mean(tempos)) if tempos else None,
                "median": float(np.median(tempos)) if tempos else None,
                "std": float(np.std(tempos)) if tempos else None,
                "distribution": self._calculate_distribution(
                    tempos, [60, 90, 120, 150, 180]
                ),
            },
            "energy": {
                "mean": float(np.mean(energy_levels)) if energy_levels else None,
                "median": float(np.median(energy_levels)) if energy_levels else None,
                "std": float(np.std(energy_levels)) if energy_levels else None,
                "distribution": self._calculate_distribution(
                    energy_levels, [0.2, 0.4, 0.6, 0.8]
                ),
            },
            "danceability": {
                "mean": (
                    float(np.mean(danceability_levels)) if danceability_levels else None
                ),
                "median": (
                    float(np.median(danceability_levels))
                    if danceability_levels
                    else None
                ),
                "std": (
                    float(np.std(danceability_levels)) if danceability_levels else None
                ),
                "distribution": self._calculate_distribution(
                    danceability_levels, [0.2, 0.4, 0.6, 0.8]
                ),
            },
            "key": {
                "most_common": max(set(keys), key=keys.count) if keys else None,
                "distribution": self._count_occurrences(keys),
            },
            "mood": {
                "most_common_valence": (
                    max(set([m[0] for m in moods]), key=[m[0] for m in moods].count)
                    if moods
                    else None
                ),
                "most_common_arousal": (
                    max(set([m[1] for m in moods]), key=[m[1] for m in moods].count)
                    if moods
                    else None
                ),
                "valence_distribution": (
                    self._count_occurrences([m[0] for m in moods]) if moods else {}
                ),
                "arousal_distribution": (
                    self._count_occurrences([m[1] for m in moods]) if moods else {}
                ),
            },
        }

        return trends

    def _calculate_distribution(self, values: List[float], bins: List[float]) -> Dict:
        """
        Calculate distribution of values across bins.

        Args:
            values (list): List of numerical values
            bins (list): List of bin edges

        Returns:
            dict: Dictionary with bin labels and percentages
        """
        if not values:
            return {}

        # Create bin labels
        bin_labels = [f"<{bins[0]}"]
        for i in range(len(bins) - 1):
            bin_labels.append(f"{bins[i]}-{bins[i+1]}")
        bin_labels.append(f">{bins[-1]}")

        # Count values in each bin
        counts = [0] * (len(bins) + 1)
        for value in values:
            bin_index = 0
            while bin_index < len(bins) and value >= bins[bin_index]:
                bin_index += 1
            counts[bin_index] += 1

        # Calculate percentages
        total = len(values)
        percentages = [count / total for count in counts]

        # Create distribution dictionary
        distribution = {
            label: float(percentage)
            for label, percentage in zip(bin_labels, percentages)
        }

        return distribution

    def _count_occurrences(self, values: List) -> Dict:
        """
        Count occurrences of each unique value.

        Args:
            values (list): List of values

        Returns:
            dict: Dictionary with values and their frequencies
        """
        if not values:
            return {}

        # Count occurrences
        counts = {}
        for value in values:
            if value in counts:
                counts[value] += 1
            else:
                counts[value] = 1

        # Calculate percentages
        total = len(values)
        distribution = {str(value): count / total for value, count in counts.items()}

        return distribution

    def track_trend_evolution(self, new_trend: Dict) -> Dict:
        """
        Track the evolution of trends over time.

        Args:
            new_trend (dict): New trend data to add to history

        Returns:
            dict: Dictionary containing trend evolution analysis
        """
        # Add new trend to history
        self.trend_history.append(new_trend)

        # If we don't have enough history, return limited analysis
        if len(self.trend_history) < 2:
            return {
                "status": "limited",
                "message": "Not enough trend history for evolution analysis",
                "current_trend": new_trend,
            }

        # Sort trend history by timestamp
        sorted_history = sorted(
            self.trend_history, key=lambda x: x.get("timestamp", "")
        )

        # Extract key metrics for evolution analysis
        tempo_evolution = []
        energy_evolution = []
        danceability_evolution = []
        key_evolution = []
        mood_valence_evolution = []

        for trend in sorted_history:
            # Extract tempo
            tempo_mean = trend.get("tempo", {}).get("mean")
            if tempo_mean is not None:
                tempo_evolution.append(tempo_mean)

            # Extract energy
            energy_mean = trend.get("energy", {}).get("mean")
            if energy_mean is not None:
                energy_evolution.append(energy_mean)

            # Extract danceability
            danceability_mean = trend.get("danceability", {}).get("mean")
            if danceability_mean is not None:
                danceability_evolution.append(danceability_mean)

            # Extract key
            key_most_common = trend.get("key", {}).get("most_common")
            if key_most_common is not None:
                key_evolution.append(key_most_common)

            # Extract mood valence
            mood_valence = trend.get("mood", {}).get("most_common_valence")
            if mood_valence is not None:
                mood_valence_evolution.append(mood_valence)

        # Calculate evolution metrics
        evolution_analysis = {
            "tempo": {
                "values": tempo_evolution,
                "change": self._calculate_change(tempo_evolution),
            },
            "energy": {
                "values": energy_evolution,
                "change": self._calculate_change(energy_evolution),
            },
            "danceability": {
                "values": danceability_evolution,
                "change": self._calculate_change(danceability_evolution),
            },
            "key": {
                "values": key_evolution,
                "stability": self._calculate_stability(key_evolution),
            },
            "mood_valence": {
                "values": mood_valence_evolution,
                "stability": self._calculate_stability(mood_valence_evolution),
            },
        }

        return {
            "status": "success",
            "evolution_analysis": evolution_analysis,
            "current_trend": new_trend,
        }

    def _calculate_change(self, values: List[float]) -> Dict:
        """
        Calculate change metrics for a series of values.

        Args:
            values (list): List of numerical values

        Returns:
            dict: Dictionary with change metrics
        """
        if len(values) < 2:
            return {"direction": "stable", "magnitude": 0.0, "rate": 0.0}

        # Calculate absolute and percentage changes
        absolute_change = values[-1] - values[0]
        percentage_change = absolute_change / values[0] if values[0] != 0 else 0

        # Calculate rate of change (average change per period)
        rate_of_change = absolute_change / (len(values) - 1)

        # Determine direction
        if absolute_change > 0.05 * values[0]:  # 5% threshold for significance
            direction = "increasing"
        elif absolute_change < -0.05 * values[0]:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "magnitude": float(absolute_change),
            "percentage": float(percentage_change),
            "rate": float(rate_of_change),
        }

    def _calculate_stability(self, values: List) -> Dict:
        """
        Calculate stability metrics for a series of categorical values.

        Args:
            values (list): List of categorical values

        Returns:
            dict: Dictionary with stability metrics
        """
        if len(values) < 2:
            return {
                "is_stable": True,
                "changes": 0,
                "most_frequent": values[0] if values else None,
            }

        # Count changes
        changes = sum(1 for i in range(1, len(values)) if values[i] != values[i - 1])

        # Calculate stability percentage
        stability_percentage = 1.0 - (changes / (len(values) - 1))

        # Count occurrences of each value
        value_counts = {}
        for value in values:
            if value in value_counts:
                value_counts[value] += 1
            else:
                value_counts[value] = 1

        # Find most frequent value
        most_frequent = (
            max(value_counts.items(), key=lambda x: x[1])[0] if value_counts else None
        )

        return {
            "is_stable": stability_percentage > 0.7,  # 70% threshold for stability
            "stability_percentage": float(stability_percentage),
            "changes": changes,
            "most_frequent": most_frequent,
        }

    def predict_future_trends(self, prediction_periods: int = 1) -> Dict:
        """
        Predict future trends based on historical data.

        Args:
            prediction_periods (int): Number of periods to predict into the future

        Returns:
            dict: Dictionary containing trend predictions
        """
        if len(self.trend_history) < 3:
            return {
                "status": "error",
                "message": "Not enough trend history for prediction (minimum 3 periods required)",
            }

        # Sort trend history by timestamp
        sorted_history = sorted(
            self.trend_history, key=lambda x: x.get("timestamp", "")
        )

        # Extract key metrics for prediction
        tempo_history = []
        energy_history = []
        danceability_history = []

        for trend in sorted_history:
            # Extract tempo
            tempo_mean = trend.get("tempo", {}).get("mean")
            if tempo_mean is not None:
                tempo_history.append(tempo_mean)

            # Extract energy
            energy_mean = trend.get("energy", {}).get("mean")
            if energy_mean is not None:
                energy_history.append(energy_mean)

            # Extract danceability
            danceability_mean = trend.get("danceability", {}).get("mean")
            if danceability_mean is not None:
                danceability_history.append(danceability_mean)

        # Predict future values using simple linear regression
        tempo_prediction = self._predict_future_values(
            tempo_history, prediction_periods
        )
        energy_prediction = self._predict_future_values(
            energy_history, prediction_periods
        )
        danceability_prediction = self._predict_future_values(
            danceability_history, prediction_periods
        )

        # Create prediction dictionary
        predictions = {
            "tempo": tempo_prediction,
            "energy": energy_prediction,
            "danceability": danceability_prediction,
            "prediction_periods": prediction_periods,
            "confidence": self._calculate_prediction_confidence(),
        }

        return {"status": "success", "predictions": predictions}

    def _predict_future_values(self, history: List[float], periods: int) -> List[float]:
        """
        Predict future values using simple linear regression.

        Args:
            history (list): List of historical values
            periods (int): Number of periods to predict

        Returns:
            list: List of predicted values
        """
        if not history or len(history) < 2:
            return [history[-1]] * periods if history else [0] * periods

        # Create x and y arrays for regression
        x = np.array(range(len(history))).reshape(-1, 1)
        y = np.array(history)

        # Calculate slope and intercept
        n = len(history)
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean

        # Predict future values
        predictions = []
        for i in range(1, periods + 1):
            next_x = len(history) + i - 1
            next_y = slope * next_x + intercept
            predictions.append(float(next_y))

        return predictions

    def _calculate_prediction_confidence(self) -> float:
        """
        Calculate confidence level for predictions.

        Returns:
            float: Confidence level between 0 and 1
        """
        # This is a simplified confidence calculation
        # A real implementation would use statistical methods

        # More history = higher confidence, up to a point
        history_factor = min(len(self.trend_history) / 10, 1.0)

        # More consistent trends = higher confidence
        consistency_factor = 0.7  # Default medium-high consistency

        # Combine factors
        confidence = history_factor * consistency_factor

        return float(confidence)

    def save_trend_data(self, trend_data_path: str) -> bool:
        """
        Save trend data to file.

        Args:
            trend_data_path (str): Path to save trend data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare data for saving
            data = {
                "current_trends": self.trend_data,
                "trend_history": self.trend_history,
                "last_updated": datetime.now().isoformat(),
            }

            # Save data
            with open(trend_data_path, "w") as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving trend data: {str(e)}")
            return False
