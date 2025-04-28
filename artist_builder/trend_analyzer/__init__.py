"""
Trend Analyzer Package Initialization

This module initializes the trend analyzer package and provides
a unified interface for trend analysis functionality.
"""

import logging
from typing import Dict, Any, List, Optional

from .trend_collector import TrendCollector
from .trend_processor import TrendProcessor
from .artist_compatibility_analyzer import ArtistCompatibilityAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.trend_analyzer")


class TrendAnalyzer:
    """
    Main interface for the trend analyzer system.
    Coordinates the collection, processing, and compatibility analysis of trends.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the trend analyzer system.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.collector = TrendCollector(self.config.get("collector_config"))
        self.processor = TrendProcessor(self.config.get("processor_config"))
        self.compatibility_analyzer = ArtistCompatibilityAnalyzer(self.config.get("compatibility_config"))
        
        logger.info("Initialized TrendAnalyzer system")

    def analyze_trends_for_artist(
        self, 
        artist_profile: Dict[str, Any], 
        time_window: int = 30
    ) -> Dict[str, Any]:
        """
        Perform a complete trend analysis for an artist.
        
        Args:
            artist_profile: The artist's profile
            time_window: Time window in days (default: 30)
            
        Returns:
            Dictionary containing complete trend analysis results
        """
        try:
            logger.info(f"Starting trend analysis for artist {artist_profile.get('stage_name', 'Unknown')}")
            
            # Get the artist's main genre
            genre = artist_profile.get("genre", "Unknown")
            
            # Collect trend data
            raw_trend_data = self.collector.collect_trends(genre, time_window)
            
            # Process trend data
            processed_trends = self.processor.process_trend_data(raw_trend_data)
            
            # Analyze compatibility with artist
            compatibility_analysis = self.compatibility_analyzer.analyze_trend_compatibility(
                artist_profile, processed_trends
            )
            
            # Combine all results
            analysis_results = {
                "artist_id": artist_profile.get("artist_id", "unknown"),
                "artist_name": artist_profile.get("stage_name", "Unknown"),
                "genre": genre,
                "time_window": time_window,
                "trend_data": raw_trend_data,
                "processed_trends": processed_trends,
                "compatibility_analysis": compatibility_analysis,
                "trend_summary": self.processor.get_trend_summary(processed_trends),
                "evolution_recommendations": compatibility_analysis.get("evolution_recommendations", [])
            }
            
            logger.info(f"Completed trend analysis for artist {artist_profile.get('stage_name', 'Unknown')}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            raise Exception(f"Failed to complete trend analysis: {str(e)}")

    def get_evolution_recommendations(
        self, 
        artist_profile: Dict[str, Any], 
        time_windows: List[int] = [7, 30, 90]
    ) -> Dict[str, Any]:
        """
        Get evolution recommendations for an artist based on multiple time windows.
        
        Args:
            artist_profile: The artist's profile
            time_windows: List of time windows in days to analyze
            
        Returns:
            Dictionary containing evolution recommendations
        """
        try:
            logger.info(f"Generating evolution recommendations for artist {artist_profile.get('stage_name', 'Unknown')}")
            
            all_recommendations = []
            window_analyses = {}
            
            # Analyze trends for each time window
            for window in time_windows:
                analysis = self.analyze_trends_for_artist(artist_profile, window)
                window_analyses[f"{window}d"] = analysis
                
                # Add time window to each recommendation
                for rec in analysis.get("evolution_recommendations", []):
                    rec["time_window"] = f"{window}d"
                    all_recommendations.append(rec)
            
            # Prioritize recommendations
            prioritized_recommendations = self._prioritize_recommendations(all_recommendations)
            
            result = {
                "artist_id": artist_profile.get("artist_id", "unknown"),
                "artist_name": artist_profile.get("stage_name", "Unknown"),
                "prioritized_recommendations": prioritized_recommendations,
                "window_analyses": window_analyses
            }
            
            logger.info(f"Generated {len(prioritized_recommendations)} evolution recommendations")
            return result
            
        except Exception as e:
            logger.error(f"Error generating evolution recommendations: {str(e)}")
            raise Exception(f"Failed to generate evolution recommendations: {str(e)}")

    def _prioritize_recommendations(
        self, 
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize recommendations across different time windows.
        
        Args:
            recommendations: List of recommendations from different time windows
            
        Returns:
            Prioritized list of recommendations
        """
        # Group recommendations by type and name
        grouped_recs = {}
        for rec in recommendations:
            key = f"{rec['type']}:{rec['name']}"
            if key not in grouped_recs:
                grouped_recs[key] = []
            grouped_recs[key].append(rec)
        
        # For each group, select the best recommendation
        prioritized = []
        for group in grouped_recs.values():
            # Sort by priority first, then by combined score
            group.sort(
                key=lambda x: (
                    0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2,
                    -(x["compatibility_score"] + x["relevance_score"])
                )
            )
            
            # Take the highest priority recommendation
            best_rec = group[0].copy()
            
            # Add information about which time windows this appears in
            best_rec["appears_in_windows"] = [rec["time_window"] for rec in group]
            
            # Boost priority if it appears in multiple windows
            if len(best_rec["appears_in_windows"]) > 1:
                if best_rec["priority"] == "medium":
                    best_rec["priority"] = "high"
                best_rec["confidence"] = "high"
            else:
                best_rec["confidence"] = "medium" if best_rec["priority"] == "high" else "low"
            
            prioritized.append(best_rec)
        
        # Final sort by priority and confidence
        prioritized.sort(
            key=lambda x: (
                0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2,
                0 if x["confidence"] == "high" else 1 if x["confidence"] == "medium" else 2,
                -(x["compatibility_score"] + x["relevance_score"])
            )
        )
        
        return prioritized
