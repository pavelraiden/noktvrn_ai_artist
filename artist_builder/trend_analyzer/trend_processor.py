"""
Trend Processor Module

This module processes raw trend data into actionable insights,
identifying patterns, calculating relevance scores, and preparing
the data for artist evolution decisions.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.trend_analyzer.processor")


class TrendProcessorError(Exception):
    """Exception raised for errors in the trend processing."""

    pass


class TrendProcessor:
    """
    Processes raw trend data into actionable insights for artist evolution.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the trend processor.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.relevance_threshold = self.config.get("relevance_threshold", 0.6)
        self.growth_weight = self.config.get("growth_weight", 0.7)
        self.popularity_weight = self.config.get("popularity_weight", 0.3)

        logger.info(
            f"Initialized TrendProcessor with relevance threshold {self.relevance_threshold}"
        )

    def process_trend_data(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw trend data into actionable insights.

        Args:
            trend_data: Raw trend data from the collector

        Returns:
            Processed trend data with insights and scores
        """
        try:
            logger.info(
                f"Processing trend data for {trend_data.get('genre')} ({trend_data.get('time_window')})"
            )

            # Create a copy of the input data
            processed_data = trend_data.copy()

            # Add processed insights
            processed_data["insights"] = {
                "rising_subgenres": self._identify_rising_subgenres(trend_data),
                "trending_techniques": self._identify_trending_techniques(trend_data),
                "trending_themes": self._identify_trending_themes(trend_data),
                "trending_visuals": self._identify_trending_visuals(trend_data),
            }

            # Calculate overall trend strength
            processed_data["trend_strength"] = self._calculate_trend_strength(
                processed_data["insights"]
            )

            # Add metadata
            processed_data["processing_metadata"] = {
                "processed_at": datetime.now().isoformat(),
                "processor_version": "1.0",
                "relevance_threshold": self.relevance_threshold,
                "growth_weight": self.growth_weight,
                "popularity_weight": self.popularity_weight,
            }

            logger.info(
                f"Successfully processed trend data with {len(processed_data['insights']['rising_subgenres'])} rising subgenres"
            )
            return processed_data

        except Exception as e:
            logger.error(f"Error processing trend data: {str(e)}")
            raise TrendProcessorError(f"Failed to process trend data: {str(e)}")

    def _identify_rising_subgenres(
        self, trend_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify rising subgenres from trend data.

        Args:
            trend_data: Raw trend data

        Returns:
            List of rising subgenres with relevance scores
        """
        rising_subgenres = []

        for subgenre, data in trend_data.get("subgenres", {}).items():
            # Calculate relevance score based on popularity and growth
            relevance_score = (
                data.get("popularity_score", 0) * self.popularity_weight
                + data.get("growth_rate", 0) * self.growth_weight
            )

            # Only include subgenres above the relevance threshold
            if relevance_score >= self.relevance_threshold:
                rising_subgenres.append(
                    {
                        "name": subgenre,
                        "relevance_score": round(relevance_score, 2),
                        "popularity_score": data.get("popularity_score", 0),
                        "growth_rate": data.get("growth_rate", 0),
                        "key_attributes": data.get("key_attributes", []),
                    }
                )

        # Sort by relevance score (descending)
        rising_subgenres.sort(key=lambda x: x["relevance_score"], reverse=True)

        return rising_subgenres

    def _identify_trending_techniques(
        self, trend_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify trending production techniques from trend data.

        Args:
            trend_data: Raw trend data

        Returns:
            List of trending techniques with relevance scores
        """
        trending_techniques = []

        for technique in trend_data.get("production_techniques", []):
            # Calculate relevance score
            relevance_score = (
                technique.get("popularity_score", 0) * self.popularity_weight
                + technique.get("growth_rate", 0) * self.growth_weight
            )

            # Only include techniques above the relevance threshold
            if relevance_score >= self.relevance_threshold:
                trending_techniques.append(
                    {
                        "name": technique.get("name", "unknown"),
                        "relevance_score": round(relevance_score, 2),
                        "popularity_score": technique.get("popularity_score", 0),
                        "growth_rate": technique.get("growth_rate", 0),
                    }
                )

        # Sort by relevance score (descending)
        trending_techniques.sort(key=lambda x: x["relevance_score"], reverse=True)

        return trending_techniques

    def _identify_trending_themes(
        self, trend_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify trending lyrical themes from trend data.

        Args:
            trend_data: Raw trend data

        Returns:
            List of trending themes with relevance scores
        """
        trending_themes = []

        for theme in trend_data.get("lyrical_themes", []):
            # Calculate relevance score
            relevance_score = (
                theme.get("popularity_score", 0) * self.popularity_weight
                + theme.get("growth_rate", 0) * self.growth_weight
            )

            # Only include themes above the relevance threshold
            if relevance_score >= self.relevance_threshold:
                trending_themes.append(
                    {
                        "name": theme.get("theme", "unknown"),
                        "relevance_score": round(relevance_score, 2),
                        "popularity_score": theme.get("popularity_score", 0),
                        "growth_rate": theme.get("growth_rate", 0),
                    }
                )

        # Sort by relevance score (descending)
        trending_themes.sort(key=lambda x: x["relevance_score"], reverse=True)

        return trending_themes

    def _identify_trending_visuals(
        self, trend_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify trending visual aesthetics from trend data.

        Args:
            trend_data: Raw trend data

        Returns:
            List of trending visual styles with relevance scores
        """
        trending_visuals = []

        for visual in trend_data.get("visual_aesthetics", []):
            # Calculate relevance score
            relevance_score = (
                visual.get("popularity_score", 0) * self.popularity_weight
                + visual.get("growth_rate", 0) * self.growth_weight
            )

            # Only include visuals above the relevance threshold
            if relevance_score >= self.relevance_threshold:
                trending_visuals.append(
                    {
                        "name": visual.get("style", "unknown"),
                        "relevance_score": round(relevance_score, 2),
                        "popularity_score": visual.get("popularity_score", 0),
                        "growth_rate": visual.get("growth_rate", 0),
                    }
                )

        # Sort by relevance score (descending)
        trending_visuals.sort(key=lambda x: x["relevance_score"], reverse=True)

        return trending_visuals

    def _calculate_trend_strength(
        self, insights: Dict[str, List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate overall trend strength based on insights.

        Args:
            insights: Processed trend insights

        Returns:
            Overall trend strength score (0.0 to 1.0)
        """
        # Count the number of significant trends
        total_trends = sum(len(category) for category in insights.values())

        if total_trends == 0:
            return 0.0

        # Calculate average relevance score across all trends
        total_relevance = 0.0
        for category in insights.values():
            for item in category:
                total_relevance += item.get("relevance_score", 0)

        average_relevance = total_relevance / total_trends if total_trends > 0 else 0

        # Apply a logarithmic scaling to account for the number of trends
        # More trends with high relevance = stronger overall trend
        strength = average_relevance * (1 + math.log(total_trends + 1) / 10)

        # Ensure the result is between 0 and 1
        return min(max(round(strength, 2), 0.0), 1.0)

    def compare_trend_periods(
        self, current_data: Dict[str, Any], previous_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare trend data between two time periods to identify changes.

        Args:
            current_data: Current processed trend data
            previous_data: Previous processed trend data

        Returns:
            Dictionary containing trend changes and velocity
        """
        try:
            logger.info("Comparing trend periods to identify changes")

            # Extract time windows for context
            current_window = current_data.get("time_window", "unknown")
            previous_window = previous_data.get("time_window", "unknown")

            # Initialize result structure
            comparison = {
                "timestamp": datetime.now().isoformat(),
                "current_window": current_window,
                "previous_window": previous_window,
                "subgenre_changes": [],
                "technique_changes": [],
                "theme_changes": [],
                "visual_changes": [],
                "overall_velocity": 0.0,
            }

            # Compare subgenres
            current_subgenres = {
                item["name"]: item
                for item in current_data.get("insights", {}).get("rising_subgenres", [])
            }
            previous_subgenres = {
                item["name"]: item
                for item in previous_data.get("insights", {}).get(
                    "rising_subgenres", []
                )
            }

            for name, current in current_subgenres.items():
                if name in previous_subgenres:
                    # Calculate change in relevance
                    previous = previous_subgenres[name]
                    change = current["relevance_score"] - previous["relevance_score"]

                    comparison["subgenre_changes"].append(
                        {
                            "name": name,
                            "current_score": current["relevance_score"],
                            "previous_score": previous["relevance_score"],
                            "change": round(change, 2),
                            "status": (
                                "rising"
                                if change > 0.05
                                else "stable" if abs(change) <= 0.05 else "declining"
                            ),
                        }
                    )
                else:
                    # New subgenre
                    comparison["subgenre_changes"].append(
                        {
                            "name": name,
                            "current_score": current["relevance_score"],
                            "previous_score": 0.0,
                            "change": round(current["relevance_score"], 2),
                            "status": "new",
                        }
                    )

            # Check for disappeared subgenres
            for name, previous in previous_subgenres.items():
                if name not in current_subgenres:
                    comparison["subgenre_changes"].append(
                        {
                            "name": name,
                            "current_score": 0.0,
                            "previous_score": previous["relevance_score"],
                            "change": -round(previous["relevance_score"], 2),
                            "status": "disappeared",
                        }
                    )

            # Sort by absolute change (descending)
            comparison["subgenre_changes"].sort(
                key=lambda x: abs(x["change"]), reverse=True
            )

            # Similarly compare other categories (techniques, themes, visuals)
            # (Implementation similar to subgenres, omitted for brevity)

            # Calculate overall velocity (rate of change)
            all_changes = (
                comparison["subgenre_changes"]
                + comparison["technique_changes"]
                + comparison["theme_changes"]
                + comparison["visual_changes"]
            )

            if all_changes:
                # Average of absolute changes
                avg_change = sum(abs(item["change"]) for item in all_changes) / len(
                    all_changes
                )
                # Scale to 0-1 range
                comparison["overall_velocity"] = min(round(avg_change * 2, 2), 1.0)

            logger.info(
                f"Completed trend comparison with velocity {comparison['overall_velocity']}"
            )
            return comparison

        except Exception as e:
            logger.error(f"Error comparing trend periods: {str(e)}")
            raise TrendProcessorError(f"Failed to compare trend periods: {str(e)}")

    def get_trend_summary(
        self, processed_data: Dict[str, Any], max_items: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a human-readable summary of the most significant trends.

        Args:
            processed_data: Processed trend data
            max_items: Maximum number of items to include per category

        Returns:
            Dictionary containing trend summaries
        """
        insights = processed_data.get("insights", {})

        summary = {
            "genre": processed_data.get("genre", "Unknown"),
            "time_window": processed_data.get("time_window", "Unknown"),
            "trend_strength": processed_data.get("trend_strength", 0.0),
            "top_subgenres": [
                f"{item['name']} (score: {item['relevance_score']})"
                for item in insights.get("rising_subgenres", [])[:max_items]
            ],
            "top_techniques": [
                f"{item['name']} (score: {item['relevance_score']})"
                for item in insights.get("trending_techniques", [])[:max_items]
            ],
            "top_themes": [
                f"{item['name']} (score: {item['relevance_score']})"
                for item in insights.get("trending_themes", [])[:max_items]
            ],
            "top_visuals": [
                f"{item['name']} (score: {item['relevance_score']})"
                for item in insights.get("trending_visuals", [])[:max_items]
            ],
            "summary_text": self._generate_summary_text(processed_data, max_items),
        }

        return summary

    def _generate_summary_text(
        self, processed_data: Dict[str, Any], max_items: int = 5
    ) -> str:
        """
        Generate a natural language summary of trends.

        Args:
            processed_data: Processed trend data
            max_items: Maximum number of items to include

        Returns:
            Summary text
        """
        genre = processed_data.get("genre", "Unknown")
        time_window = processed_data.get("time_window", "Unknown")
        trend_strength = processed_data.get("trend_strength", 0.0)
        insights = processed_data.get("insights", {})

        strength_desc = (
            "strong"
            if trend_strength > 0.7
            else "moderate" if trend_strength > 0.4 else "mild"
        )

        summary = f"Current {strength_desc} trends in {genre} music over the past {time_window}:\n\n"

        # Add subgenres
        subgenres = insights.get("rising_subgenres", [])[:max_items]
        if subgenres:
            summary += "Rising subgenres: "
            summary += ", ".join(f"{item['name']}" for item in subgenres)
            summary += ".\n\n"

        # Add techniques
        techniques = insights.get("trending_techniques", [])[:max_items]
        if techniques:
            summary += "Popular production techniques: "
            summary += ", ".join(f"{item['name']}" for item in techniques)
            summary += ".\n\n"

        # Add themes
        themes = insights.get("trending_themes", [])[:max_items]
        if themes:
            summary += "Trending lyrical themes: "
            summary += ", ".join(f"{item['name']}" for item in themes)
            summary += ".\n\n"

        # Add visuals
        visuals = insights.get("trending_visuals", [])[:max_items]
        if visuals:
            summary += "Popular visual aesthetics: "
            summary += ", ".join(f"{item['name']}" for item in visuals)
            summary += ".\n"

        return summary
