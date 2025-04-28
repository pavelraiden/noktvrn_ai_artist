"""
Trend Collector Module

This module is responsible for collecting trend data from various sources
including music streaming platforms, social media, and industry charts.
It supports configurable time windows for trend analysis.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random  # For mock data generation

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.trend_analyzer.collector")


class TrendCollectorError(Exception):
    """Exception raised for errors in the trend collection process."""
    pass


class TrendCollector:
    """
    Collects trend data from various sources for analysis.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the trend collector.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.data_sources = self.config.get("data_sources", ["streaming", "social", "charts"])
        self.time_windows = self.config.get("time_windows", [1, 3, 7, 14, 30, 60, 90])  # in days
        
        # Set up cache directory
        self.cache_dir = Path(self.config.get("cache_dir", "/tmp/trend_cache"))
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"Initialized TrendCollector with {len(self.data_sources)} data sources")

    def collect_trends(self, genre: str, time_window: int) -> Dict[str, Any]:
        """
        Collect trend data for a specific genre and time window.
        
        Args:
            genre: The main genre to collect trends for
            time_window: Time window in days (1, 3, 7, 14, 30, 60, or 90)
            
        Returns:
            Dictionary containing trend data
        """
        if time_window not in self.time_windows:
            raise TrendCollectorError(f"Invalid time window: {time_window}. Must be one of {self.time_windows}")
        
        logger.info(f"Collecting {time_window}-day trends for genre: {genre}")
        
        # Check cache first
        cached_data = self._check_cache(genre, time_window)
        if cached_data:
            logger.info(f"Using cached trend data for {genre} ({time_window} days)")
            return cached_data
        
        # Collect data from each source
        trend_data = {
            "timestamp": datetime.now().isoformat(),
            "genre": genre,
            "time_window": f"{time_window}d",
            "subgenres": {},
            "production_techniques": [],
            "lyrical_themes": [],
            "visual_aesthetics": []
        }
        
        try:
            # Collect from each source
            for source in self.data_sources:
                source_data = self._collect_from_source(source, genre, time_window)
                self._merge_source_data(trend_data, source_data)
            
            # Cache the results
            self._cache_data(genre, time_window, trend_data)
            
            logger.info(f"Successfully collected trend data for {genre} ({time_window} days)")
            return trend_data
            
        except Exception as e:
            logger.error(f"Error collecting trend data: {str(e)}")
            raise TrendCollectorError(f"Failed to collect trend data: {str(e)}")

    def _collect_from_source(self, source: str, genre: str, time_window: int) -> Dict[str, Any]:
        """
        Collect trend data from a specific source.
        
        Args:
            source: The data source to collect from
            genre: The main genre to collect trends for
            time_window: Time window in days
            
        Returns:
            Dictionary containing source-specific trend data
        """
        logger.info(f"Collecting from {source} for {genre} ({time_window} days)")
        
        # In a real implementation, this would call APIs or scrape websites
        # For now, we'll generate mock data
        if source == "streaming":
            return self._mock_streaming_data(genre, time_window)
        elif source == "social":
            return self._mock_social_data(genre, time_window)
        elif source == "charts":
            return self._mock_chart_data(genre, time_window)
        else:
            logger.warning(f"Unknown data source: {source}")
            return {}

    def _merge_source_data(self, trend_data: Dict[str, Any], source_data: Dict[str, Any]) -> None:
        """
        Merge source-specific data into the main trend data.
        
        Args:
            trend_data: The main trend data dictionary to update
            source_data: Source-specific data to merge in
        """
        # Merge subgenres
        for subgenre, data in source_data.get("subgenres", {}).items():
            if subgenre in trend_data["subgenres"]:
                # Average the scores if the subgenre already exists
                existing = trend_data["subgenres"][subgenre]
                existing["popularity_score"] = (existing["popularity_score"] + data["popularity_score"]) / 2
                existing["growth_rate"] = (existing["growth_rate"] + data["growth_rate"]) / 2
                # Combine key attributes
                existing["key_attributes"] = list(set(existing["key_attributes"] + data["key_attributes"]))
            else:
                trend_data["subgenres"][subgenre] = data
        
        # Merge other categories
        for category in ["production_techniques", "lyrical_themes", "visual_aesthetics"]:
            existing_items = {item["name" if "name" in item else "theme" if "theme" in item else "style"]: item 
                             for item in trend_data[category]}
            
            for item in source_data.get(category, []):
                key = item["name"] if "name" in item else item["theme"] if "theme" in item else item["style"]
                
                if key in existing_items:
                    # Average the scores if the item already exists
                    existing = existing_items[key]
                    existing["popularity_score"] = (existing["popularity_score"] + item["popularity_score"]) / 2
                    existing["growth_rate"] = (existing["growth_rate"] + item["growth_rate"]) / 2
                else:
                    trend_data[category].append(item)

    def _check_cache(self, genre: str, time_window: int) -> Optional[Dict[str, Any]]:
        """
        Check if trend data is available in cache.
        
        Args:
            genre: The main genre
            time_window: Time window in days
            
        Returns:
            Cached trend data if available and fresh, None otherwise
        """
        cache_file = self.cache_dir / f"{genre.lower()}_{time_window}d.json"
        
        if not cache_file.exists():
            return None
        
        try:
            # Read cache file
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is fresh enough (half the time window)
            cache_timestamp = datetime.fromisoformat(cached_data["timestamp"])
            max_age = timedelta(days=time_window / 2)
            
            if datetime.now() - cache_timestamp > max_age:
                logger.info(f"Cache for {genre} ({time_window} days) is stale")
                return None
            
            return cached_data
            
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
            return None

    def _cache_data(self, genre: str, time_window: int, data: Dict[str, Any]) -> None:
        """
        Cache trend data for future use.
        
        Args:
            genre: The main genre
            time_window: Time window in days
            data: Trend data to cache
        """
        cache_file = self.cache_dir / f"{genre.lower()}_{time_window}d.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Cached trend data for {genre} ({time_window} days)")
            
        except Exception as e:
            logger.warning(f"Error caching trend data: {str(e)}")

    # Mock data generation methods for development
    def _mock_streaming_data(self, genre: str, time_window: int) -> Dict[str, Any]:
        """Generate mock streaming platform trend data."""
        subgenres = self._get_mock_subgenres(genre)
        
        return {
            "subgenres": {
                subgenre: {
                    "popularity_score": round(random.uniform(0.5, 0.95), 2),
                    "growth_rate": round(random.uniform(0.01, 0.2), 2),
                    "key_attributes": self._get_mock_attributes(subgenre)
                }
                for subgenre in subgenres
            },
            "production_techniques": [
                {
                    "name": technique,
                    "popularity_score": round(random.uniform(0.5, 0.9), 2),
                    "growth_rate": round(random.uniform(0.01, 0.15), 2)
                }
                for technique in self._get_mock_production_techniques(genre)
            ]
        }

    def _mock_social_data(self, genre: str, time_window: int) -> Dict[str, Any]:
        """Generate mock social media trend data."""
        return {
            "subgenres": {
                subgenre: {
                    "popularity_score": round(random.uniform(0.5, 0.95), 2),
                    "growth_rate": round(random.uniform(0.01, 0.2), 2),
                    "key_attributes": self._get_mock_attributes(subgenre)
                }
                for subgenre in self._get_mock_subgenres(genre)[:3]  # Fewer subgenres from social
            },
            "lyrical_themes": [
                {
                    "theme": theme,
                    "popularity_score": round(random.uniform(0.5, 0.9), 2),
                    "growth_rate": round(random.uniform(0.01, 0.15), 2)
                }
                for theme in self._get_mock_lyrical_themes(genre)
            ],
            "visual_aesthetics": [
                {
                    "style": style,
                    "popularity_score": round(random.uniform(0.5, 0.9), 2),
                    "growth_rate": round(random.uniform(0.01, 0.15), 2)
                }
                for style in self._get_mock_visual_styles(genre)
            ]
        }

    def _mock_chart_data(self, genre: str, time_window: int) -> Dict[str, Any]:
        """Generate mock chart and industry trend data."""
        return {
            "subgenres": {
                subgenre: {
                    "popularity_score": round(random.uniform(0.6, 0.95), 2),
                    "growth_rate": round(random.uniform(0.01, 0.1), 2),
                    "key_attributes": self._get_mock_attributes(subgenre)
                }
                for subgenre in self._get_mock_subgenres(genre)[:2]  # Even fewer subgenres from charts
            },
            "production_techniques": [
                {
                    "name": technique,
                    "popularity_score": round(random.uniform(0.6, 0.9), 2),
                    "growth_rate": round(random.uniform(0.01, 0.1), 2)
                }
                for technique in self._get_mock_production_techniques(genre)[:3]
            ]
        }

    def _get_mock_subgenres(self, genre: str) -> List[str]:
        """Get mock subgenres for a genre."""
        genre_map = {
            "Electronic": ["ambient", "techno", "house", "trance", "drum and bass", "dubstep", "synthwave", "chillwave"],
            "Rock": ["indie rock", "alternative", "post-rock", "garage rock", "psychedelic", "prog rock"],
            "Hip Hop": ["trap", "boom bap", "conscious", "drill", "cloud rap", "lo-fi hip hop"],
            "Pop": ["synth-pop", "indie pop", "dream pop", "hyperpop", "bedroom pop", "dance-pop"],
            "Jazz": ["nu-jazz", "jazz fusion", "acid jazz", "smooth jazz", "contemporary jazz"],
            "R&B": ["neo-soul", "alternative R&B", "future R&B", "soul", "funk"],
            "Folk": ["indie folk", "folk rock", "contemporary folk", "freak folk", "americana"]
        }
        
        return genre_map.get(genre, ["subgenre1", "subgenre2", "subgenre3", "subgenre4"])

    def _get_mock_attributes(self, subgenre: str) -> List[str]:
        """Get mock attributes for a subgenre."""
        attribute_map = {
            "ambient": ["atmospheric", "textural", "minimal", "ethereal"],
            "techno": ["rhythmic", "hypnotic", "mechanical", "futuristic"],
            "house": ["groovy", "soulful", "uplifting", "melodic"],
            "trance": ["euphoric", "energetic", "layered", "emotional"],
            "synthwave": ["retro", "nostalgic", "cinematic", "80s-inspired"],
            "trap": ["bass-heavy", "dark", "aggressive", "minimal"],
            "indie rock": ["raw", "emotional", "guitar-driven", "authentic"],
            "synth-pop": ["catchy", "electronic", "melodic", "polished"]
        }
        
        return attribute_map.get(subgenre, ["attribute1", "attribute2", "attribute3"])

    def _get_mock_production_techniques(self, genre: str) -> List[str]:
        """Get mock production techniques for a genre."""
        technique_map = {
            "Electronic": ["analog synthesis", "digital processing", "field recordings", "granular synthesis", 
                          "modular synthesis", "lo-fi processing", "sampling", "generative algorithms"],
            "Rock": ["live recording", "analog tape", "vintage amplifiers", "room acoustics", 
                    "minimal processing", "dynamic compression", "guitar pedals"],
            "Hip Hop": ["sampling", "drum programming", "808 bass", "vocal processing", 
                       "looping", "beat chopping", "layered vocals"],
            "Pop": ["vocal layering", "pitch correction", "digital production", "synthesized instruments", 
                   "maximized loudness", "precise editing", "sample libraries"]
        }
        
        return technique_map.get(genre, ["technique1", "technique2", "technique3", "technique4"])

    def _get_mock_lyrical_themes(self, genre: str) -> List[str]:
        """Get mock lyrical themes for a genre."""
        theme_map = {
            "Electronic": ["futurism", "technology", "space", "nature", "introspection", "urban life"],
            "Rock": ["rebellion", "love", "social issues", "personal struggles", "politics", "existentialism"],
            "Hip Hop": ["street life", "success", "social commentary", "personal growth", "relationships", "wealth"],
            "Pop": ["love", "heartbreak", "empowerment", "celebration", "youth", "relationships"],
            "Folk": ["storytelling", "nature", "tradition", "social justice", "personal journey"]
        }
        
        return theme_map.get(genre, ["theme1", "theme2", "theme3", "theme4"])

    def _get_mock_visual_styles(self, genre: str) -> List[str]:
        """Get mock visual styles for a genre."""
        style_map = {
            "Electronic": ["minimalist", "futuristic", "glitch art", "abstract", "retro-futurism", "cyberpunk"],
            "Rock": ["gritty", "vintage", "band-focused", "high-contrast", "documentary-style", "artistic"],
            "Hip Hop": ["urban", "luxury", "stylized", "street", "high-fashion", "cinematic"],
            "Pop": ["colorful", "high-production", "fashion-forward", "clean", "conceptual", "narrative"],
            "Folk": ["natural", "authentic", "rustic", "documentary", "intimate", "nostalgic"]
        }
        
        return style_map.get(genre, ["style1", "style2", "style3", "style4"])
