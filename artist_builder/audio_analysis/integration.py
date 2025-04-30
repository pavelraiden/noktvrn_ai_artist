"""
Audio Analysis Integration Module

This module integrates the enhanced feature extractor, country-based trend analysis,
artist evolution, and country profiles database components to provide a unified
interface for the AI Artist Creation and Management System.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple, Any

from ..audio_analysis.feature_extractor import FeatureExtractor
from ..trend_analyzer.enhanced_trend_analyzer import EnhancedTrendAnalyzer
from ..artist_evolution.artist_evolution_manager import ArtistEvolutionManager
from ..data_management.country_profiles_manager import CountryProfilesManager


class AudioAnalysisIntegrator:
    """
    Class for integrating audio analysis components and providing a unified interface.
    """
    
    def __init__(self, 
                 data_dir: str = "/home/ubuntu/country_profiles_data",
                 artist_profiles_dir: str = None):
        """
        Initialize the AudioAnalysisIntegrator with component instances.
        
        Args:
            data_dir (str): Path to the country profiles data directory
            artist_profiles_dir (str, optional): Path to the artist profiles directory
        """
        # Initialize component instances
        self.feature_extractor = FeatureExtractor()
        self.country_profiles_manager = CountryProfilesManager(data_dir)
        self.trend_analyzer = EnhancedTrendAnalyzer(
            country_profiles_path=data_dir
        )
        self.artist_evolution_manager = None
        
        # Set artist profiles directory
        self.artist_profiles_dir = artist_profiles_dir
    
    def analyze_audio(self, audio_file: str) -> Dict:
        """
        Extract features from an audio file using the enhanced feature extractor.
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            dict: Extracted audio features
        """
        return self.feature_extractor.extract_features(audio_file)
    
    def analyze_audio_batch(self, audio_files: List[str]) -> List[Dict]:
        """
        Extract features from multiple audio files.
        
        Args:
            audio_files (list): List of paths to audio files
            
        Returns:
            list: List of extracted audio features
        """
        results = []
        for file in audio_files:
            features = self.analyze_audio(file)
            results.append(features)
        return results
    
    def get_country_trends(self, country_code: str, date: Optional[str] = None) -> Dict:
        """
        Get trends for a specific country.
        
        Args:
            country_code (str): ISO country code
            date (str, optional): Date in ISO format (YYYY-MM-DD)
            
        Returns:
            dict: Country trends
        """
        return self.trend_analyzer.get_country_trends(country_code, date)
    
    def compare_country_trends(self, country_code1: str, country_code2: str, date: Optional[str] = None) -> Dict:
        """
        Compare trends between two countries.
        
        Args:
            country_code1 (str): First country ISO code
            country_code2 (str): Second country ISO code
            date (str, optional): Date in ISO format (YYYY-MM-DD)
            
        Returns:
            dict: Comparison results
        """
        segment1 = {"country": country_code1}
        segment2 = {"country": country_code2}
        return self.trend_analyzer.compare_segment_trends(segment1, segment2, date)
    
    def track_country_trend_evolution(self, 
                                     country_code: str, 
                                     start_date: str, 
                                     end_date: str) -> Dict:
        """
        Track the evolution of trends for a specific country over time.
        
        Args:
            country_code (str): ISO country code
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            end_date (str): End date in ISO format (YYYY-MM-DD)
            
        Returns:
            dict: Trend evolution analysis
        """
        segment = {"country": country_code}
        return self.trend_analyzer.track_trend_evolution(segment, start_date, end_date)
    
    def predict_country_trends(self, country_code: str, prediction_periods: int = 3) -> Dict:
        """
        Predict future trends for a specific country.
        
        Args:
            country_code (str): ISO country code
            prediction_periods (int): Number of periods to predict
            
        Returns:
            dict: Trend predictions
        """
        segment = {"country": country_code}
        return self.trend_analyzer.predict_future_trends(segment, prediction_periods)
    
    def initialize_artist_evolution(self, artist_id: str) -> bool:
        """
        Initialize the artist evolution manager for a specific artist.
        
        Args:
            artist_id (str): Artist identifier
            
        Returns:
            bool: Success status
        """
        if not self.artist_profiles_dir:
            return False
        
        artist_profile_path = os.path.join(self.artist_profiles_dir, f"{artist_id}.json")
        evolution_history_path = os.path.join(self.artist_profiles_dir, f"{artist_id}_evolution.json")
        
        self.artist_evolution_manager = ArtistEvolutionManager(
            artist_profile_path=artist_profile_path,
            evolution_history_path=evolution_history_path,
            trend_analyzer=self.trend_analyzer
        )
        
        return True
    
    def generate_artist_adaptation_plan(self, 
                                       target_countries: List[str],
                                       strategic_goals: Optional[Dict] = None) -> Dict:
        """
        Generate an adaptation plan for the artist based on country trends.
        
        Args:
            target_countries (list): List of target country ISO codes
            strategic_goals (dict, optional): Strategic goals for the artist
            
        Returns:
            dict: Adaptation plan
        """
        if not self.artist_evolution_manager:
            return {
                "status": "error",
                "message": "Artist evolution manager not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        # Convert countries to segments
        target_segments = [{"country": country} for country in target_countries]
        
        # Generate adaptation plan
        return self.artist_evolution_manager.generate_adaptation_plan(
            target_segments=target_segments,
            strategic_goals=strategic_goals
        )
    
    def apply_adaptation_plan(self, plan_id: str) -> Dict:
        """
        Apply an adaptation plan to the artist profile.
        
        Args:
            plan_id (str): ID of the adaptation plan to apply
            
        Returns:
            dict: Result of applying the adaptation plan
        """
        if not self.artist_evolution_manager:
            return {
                "status": "error",
                "message": "Artist evolution manager not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        return self.artist_evolution_manager.apply_adaptation_plan(plan_id)
    
    def evaluate_adaptation_results(self, 
                                   plan_id: str, 
                                   performance_data: Dict) -> Dict:
        """
        Evaluate the results of an adaptation plan based on performance data.
        
        Args:
            plan_id (str): ID of the adaptation plan to evaluate
            performance_data (dict): Performance data for the adapted content
            
        Returns:
            dict: Evaluation results
        """
        if not self.artist_evolution_manager:
            return {
                "status": "error",
                "message": "Artist evolution manager not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        return self.artist_evolution_manager.evaluate_adaptation_results(
            plan_id=plan_id,
            performance_data=performance_data
        )
    
    def update_country_profile(self, 
                              country_code: str, 
                              date: str, 
                              profile_data: Dict) -> bool:
        """
        Update a country profile in the database.
        
        Args:
            country_code (str): ISO country code
            date (str): Date in ISO format (YYYY-MM-DD)
            profile_data (dict): Country profile data
            
        Returns:
            bool: Success status
        """
        return self.country_profiles_manager.update_country_profile(
            country_code=country_code,
            date=date,
            data=profile_data
        )
    
    def update_genre_trend(self, 
                          country_code: str, 
                          genre: str, 
                          date: str, 
                          trend_data: Dict) -> bool:
        """
        Update a genre trend in the database.
        
        Args:
            country_code (str): ISO country code
            genre (str): Genre name
            date (str): Date in ISO format (YYYY-MM-DD)
            trend_data (dict): Genre trend data
            
        Returns:
            bool: Success status
        """
        return self.country_profiles_manager.update_genre_trend(
            country_code=country_code,
            genre=genre,
            date=date,
            data=trend_data
        )
    
    def update_audience_trend(self, 
                             country_code: str, 
                             cluster: str, 
                             date: str, 
                             trend_data: Dict) -> bool:
        """
        Update an audience cluster trend in the database.
        
        Args:
            country_code (str): ISO country code
            cluster (str): Audience cluster name
            date (str): Date in ISO format (YYYY-MM-DD)
            trend_data (dict): Audience cluster trend data
            
        Returns:
            bool: Success status
        """
        return self.country_profiles_manager.update_audience_trend(
            country_code=country_code,
            cluster=cluster,
            date=date,
            data=trend_data
        )
    
    def update_historical_aggregate(self, 
                                   country_code: str, 
                                   period_type: str, 
                                   end_date: str, 
                                   aggregate_data: Dict) -> bool:
        """
        Update a historical aggregate in the database.
        
        Args:
            country_code (str): ISO country code
            period_type (str): Period type (e.g., "30day")
            end_date (str): End date in ISO format (YYYY-MM-DD)
            aggregate_data (dict): Historical aggregate data
            
        Returns:
            bool: Success status
        """
        return self.country_profiles_manager.update_historical_aggregate(
            country_code=country_code,
            period_type=period_type,
            end_date=end_date,
            data=aggregate_data
        )
    
    def analyze_and_update_trends(self, 
                                 audio_files: List[Dict],
                                 country_code: str,
                                 date: str) -> Dict:
        """
        Analyze audio files and update country trends based on the analysis.
        
        Args:
            audio_files (list): List of dictionaries with audio file paths and metadata
            country_code (str): ISO country code
            date (str): Date in ISO format (YYYY-MM-DD)
            
        Returns:
            dict: Analysis and update results
        """
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "country_code": country_code,
            "date": date,
            "files_processed": 0,
            "features_extracted": 0,
            "trends_updated": False,
            "genre_trends_updated": [],
            "errors": []
        }
        
        # Extract features from audio files
        features_collection = []
        for file_info in audio_files:
            try:
                file_path = file_info.get("path")
                metadata = file_info.get("metadata", {})
                
                # Extract features
                features = self.feature_extractor.extract_features(file_path)
                
                # Add metadata
                features["metadata"] = metadata
                features["metadata"]["country"] = country_code
                
                features_collection.append(features)
                results["files_processed"] += 1
                
                if features.get("status") == "success":
                    results["features_extracted"] += 1
                else:
                    results["errors"].append({
                        "file": file_path,
                        "error": features.get("message", "Unknown error")
                    })
            except Exception as e:
                results["errors"].append({
                    "file": file_info.get("path", "Unknown file"),
                    "error": str(e)
                })
        
        # Skip trend analysis if no features were extracted
        if results["features_extracted"] == 0:
            results["status"] = "error"
            results["message"] = "No features extracted from audio files"
            return results
        
        # Analyze trends by genre
        genres = {}
        for features in features_collection:
            genre = features.get("metadata", {}).get("genre")
            if genre:
                if genre not in genres:
                    genres[genre] = []
                genres[genre].append(features)
        
        # Update genre trends
        for genre, genre_features in genres.items():
            try:
                # Analyze genre trends
                segmentation = {"country": country_code, "genre": genre}
                trends = self.trend_analyzer.identify_trends_by_segment(
                    features_collection=genre_features,
                    segmentation=segmentation,
                    time_period=date
                )
                
                # Update genre trend in database
                if trends.get("status") == "success":
                    success = self.update_genre_trend(
                        country_code=country_code,
                        genre=genre,
                        date=date,
                        trend_data=trends
                    )
                    
                    if success:
                        results["genre_trends_updated"].append(genre)
                    else:
                        results["errors"].append({
                            "genre": genre,
                            "error": "Failed to update genre trend in database"
                        })
            except Exception as e:
                results["errors"].append({
                    "genre": genre,
                    "error": str(e)
                })
        
        # Update country profile with aggregated trends
        try:
            # Get existing profile or create new one
            profile = self.country_profiles_manager.get_country_profile(
                country_code=country_code,
                date=date
            ) or {}
            
            # Update profile with new data
            profile["timestamp"] = datetime.now().isoformat()
            profile["audio_feature_trends"] = self._aggregate_audio_features(features_collection)
            
            # Update genre trends summary
            genre_trends = []
            for genre in results["genre_trends_updated"]:
                genre_trend = self.country_profiles_manager.get_genre_trends(
                    country_code=country_code,
                    genre=genre,
                    date=date
                )
                if genre_trend:
                    genre_trends.append(genre_trend)
            
            profile["genre_trends"] = genre_trends
            
            # Update profile in database
            success = self.update_country_profile(
                country_code=country_code,
                date=date,
                profile_data=profile
            )
            
            results["trends_updated"] = success
            
            if not success:
                results["errors"].append({
                    "country": country_code,
                    "error": "Failed to update country profile in database"
                })
        except Exception as e:
            results["errors"].append({
                "country": country_code,
                "error": str(e)
            })
            results["trends_updated"] = False
        
        return results
    
    def _aggregate_audio_features(self, features_collection: List[Dict]) -> Dict:
        """
        Aggregate audio features from a collection of features.
        
        Args:
            features_collection (list): Collection of audio features
            
        Returns:
            dict: Aggregated audio features
        """
        # Extract relevant features for aggregation
        tempos = []
        energy_levels = []
        danceability_scores = []
        valence_values = []
        
        for features in features_collection:
            # Skip if status is not success
            if features.get("status") != "success":
                continue
            
            # Extract temporal features
            if "temporal" in features:
                tempo = features["temporal"].get("tempo")
                if tempo is not None:
                    tempos.append(tempo)
            
            # Extract high-level features
            if "high_level" in features:
                energy = features["high_level"].get("energy_level")
                danceability = features["high_level"].get("danceability")
                valence = features["high_level"].get("mood_valence")
                
                if energy is not None:
                    energy_levels.append(energy)
                if danceability is not None:
                    danceability_scores.append(danceability)
                if valence is not None and isinstance(valence, (int, float)):
                    valence_values.append(valence)
        
        # Calculate aggregated features
        aggregated = {}
        
        if tempos:
            aggregated["tempo"] = {
                "mean": sum(tempos) / len(tempos),
                "min": min(tempos),
                "max": max(tempos)
            }
        
        if energy_levels:
            aggregated["energy"] = {
                "mean": sum(energy_levels) / len(energy_levels),
                "min": min(energy_levels),
                "max": max(energy_levels)
            }
        
        if danceability_scores:
            aggregated["danceability"] = {
                "mean": sum(danceability_scores) / len(danceability_scores),
                "min": min(danceability_scores),
                "max": max(danceability_scores)
            }
        
        if valence_values:
            aggregated["valence"] = {
                "mean": sum(valence_values) / len(valence_values),
                "min": min(valence_values),
                "max": max(valence_values)
            }
        
        return aggregated
