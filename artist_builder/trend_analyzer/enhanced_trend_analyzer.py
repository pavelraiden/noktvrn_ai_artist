"""
Enhanced Trend Analyzer Module for Country-Based Trend Analysis

This module extends the basic TrendAnalyzer to provide country-based trend analysis
capabilities, enabling the tracking of musical trends across different countries,
genres, and audience clusters.
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple, Any

from ..audio_analysis.feature_extractor import FeatureExtractor


class EnhancedTrendAnalyzer:
    """
    Class for analyzing musical trends across countries, genres, and audience clusters.
    """

    def __init__(
        self,
        trend_data_path: Optional[str] = None,
        country_profiles_path: Optional[str] = None,
    ):
        """
        Initialize the EnhancedTrendAnalyzer.

        Args:
            trend_data_path (str, optional): Path to trend data storage
            country_profiles_path (str, optional): Path to country profiles data
        """
        self.trend_data_path = trend_data_path
        self.country_profiles_path = country_profiles_path
        self.trend_history = []
        self.feature_extractor = FeatureExtractor()

        # Load trend history if path is provided
        if trend_data_path and os.path.exists(trend_data_path):
            self._load_trend_history()

    def identify_trends_by_segment(
        self,
        features_collection: List[Dict],
        segmentation: Dict[str, str],
        time_period: str = "current",
    ) -> Dict:
        """
        Identify trends for a specific segment (country, genre, audience cluster).

        Args:
            features_collection (list): Collection of audio features
            segmentation (dict): Segmentation parameters (e.g., {"country": "US", "genre": "Pop"})
            time_period (str): Time period label for the trends

        Returns:
            dict: Dictionary containing trend analysis results
        """
        # Filter features based on segmentation
        filtered_features = self._filter_features_by_segment(
            features_collection, segmentation
        )

        if not filtered_features:
            return {
                "status": "error",
                "message": f"No features found for segment: {segmentation}",
                "segmentation": segmentation,
            }

        # Calculate trends for the filtered subset
        trends = self._calculate_trends(filtered_features, time_period)

        # Add segmentation information
        trends["segmentation"] = segmentation

        return trends

    def get_country_trends(
        self, country_code: str, time_period: str = "current"
    ) -> Dict:
        """
        Retrieve aggregated trends for a specific country.

        Args:
            country_code (str): ISO country code
            time_period (str): Time period label

        Returns:
            dict: Dictionary containing country-specific trends
        """
        # Check if we have country profiles data
        if not self.country_profiles_path:
            return {
                "status": "error",
                "message": "Country profiles path not set",
                "country_code": country_code,
            }

        # Construct path to country profile
        country_profile_path = os.path.join(
            self.country_profiles_path,
            "daily_profiles",
            time_period,
            f"{country_code}.json",
        )

        # Check if country profile exists
        if not os.path.exists(country_profile_path):
            return {
                "status": "error",
                "message": f"Country profile not found for {country_code}",
                "country_code": country_code,
            }

        # Load country profile
        try:
            with open(country_profile_path, "r") as f:
                country_profile = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error loading country profile: {str(e)}",
                "country_code": country_code,
            }

        # Extract trend information from country profile
        country_trends = {
            "status": "success",
            "country_code": country_code,
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "streaming_stats": country_profile.get("streaming_stats", {}),
            "genre_trends": self._extract_genre_trends_from_profile(country_profile),
            "audio_feature_trends": self._extract_audio_feature_trends_from_profile(
                country_profile
            ),
        }

        return country_trends

    def compare_segment_trends(
        self,
        segment1: Dict[str, str],
        segment2: Dict[str, str],
        time_period: str = "current",
    ) -> Dict:
        """
        Compare trends between two different segments.

        Args:
            segment1 (dict): First segment parameters
            segment2 (dict): Second segment parameters
            time_period (str): Time period label

        Returns:
            dict: Dictionary containing comparison results
        """
        # Get trends for each segment
        trends1 = self.get_segment_trends(segment1, time_period)
        trends2 = self.get_segment_trends(segment2, time_period)

        # Check if both trend retrievals were successful
        if trends1.get("status") != "success" or trends2.get("status") != "success":
            return {
                "status": "error",
                "message": "Error retrieving trends for comparison",
                "segment1": segment1,
                "segment2": segment2,
                "trends1_status": trends1.get("status"),
                "trends2_status": trends2.get("status"),
            }

        # Compare genre trends
        genre_comparison = self._compare_genre_trends(
            trends1.get("genre_trends", {}), trends2.get("genre_trends", {})
        )

        # Compare audio feature trends
        feature_comparison = self._compare_audio_feature_trends(
            trends1.get("audio_feature_trends", {}),
            trends2.get("audio_feature_trends", {}),
        )

        return {
            "status": "success",
            "segment1": segment1,
            "segment2": segment2,
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "genre_comparison": genre_comparison,
            "feature_comparison": feature_comparison,
            "summary": self._generate_comparison_summary(
                genre_comparison, feature_comparison
            ),
        }

    def track_trend_evolution(
        self,
        segment: Dict[str, str],
        start_date: str,
        end_date: str,
        interval: str = "daily",
    ) -> Dict:
        """
        Track the evolution of trends for a specific segment over time.

        Args:
            segment (dict): Segment parameters
            start_date (str): Start date (ISO format)
            end_date (str): End date (ISO format)
            interval (str): Time interval (daily, weekly, monthly)

        Returns:
            dict: Dictionary containing trend evolution analysis
        """
        # Generate date range
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid date format. Use ISO format (YYYY-MM-DD).",
                "segment": segment,
            }

        # Check if we have country profiles data
        if not self.country_profiles_path:
            return {
                "status": "error",
                "message": "Country profiles path not set",
                "segment": segment,
            }

        # Get country code from segment
        country_code = segment.get("country")
        if not country_code:
            return {
                "status": "error",
                "message": "Country code not specified in segment",
                "segment": segment,
            }

        # Collect trend data for each date in the range
        trend_data = []
        current_date = start

        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")

            # Construct path to country profile for this date
            profile_path = os.path.join(
                self.country_profiles_path,
                f"{interval}_profiles",
                date_str,
                f"{country_code}.json",
            )

            # Check if profile exists
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, "r") as f:
                        profile = json.load(f)

                    # Extract trend data
                    trend_data.append(
                        {
                            "date": date_str,
                            "genre_trends": self._extract_genre_trends_from_profile(
                                profile
                            ),
                            "audio_feature_trends": self._extract_audio_feature_trends_from_profile(
                                profile
                            ),
                        }
                    )
                except Exception as e:
                    # Log error but continue
                    print(f"Error loading profile for {date_str}: {str(e)}")

            # Move to next date
            if interval == "daily":
                current_date = current_date.replace(day=current_date.day + 1)
            elif interval == "weekly":
                current_date = current_date.replace(day=current_date.day + 7)
            elif interval == "monthly":
                month = current_date.month + 1
                year = current_date.year + (month > 12)
                month = (month - 1) % 12 + 1
                current_date = current_date.replace(year=year, month=month)

        # Analyze trend evolution
        evolution_analysis = self._analyze_trend_evolution(trend_data, segment)

        return {
            "status": "success",
            "segment": segment,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "data_points": len(trend_data),
            "evolution_analysis": evolution_analysis,
        }

    def predict_future_trends(
        self, segment: Dict[str, str], prediction_periods: int = 3
    ) -> Dict:
        """
        Predict future trends for a specific segment.

        Args:
            segment (dict): Segment parameters
            prediction_periods (int): Number of periods to predict

        Returns:
            dict: Dictionary containing trend predictions
        """
        # Check if we have enough history for prediction
        if len(self.trend_history) < 2:
            return {
                "status": "error",
                "message": "Insufficient trend history for prediction",
                "segment": segment,
            }

        # Filter trend history for the specified segment
        segment_history = self._filter_trend_history_by_segment(segment)

        if len(segment_history) < 2:
            return {
                "status": "error",
                "message": "Insufficient segment-specific trend history for prediction",
                "segment": segment,
            }

        # Predict genre trends
        genre_predictions = self._predict_genre_trends(
            segment_history, prediction_periods
        )

        # Predict audio feature trends
        feature_predictions = self._predict_audio_feature_trends(
            segment_history, prediction_periods
        )

        return {
            "status": "success",
            "segment": segment,
            "prediction_periods": prediction_periods,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "genres": genre_predictions,
                "features": feature_predictions,
            },
            "confidence": self._calculate_prediction_confidence(segment_history),
        }

    def update_trend_history(self, trend_data: Dict) -> None:
        """
        Update the trend history with new trend data.

        Args:
            trend_data (dict): New trend data to add to history
        """
        # Add timestamp if not present
        if "timestamp" not in trend_data:
            trend_data["timestamp"] = datetime.now().isoformat()

        # Add to history
        self.trend_history.append(trend_data)

        # Save to file if path is provided
        if self.trend_data_path:
            self._save_trend_history()

    def get_segment_trends(
        self, segment: Dict[str, str], time_period: str = "current"
    ) -> Dict:
        """
        Get trends for a specific segment.

        Args:
            segment (dict): Segment parameters
            time_period (str): Time period label

        Returns:
            dict: Dictionary containing segment-specific trends
        """
        # Check segment type
        if "country" in segment and "genre" not in segment and "cluster" not in segment:
            # Country-level trends
            return self.get_country_trends(segment["country"], time_period)
        elif "country" in segment and "genre" in segment and "cluster" not in segment:
            # Country-genre trends
            return self._get_country_genre_trends(
                segment["country"], segment["genre"], time_period
            )
        elif "country" in segment and "cluster" in segment:
            # Audience cluster trends
            return self._get_audience_cluster_trends(
                segment["country"], segment["cluster"], time_period
            )
        else:
            return {
                "status": "error",
                "message": "Invalid segment specification",
                "segment": segment,
            }

    def _filter_features_by_segment(
        self, features_collection: List[Dict], segmentation: Dict[str, str]
    ) -> List[Dict]:
        """
        Filter features based on segmentation parameters.

        Args:
            features_collection (list): Collection of audio features
            segmentation (dict): Segmentation parameters

        Returns:
            list: Filtered features
        """
        # This is a placeholder implementation
        # In a real system, features would have metadata about country, genre, etc.
        filtered = []

        for features in features_collection:
            # Check if features match segmentation
            match = True

            # Example: Check country
            if (
                "country" in segmentation
                and features.get("metadata", {}).get("country")
                != segmentation["country"]
            ):
                match = False

            # Example: Check genre
            if (
                "genre" in segmentation
                and features.get("metadata", {}).get("genre") != segmentation["genre"]
            ):
                match = False

            # Example: Check audience cluster
            if (
                "cluster" in segmentation
                and features.get("metadata", {}).get("cluster")
                != segmentation["cluster"]
            ):
                match = False

            if match:
                filtered.append(features)

        return filtered

    def _calculate_trends(
        self, features_collection: List[Dict], time_period: str
    ) -> Dict:
        """
        Calculate trends from a collection of features.

        Args:
            features_collection (list): Collection of audio features
            time_period (str): Time period label

        Returns:
            dict: Dictionary containing trend analysis results
        """
        # Extract relevant features for trend analysis
        tempos = []
        keys = []
        modes = []
        energy_levels = []
        danceability_scores = []
        valence_values = []

        for features in features_collection:
            # Extract temporal features
            if "temporal" in features:
                tempo = features["temporal"].get("tempo")
                if tempo is not None:
                    tempos.append(tempo)

            # Extract harmonic features
            if "harmonic" in features:
                key = features["harmonic"].get("key")
                mode = features["harmonic"].get("mode")
                if key is not None:
                    keys.append(key)
                if mode is not None:
                    modes.append(mode)

            # Extract high-level features
            if "high_level" in features:
                energy = features["high_level"].get("energy_level")
                danceability = features["high_level"].get("danceability")
                valence = features["high_level"].get("mood_valence")

                if energy is not None:
                    energy_levels.append(energy)
                if danceability is not None:
                    danceability_scores.append(danceability)
                if valence is not None:
                    valence_values.append(valence)

        # Calculate statistics
        tempo_stats = self._calculate_numeric_stats(tempos)
        energy_stats = self._calculate_numeric_stats(energy_levels)
        danceability_stats = self._calculate_numeric_stats(danceability_scores)
        key_stats = self._calculate_categorical_stats(keys)
        mode_stats = self._calculate_categorical_stats(modes)
        valence_stats = self._calculate_categorical_stats(valence_values)

        # Compile trends
        trends = {
            "status": "success",
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "sample_size": len(features_collection),
            "tempo": tempo_stats,
            "energy": energy_stats,
            "danceability": danceability_stats,
            "key": key_stats,
            "mode": mode_stats,
            "mood": {"valence": valence_stats},
        }

        return trends

    def _calculate_numeric_stats(self, values: List[float]) -> Dict:
        """
        Calculate statistics for numeric values.

        Args:
            values (list): List of numeric values

        Returns:
            dict: Dictionary containing statistics
        """
        if not values:
            return {
                "count": 0,
                "mean": None,
                "median": None,
                "std_dev": None,
                "min": None,
                "max": None,
            }

        return {
            "count": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std_dev": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
        }

    def _calculate_categorical_stats(self, values: List[str]) -> Dict:
        """
        Calculate statistics for categorical values.

        Args:
            values (list): List of categorical values

        Returns:
            dict: Dictionary containing statistics
        """
        if not values:
            return {"count": 0, "most_common": None, "distribution": {}}

        # Count occurrences
        counts = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1

        # Find most common
        most_common = max(counts.items(), key=lambda x: x[1])[0] if counts else None

        # Calculate distribution
        distribution = {k: v / len(values) for k, v in counts.items()}

        return {
            "count": len(values),
            "most_common": most_common,
            "distribution": distribution,
        }

    def _extract_genre_trends_from_profile(self, profile: Dict) -> Dict:
        """
        Extract genre trends from a country profile.

        Args:
            profile (dict): Country profile data

        Returns:
            dict: Dictionary containing genre trends
        """
        # This is a placeholder implementation
        # In a real system, this would extract actual genre trend data from the profile

        # Check if profile has genre trends
        if "genre_trends" not in profile:
            return {}

        genre_trends = {}

        for genre_data in profile["genre_trends"]:
            genre = genre_data.get("genre")
            if genre:
                genre_trends[genre] = {
                    "popularity": genre_data.get("popularity", {}),
                    "audio_features": genre_data.get("audio_features", {}),
                }

        return genre_trends

    def _extract_audio_feature_trends_from_profile(self, profile: Dict) -> Dict:
        """
        Extract audio feature trends from a country profile.

        Args:
            profile (dict): Country profile data

        Returns:
            dict: Dictionary containing audio feature trends
        """
        # This is a placeholder implementation
        # In a real system, this would extract actual audio feature trend data from the profile

        # Check if profile has audio feature trends
        if "audio_feature_trends" not in profile:
            return {}

        return profile["audio_feature_trends"]

    def _compare_genre_trends(self, trends1: Dict, trends2: Dict) -> Dict:
        """
        Compare genre trends between two segments.

        Args:
            trends1 (dict): Genre trends for first segment
            trends2 (dict): Genre trends for second segment

        Returns:
            dict: Dictionary containing comparison results
        """
        comparison = {}

        # Get all genres from both trend sets
        all_genres = set(trends1.keys()) | set(trends2.keys())

        for genre in all_genres:
            # Get genre data from each trend set
            genre1 = trends1.get(genre, {})
            genre2 = trends2.get(genre, {})

            # Compare popularity
            popularity1 = genre1.get("popularity", {}).get("stream_share", 0)
            popularity2 = genre2.get("popularity", {}).get("stream_share", 0)

            popularity_diff = (
                popularity2 - popularity1
                if popularity1 is not None and popularity2 is not None
                else None
            )

            # Compare audio features
            features1 = genre1.get("audio_features", {})
            features2 = genre2.get("audio_features", {})

            feature_comparison = {}

            for feature in set(features1.keys()) | set(features2.keys()):
                feature1 = features1.get(feature, {})
                feature2 = features2.get(feature, {})

                # Compare means
                mean1 = feature1.get("mean")
                mean2 = feature2.get("mean")

                mean_diff = (
                    mean2 - mean1 if mean1 is not None and mean2 is not None else None
                )

                feature_comparison[feature] = {
                    "mean_diff": mean_diff,
                    "segment1_mean": mean1,
                    "segment2_mean": mean2,
                }

            comparison[genre] = {
                "popularity_diff": popularity_diff,
                "segment1_popularity": popularity1,
                "segment2_popularity": popularity2,
                "features": feature_comparison,
            }

        return comparison

    def _compare_audio_feature_trends(self, trends1: Dict, trends2: Dict) -> Dict:
        """
        Compare audio feature trends between two segments.

        Args:
            trends1 (dict): Audio feature trends for first segment
            trends2 (dict): Audio feature trends for second segment

        Returns:
            dict: Dictionary containing comparison results
        """
        comparison = {}

        # Get all features from both trend sets
        all_features = set(trends1.keys()) | set(trends2.keys())

        for feature in all_features:
            # Get feature data from each trend set
            feature1 = trends1.get(feature, {})
            feature2 = trends2.get(feature, {})

            # Compare means
            mean1 = feature1.get("mean")
            mean2 = feature2.get("mean")

            mean_diff = (
                mean2 - mean1 if mean1 is not None and mean2 is not None else None
            )

            comparison[feature] = {
                "mean_diff": mean_diff,
                "segment1_mean": mean1,
                "segment2_mean": mean2,
            }

        return comparison

    def _generate_comparison_summary(
        self, genre_comparison: Dict, feature_comparison: Dict
    ) -> str:
        """
        Generate a summary of the comparison results.

        Args:
            genre_comparison (dict): Genre comparison results
            feature_comparison (dict): Feature comparison results

        Returns:
            str: Summary text
        """
        # This is a placeholder implementation
        # In a real system, this would generate a more detailed and insightful summary

        summary = "Comparison summary:\n"

        # Summarize genre differences
        if genre_comparison:
            summary += "- Genre differences:\n"

            for genre, data in genre_comparison.items():
                popularity_diff = data.get("popularity_diff")

                if popularity_diff is not None:
                    direction = (
                        "higher"
                        if popularity_diff > 0
                        else "lower" if popularity_diff < 0 else "same"
                    )
                    summary += f"  - {genre}: {abs(popularity_diff)*100:.1f}% {direction} in segment2\n"

        # Summarize feature differences
        if feature_comparison:
            summary += "- Feature differences:\n"

            for feature, data in feature_comparison.items():
                mean_diff = data.get("mean_diff")

                if mean_diff is not None:
                    direction = (
                        "higher"
                        if mean_diff > 0
                        else "lower" if mean_diff < 0 else "same"
                    )
                    summary += f"  - {feature}: {direction} in segment2\n"

        return summary

    def _analyze_trend_evolution(
        self, trend_data: List[Dict], segment: Dict[str, str]
    ) -> Dict:
        """
        Analyze the evolution of trends over time.

        Args:
            trend_data (list): List of trend data points
            segment (dict): Segment parameters

        Returns:
            dict: Dictionary containing evolution analysis
        """
        if not trend_data:
            return {}

        evolution = {}

        # Analyze genre evolution
        genre_evolution = {}

        # Get all genres across all data points
        all_genres = set()
        for data_point in trend_data:
            all_genres.update(data_point.get("genre_trends", {}).keys())

        for genre in all_genres:
            # Extract popularity over time
            popularity_series = []

            for data_point in trend_data:
                date = data_point.get("date")
                popularity = (
                    data_point.get("genre_trends", {})
                    .get(genre, {})
                    .get("popularity", {})
                    .get("stream_share")
                )

                if date and popularity is not None:
                    popularity_series.append((date, popularity))

            # Sort by date
            popularity_series.sort(key=lambda x: x[0])

            # Calculate trend
            if len(popularity_series) >= 2:
                first_value = popularity_series[0][1]
                last_value = popularity_series[-1][1]

                change = last_value - first_value
                percent_change = (
                    (change / first_value) * 100 if first_value != 0 else float("inf")
                )

                direction = (
                    "increasing"
                    if change > 0
                    else "decreasing" if change < 0 else "stable"
                )

                genre_evolution[genre] = {
                    "direction": direction,
                    "change": change,
                    "percent_change": percent_change,
                    "data_points": len(popularity_series),
                }

        # Analyze feature evolution
        feature_evolution = {}

        # Get all features across all data points
        all_features = set()
        for data_point in trend_data:
            all_features.update(data_point.get("audio_feature_trends", {}).keys())

        for feature in all_features:
            # Extract mean values over time
            mean_series = []

            for data_point in trend_data:
                date = data_point.get("date")
                mean = (
                    data_point.get("audio_feature_trends", {})
                    .get(feature, {})
                    .get("mean")
                )

                if date and mean is not None:
                    mean_series.append((date, mean))

            # Sort by date
            mean_series.sort(key=lambda x: x[0])

            # Calculate trend
            if len(mean_series) >= 2:
                first_value = mean_series[0][1]
                last_value = mean_series[-1][1]

                change = last_value - first_value
                percent_change = (
                    (change / first_value) * 100 if first_value != 0 else float("inf")
                )

                direction = (
                    "increasing"
                    if change > 0
                    else "decreasing" if change < 0 else "stable"
                )

                feature_evolution[feature] = {
                    "direction": direction,
                    "change": change,
                    "percent_change": percent_change,
                    "data_points": len(mean_series),
                }

        evolution["genres"] = genre_evolution
        evolution["features"] = feature_evolution

        return evolution

    def _filter_trend_history_by_segment(self, segment: Dict[str, str]) -> List[Dict]:
        """
        Filter trend history for a specific segment.

        Args:
            segment (dict): Segment parameters

        Returns:
            list: Filtered trend history
        """
        filtered = []

        for trend in self.trend_history:
            # Check if trend matches segment
            trend_segment = trend.get("segmentation", {})

            match = True

            for key, value in segment.items():
                if trend_segment.get(key) != value:
                    match = False
                    break

            if match:
                filtered.append(trend)

        return filtered

    def _predict_genre_trends(
        self, segment_history: List[Dict], prediction_periods: int
    ) -> Dict:
        """
        Predict genre trends based on historical data.

        Args:
            segment_history (list): Segment-specific trend history
            prediction_periods (int): Number of periods to predict

        Returns:
            dict: Dictionary containing genre trend predictions
        """
        predictions = {}

        # Get all genres across all history points
        all_genres = set()
        for data_point in segment_history:
            all_genres.update(data_point.get("genre_trends", {}).keys())

        for genre in all_genres:
            # Extract popularity over time
            popularity_series = []

            for data_point in segment_history:
                timestamp = data_point.get("timestamp")
                popularity = (
                    data_point.get("genre_trends", {})
                    .get(genre, {})
                    .get("popularity", {})
                    .get("stream_share")
                )

                if timestamp and popularity is not None:
                    # Convert timestamp to numeric value (days since epoch)
                    try:
                        date = datetime.fromisoformat(timestamp)
                        days = (date - datetime(1970, 1, 1)).days
                        popularity_series.append((days, popularity))
                    except ValueError:
                        continue

            # Sort by date
            popularity_series.sort(key=lambda x: x[0])

            # Predict future values using simple linear regression
            if len(popularity_series) >= 2:
                # Extract x and y values
                x = np.array([p[0] for p in popularity_series])
                y = np.array([p[1] for p in popularity_series])

                # Fit linear regression
                slope, intercept = np.polyfit(x, y, 1)

                # Predict future values
                last_x = x[-1]
                future_x = [last_x + i for i in range(1, prediction_periods + 1)]
                future_y = [slope * xi + intercept for xi in future_x]

                predictions[genre] = future_y

        return predictions

    def _predict_audio_feature_trends(
        self, segment_history: List[Dict], prediction_periods: int
    ) -> Dict:
        """
        Predict audio feature trends based on historical data.

        Args:
            segment_history (list): Segment-specific trend history
            prediction_periods (int): Number of periods to predict

        Returns:
            dict: Dictionary containing audio feature trend predictions
        """
        predictions = {}

        # Get all features across all history points
        all_features = set()
        for data_point in segment_history:
            all_features.update(data_point.get("audio_feature_trends", {}).keys())

        for feature in all_features:
            # Extract mean values over time
            mean_series = []

            for data_point in segment_history:
                timestamp = data_point.get("timestamp")
                mean = (
                    data_point.get("audio_feature_trends", {})
                    .get(feature, {})
                    .get("mean")
                )

                if timestamp and mean is not None:
                    # Convert timestamp to numeric value (days since epoch)
                    try:
                        date = datetime.fromisoformat(timestamp)
                        days = (date - datetime(1970, 1, 1)).days
                        mean_series.append((days, mean))
                    except ValueError:
                        continue

            # Sort by date
            mean_series.sort(key=lambda x: x[0])

            # Predict future values using simple linear regression
            if len(mean_series) >= 2:
                # Extract x and y values
                x = np.array([p[0] for p in mean_series])
                y = np.array([p[1] for p in mean_series])

                # Fit linear regression
                slope, intercept = np.polyfit(x, y, 1)

                # Predict future values
                last_x = x[-1]
                future_x = [last_x + i for i in range(1, prediction_periods + 1)]
                future_y = [slope * xi + intercept for xi in future_x]

                predictions[feature] = future_y

        return predictions

    def _calculate_prediction_confidence(self, segment_history: List[Dict]) -> float:
        """
        Calculate confidence score for predictions.

        Args:
            segment_history (list): Segment-specific trend history

        Returns:
            float: Confidence score (0-1)
        """
        # Simple confidence calculation based on history size and consistency
        history_size = len(segment_history)

        # Base confidence on history size
        size_factor = min(1.0, history_size / 10)  # Max confidence at 10+ data points

        # Check consistency of trends
        consistency_factor = 0.5  # Default medium consistency

        # More sophisticated consistency check would analyze trend stability

        # Combine factors
        confidence = 0.7 * size_factor + 0.3 * consistency_factor

        return float(confidence)

    def _get_country_genre_trends(
        self, country_code: str, genre: str, time_period: str
    ) -> Dict:
        """
        Get trends for a specific country and genre.

        Args:
            country_code (str): ISO country code
            genre (str): Genre name
            time_period (str): Time period label

        Returns:
            dict: Dictionary containing country-genre trends
        """
        # Check if we have country profiles data
        if not self.country_profiles_path:
            return {
                "status": "error",
                "message": "Country profiles path not set",
                "country_code": country_code,
                "genre": genre,
            }

        # Construct path to genre trend data
        genre_trend_path = os.path.join(
            self.country_profiles_path,
            "genre_trends",
            time_period,
            f"{country_code}-{genre.lower()}.json",
        )

        # Check if genre trend data exists
        if not os.path.exists(genre_trend_path):
            return {
                "status": "error",
                "message": f"Genre trend data not found for {country_code}/{genre}",
                "country_code": country_code,
                "genre": genre,
            }

        # Load genre trend data
        try:
            with open(genre_trend_path, "r") as f:
                genre_trend = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error loading genre trend data: {str(e)}",
                "country_code": country_code,
                "genre": genre,
            }

        return {
            "status": "success",
            "country_code": country_code,
            "genre": genre,
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "popularity": genre_trend.get("popularity", {}),
            "audio_features": genre_trend.get("audio_features", {}),
            "top_artists": genre_trend.get("top_artists", []),
            "trending_tracks": genre_trend.get("trending_tracks", []),
            "subgenre_distribution": genre_trend.get("subgenre_distribution", {}),
        }

    def _get_audience_cluster_trends(
        self, country_code: str, cluster: str, time_period: str
    ) -> Dict:
        """
        Get trends for a specific audience cluster.

        Args:
            country_code (str): ISO country code
            cluster (str): Audience cluster name
            time_period (str): Time period label

        Returns:
            dict: Dictionary containing audience cluster trends
        """
        # Check if we have country profiles data
        if not self.country_profiles_path:
            return {
                "status": "error",
                "message": "Country profiles path not set",
                "country_code": country_code,
                "cluster": cluster,
            }

        # Construct path to audience cluster trend data
        cluster_trend_path = os.path.join(
            self.country_profiles_path,
            "audience_trends",
            time_period,
            f"{country_code}-{cluster.lower().replace(' ', '-')}.json",
        )

        # Check if audience cluster trend data exists
        if not os.path.exists(cluster_trend_path):
            return {
                "status": "error",
                "message": f"Audience cluster trend data not found for {country_code}/{cluster}",
                "country_code": country_code,
                "cluster": cluster,
            }

        # Load audience cluster trend data
        try:
            with open(cluster_trend_path, "r") as f:
                cluster_trend = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error loading audience cluster trend data: {str(e)}",
                "country_code": country_code,
                "cluster": cluster,
            }

        return {
            "status": "success",
            "country_code": country_code,
            "cluster": cluster,
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "size": cluster_trend.get("size", {}),
            "demographics": cluster_trend.get("demographics", {}),
            "genre_preferences": cluster_trend.get("genre_preferences", []),
            "listening_habits": cluster_trend.get("listening_habits", {}),
            "engagement_patterns": cluster_trend.get("engagement_patterns", {}),
        }

    def _load_trend_history(self) -> None:
        """Load trend history from file."""
        try:
            with open(self.trend_data_path, "r") as f:
                self.trend_history = json.load(f)
        except Exception as e:
            print(f"Error loading trend history: {str(e)}")
            self.trend_history = []

    def _save_trend_history(self) -> None:
        """Save trend history to file."""
        try:
            with open(self.trend_data_path, "w") as f:
                json.dump(self.trend_history, f, indent=2)
        except Exception as e:
            print(f"Error saving trend history: {str(e)}")
