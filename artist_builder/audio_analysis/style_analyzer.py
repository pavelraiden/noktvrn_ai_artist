"""
Style Analyzer Module for Audio Analysis

This module provides functionality to analyze musical styles based on
extracted audio features. It includes algorithms for style classification,
similarity analysis, and trend identification.
"""

import numpy as np
from typing import Dict, List, Tuple, Union, Optional
import json
import os


class StyleAnalyzer:
    """
    Class for analyzing musical styles based on extracted audio features.
    """

    def __init__(self, reference_data_path: Optional[str] = None):
        """
        Initialize the StyleAnalyzer with optional reference data.

        Args:
            reference_data_path (str, optional): Path to reference data for style comparison
        """
        self.reference_data = {}
        if reference_data_path and os.path.exists(reference_data_path):
            try:
                with open(reference_data_path, "r") as f:
                    self.reference_data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load reference data: {str(e)}")

    def classify_genre(self, features: Dict) -> Dict:
        """
        Classify the genre of a track based on its features.

        Args:
            features (dict): Dictionary of extracted audio features

        Returns:
            dict: Dictionary containing genre classification results
        """
        # This is a simplified implementation
        # A real implementation would use a trained classifier model

        # Extract relevant features for classification
        tempo = features.get("temporal", {}).get("tempo", 0)
        energy = features.get("high_level", {}).get("energy_level", 0)
        harmonic_ratio = features.get("harmonic", {}).get("harmonic_ratio", 0)
        spectral_centroid = features.get("spectral", {}).get("centroid_mean", 0)

        # Simple rule-based classification
        genres = []
        confidences = []

        # Electronic music often has high tempo and spectral centroid
        if tempo > 120 and spectral_centroid > 2000:
            genres.append("Electronic")
            confidences.append(0.7)

        # Rock music often has medium-high energy and harmonic ratio
        if 0.5 < energy < 0.8 and 0.4 < harmonic_ratio < 0.7:
            genres.append("Rock")
            confidences.append(0.6)

        # Classical music often has high harmonic ratio
        if harmonic_ratio > 0.7:
            genres.append("Classical")
            confidences.append(0.65)

        # Hip-hop often has low tempo and high energy
        if tempo < 100 and energy > 0.6:
            genres.append("Hip-Hop")
            confidences.append(0.55)

        # Jazz often has medium tempo and high harmonic complexity
        if 90 < tempo < 140 and harmonic_ratio > 0.6:
            genres.append("Jazz")
            confidences.append(0.5)

        # If no genres were identified, add "Unknown"
        if not genres:
            genres.append("Unknown")
            confidences.append(0.3)

        # Sort by confidence
        sorted_genres = [x for _, x in sorted(zip(confidences, genres), reverse=True)]
        sorted_confidences = sorted(confidences, reverse=True)

        return {
            "primary_genre": sorted_genres[0] if sorted_genres else "Unknown",
            "confidence": sorted_confidences[0] if sorted_confidences else 0.0,
            "all_genres": [
                {"genre": g, "confidence": c}
                for g, c in zip(sorted_genres, sorted_confidences)
            ],
        }

    def calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate similarity between two tracks based on their features.

        Args:
            features1 (dict): Features of the first track
            features2 (dict): Features of the second track

        Returns:
            float: Similarity score between 0 and 1
        """
        # Extract key features for comparison
        features_to_compare = [
            ("temporal", "tempo"),
            ("high_level", "energy_level"),
            ("harmonic", "harmonic_ratio"),
            ("spectral", "centroid_mean"),
            ("high_level", "danceability"),
        ]

        # Calculate normalized Euclidean distance
        squared_diffs = []
        weights = [1.0, 1.5, 2.0, 1.0, 1.5]  # Different weights for different features

        for i, (category, feature) in enumerate(features_to_compare):
            val1 = features1.get(category, {}).get(feature, 0)
            val2 = features2.get(category, {}).get(feature, 0)

            # Normalize the values based on typical ranges
            if feature == "tempo":
                val1 = val1 / 200.0  # Assuming max tempo around 200 BPM
                val2 = val2 / 200.0

            squared_diff = (val1 - val2) ** 2 * weights[i]
            squared_diffs.append(squared_diff)

        # Calculate similarity score (1 - normalized distance)
        if squared_diffs:
            distance = np.sqrt(sum(squared_diffs) / sum(weights))
            similarity = 1.0 - min(
                distance, 1.0
            )  # Ensure similarity is between 0 and 1
        else:
            similarity = 0.0

        return similarity

    def identify_style_elements(self, features: Dict) -> Dict:
        """
        Identify key style elements from audio features.

        Args:
            features (dict): Dictionary of extracted audio features

        Returns:
            dict: Dictionary containing identified style elements
        """
        style_elements = {}

        # Tempo classification
        tempo = features.get("temporal", {}).get("tempo", 0)
        if tempo < 70:
            style_elements["tempo_class"] = "Slow"
        elif tempo < 120:
            style_elements["tempo_class"] = "Medium"
        else:
            style_elements["tempo_class"] = "Fast"

        # Energy classification
        energy = features.get("high_level", {}).get("energy_level", 0)
        if energy < 0.3:
            style_elements["energy_class"] = "Low"
        elif energy < 0.7:
            style_elements["energy_class"] = "Medium"
        else:
            style_elements["energy_class"] = "High"

        # Mood classification
        valence = features.get("high_level", {}).get("mood_valence", "neutral")
        arousal = features.get("high_level", {}).get("mood_arousal", "medium")

        mood_map = {
            ("positive", "high"): "Energetic/Happy",
            ("positive", "medium"): "Pleasant/Positive",
            ("positive", "low"): "Calm/Peaceful",
            ("neutral", "high"): "Exciting/Tense",
            ("neutral", "medium"): "Neutral/Balanced",
            ("neutral", "low"): "Relaxed/Chill",
            ("negative", "high"): "Angry/Intense",
            ("negative", "medium"): "Sad/Melancholic",
            ("negative", "low"): "Depressed/Dark",
        }

        style_elements["mood"] = mood_map.get((valence, arousal), "Unknown")

        # Complexity assessment
        spectral_complexity = features.get("spectral", {}).get("contrast_mean", [0])[0]
        harmonic_complexity = features.get("harmonic", {}).get("tonnetz_mean", [0])[0]

        if spectral_complexity + harmonic_complexity < 0.3:
            style_elements["complexity"] = "Simple"
        elif spectral_complexity + harmonic_complexity < 0.7:
            style_elements["complexity"] = "Moderate"
        else:
            style_elements["complexity"] = "Complex"

        # Instrumentation guess based on spectral features
        centroid = features.get("spectral", {}).get("centroid_mean", 0)
        flatness = features.get("high_level", {}).get("flatness_mean", 0)

        if centroid > 3000 and flatness > 0.3:
            style_elements["instrumentation"] = "Electronic/Synthetic"
        elif centroid < 1500 and flatness < 0.2:
            style_elements["instrumentation"] = "Acoustic/Organic"
        else:
            style_elements["instrumentation"] = "Mixed"

        return style_elements

    def analyze_trend_compatibility(
        self, features: Dict, trend_features: List[Dict]
    ) -> Dict:
        """
        Analyze how compatible a track is with current trends.

        Args:
            features (dict): Features of the track to analyze
            trend_features (list): List of features representing current trends

        Returns:
            dict: Dictionary containing trend compatibility analysis
        """
        if not trend_features:
            return {
                "compatibility_score": 0.0,
                "message": "No trend data available for comparison",
            }

        # Calculate similarity with each trend
        similarities = [
            self.calculate_similarity(features, tf) for tf in trend_features
        ]

        # Calculate overall compatibility score
        compatibility_score = np.mean(similarities) if similarities else 0.0

        # Determine which aspects match the trends
        matching_aspects = []
        non_matching_aspects = []

        # Compare key aspects with trends
        aspects_to_check = [
            ("tempo", "temporal", "tempo", 20),  # name, category, feature, tolerance
            ("energy", "high_level", "energy_level", 0.2),
            ("mood", "high_level", "mood_valence", None),  # Categorical comparison
            ("danceability", "high_level", "danceability", 0.2),
        ]

        for name, category, feature, tolerance in aspects_to_check:
            track_value = features.get(category, {}).get(feature)
            if track_value is None:
                continue

            # For categorical features
            if tolerance is None:
                trend_values = [
                    tf.get(category, {}).get(feature) for tf in trend_features
                ]
                most_common = (
                    max(set(trend_values), key=trend_values.count)
                    if trend_values
                    else None
                )

                if most_common and track_value == most_common:
                    matching_aspects.append(name)
                else:
                    non_matching_aspects.append(name)

            # For numerical features
            else:
                trend_values = [
                    tf.get(category, {}).get(feature, 0) for tf in trend_features
                ]
                avg_trend = np.mean(trend_values) if trend_values else 0

                if abs(track_value - avg_trend) <= tolerance:
                    matching_aspects.append(name)
                else:
                    non_matching_aspects.append(name)

        return {
            "compatibility_score": float(compatibility_score),
            "matching_aspects": matching_aspects,
            "non_matching_aspects": non_matching_aspects,
            "recommendation": (
                "High compatibility with current trends"
                if compatibility_score > 0.7
                else (
                    "Moderate compatibility with current trends"
                    if compatibility_score > 0.4
                    else "Low compatibility with current trends"
                )
            ),
        }

    def save_as_reference(
        self, features: Dict, style_name: str, reference_data_path: str
    ) -> bool:
        """
        Save features as a reference for a particular style.

        Args:
            features (dict): Features to save as reference
            style_name (str): Name of the style
            reference_data_path (str): Path to save reference data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load existing reference data if available
            reference_data = {}
            if os.path.exists(reference_data_path):
                with open(reference_data_path, "r") as f:
                    reference_data = json.load(f)

            # Add or update style reference
            if style_name not in reference_data:
                reference_data[style_name] = []

            # Add new reference features
            reference_data[style_name].append(features)

            # Save updated reference data
            with open(reference_data_path, "w") as f:
                json.dump(reference_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving reference data: {str(e)}")
            return False
