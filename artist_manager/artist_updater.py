"""
Artist Updater module for updating existing artist profiles.

This module provides functionality for updating existing artist profiles,
allowing dynamic style evolution based on trend analyzer output, and
logging all changes for transparency and analysis.
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import logging

from .artist import Artist

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_manager.artist_updater")


class ArtistUpdater:
    """
    Class for updating existing artist profiles.
    
    This class provides methods for updating artist profiles,
    allowing dynamic style evolution, and logging all changes.
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize an ArtistUpdater instance.
        
        Args:
            schema_path: Optional path to the schema file (uses default if None)
        """
        # Set default schema path if not provided
        if schema_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(current_dir, "artist_profile_schema.yaml")
        
        self.schema_path = schema_path
    
    def update_artist(self, artist: Artist, updates: Dict[str, Any], 
                     update_reason: Optional[str] = None, 
                     update_source: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Update an existing artist profile with new values.
        
        Args:
            artist: The Artist instance to update
            updates: Dictionary of fields to update
            update_reason: Optional reason for the update
            update_source: Optional source of the update
            
        Returns:
            Tuple containing (success, warnings)
        """
        warnings = []
        
        # Validate that we're working with an Artist instance
        if not isinstance(artist, Artist):
            error_msg = "artist must be an instance of Artist"
            logger.error(error_msg)
            return False, [error_msg]
        
        # Apply updates
        success = artist.update(updates, update_reason, update_source)
        
        if not success:
            error_msg = "Failed to update artist profile"
            logger.error(error_msg)
            return False, [error_msg]
        
        # Validate the updated profile
        is_valid, errors = artist.validate()
        
        if not is_valid:
            warnings.append(f"Updated profile has validation errors: {errors}")
            logger.warning(f"Updated profile has validation errors: {errors}")
        
        logger.info(f"Updated artist profile with {len(updates)} fields")
        return True, warnings
    
    def apply_trend_updates(self, artist: Artist, trend_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Update an artist profile based on trend analyzer output.
        
        Args:
            artist: The Artist instance to update
            trend_data: Dictionary containing trend analysis data
            
        Returns:
            Tuple containing (success, applied_updates, warnings)
        """
        warnings = []
        applied_updates = []
        
        # Validate that we're working with an Artist instance
        if not isinstance(artist, Artist):
            error_msg = "artist must be an instance of Artist"
            logger.error(error_msg)
            return False, [], [error_msg]
        
        # Get current artist settings
        trend_alignment = artist.get_value("settings.trend_alignment_behavior", "soft")
        evolution_settings = artist.get_value("settings.behavior_evolution_settings", {})
        
        # Determine how aggressively to apply trend updates based on alignment setting
        if trend_alignment == "strict":
            adaptation_threshold = 0.3  # Lower threshold means more changes
        elif trend_alignment == "soft":
            adaptation_threshold = 0.6  # Medium threshold
        else:  # experimental
            adaptation_threshold = 0.8  # High threshold means fewer changes
        
        # Check if evolution is allowed
        allow_genre_shifts = evolution_settings.get("allow_minor_genre_shifts", True)
        allow_personality_shifts = evolution_settings.get("allow_personality_shifts", True)
        safe_mode = evolution_settings.get("safe_mode", True)
        evolution_speed = evolution_settings.get("evolution_speed", "medium")
        preserve_core = evolution_settings.get("preserve_core_identity", True)
        
        # Adjust adaptation threshold based on evolution speed
        if evolution_speed == "fast":
            adaptation_threshold *= 0.7  # Lower threshold for faster evolution
        elif evolution_speed == "slow":
            adaptation_threshold *= 1.3  # Higher threshold for slower evolution
        
        # Prepare updates dictionary
        updates = {}
        
        # Process genre trends if allowed
        if allow_genre_shifts and "genre_trends" in trend_data:
            genre_trends = trend_data["genre_trends"]
            
            # Check if any genre trend is strong enough to influence the artist
            for genre, score in genre_trends.items():
                if score > adaptation_threshold:
                    # Don't change primary genre if preserving core identity
                    if preserve_core:
                        # Add to subgenres if not already present
                        current_subgenres = artist.get_value("subgenres", [])
                        if genre not in current_subgenres and genre != artist.get_value("genre"):
                            updates["subgenres"] = current_subgenres + [genre]
                            applied_updates.append(f"Added {genre} to subgenres")
                    else:
                        # Can change primary genre
                        updates["genre"] = genre
                        applied_updates.append(f"Updated primary genre to {genre}")
                        
                        # Update style description to reflect new genre
                        current_style = artist.get_value("style_description", "")
                        updates["style_description"] = f"A {genre} artist with {current_style.split('with')[1] if 'with' in current_style else 'a unique style'}"
                        applied_updates.append("Updated style description to match new genre")
        
        # Process personality trends if allowed
        if allow_personality_shifts and "personality_trends" in trend_data:
            personality_trends = trend_data["personality_trends"]
            
            # Check if any personality trend is strong enough to influence the artist
            for trait, score in personality_trends.items():
                if score > adaptation_threshold:
                    current_traits = artist.get_value("personality_traits", [])
                    if trait not in current_traits:
                        # Replace a trait or add a new one
                        if len(current_traits) >= 3 and preserve_core:
                            # Replace the last trait if preserving core identity
                            new_traits = current_traits[:-1] + [trait]
                            updates["personality_traits"] = new_traits
                            applied_updates.append(f"Replaced personality trait with {trait}")
                        else:
                            # Add a new trait
                            updates["personality_traits"] = current_traits + [trait]
                            applied_updates.append(f"Added {trait} to personality traits")
        
        # Process visual trends if present
        if "visual_trends" in trend_data:
            visual_trends = trend_data["visual_trends"]
            
            # Check if any visual trend is strong enough to influence the artist
            for style, score in visual_trends.items():
                if score > adaptation_threshold:
                    # Update visual identity prompt
                    current_prompt = artist.get_value("visual_identity_prompt", "")
                    if style.lower() not in current_prompt.lower():
                        updates["visual_identity_prompt"] = f"{current_prompt} Incorporate {style} visual elements."
                        applied_updates.append(f"Updated visual identity with {style} elements")
        
        # Process audience trends if present
        if "audience_trends" in trend_data:
            audience_trends = trend_data["audience_trends"]
            
            # Check if any audience trend is strong enough to influence the artist
            for audience, score in audience_trends.items():
                if score > adaptation_threshold:
                    # Update target audience
                    current_audience = artist.get_value("target_audience", "")
                    if audience.lower() not in current_audience.lower():
                        updates["target_audience"] = f"{current_audience} with appeal to {audience} listeners."
                        applied_updates.append(f"Expanded target audience to include {audience}")
        
        # Process release strategy trends if present
        if "release_trends" in trend_data:
            release_trends = trend_data["release_trends"]
            
            # Check if release frequency trend is present and significant
            if "frequency" in release_trends and release_trends["frequency"] > adaptation_threshold:
                current_days = artist.get_value("settings.release_strategy.track_release_random_days", [3, 15])
                
                # Adjust release frequency based on trend
                trend_value = release_trends["frequency"]
                if trend_value > 0.8:  # Very high frequency
                    new_days = [max(1, current_days[0] - 1), max(3, current_days[1] - 2)]
                elif trend_value > 0.6:  # High frequency
                    new_days = [max(1, current_days[0]), max(5, current_days[1] - 1)]
                elif trend_value < 0.3:  # Low frequency
                    new_days = [min(10, current_days[0] + 1), min(30, current_days[1] + 2)]
                elif trend_value < 0.5:  # Moderate-low frequency
                    new_days = [min(7, current_days[0] + 1), min(21, current_days[1] + 1)]
                else:
                    new_days = current_days  # No change
                
                if new_days != current_days:
                    updates["settings.release_strategy.track_release_random_days"] = new_days
                    applied_updates.append(f"Updated release frequency to {new_days[0]}-{new_days[1]} days")
            
            # Check if video ratio trend is present and significant
            if "video_ratio" in release_trends and release_trends["video_ratio"] > adaptation_threshold:
                current_ratio = artist.get_value("settings.release_strategy.video_release_ratio", 0.7)
                
                # Adjust video ratio based on trend
                trend_value = release_trends["video_ratio"]
                if trend_value > 0.8:  # Very high video emphasis
                    new_ratio = min(1.0, current_ratio + 0.1)
                elif trend_value > 0.6:  # High video emphasis
                    new_ratio = min(1.0, current_ratio + 0.05)
                elif trend_value < 0.3:  # Low video emphasis
                    new_ratio = max(0.2, current_ratio - 0.1)
                elif trend_value < 0.5:  # Moderate-low video emphasis
                    new_ratio = max(0.3, current_ratio - 0.05)
                else:
                    new_ratio = current_ratio  # No change
                
                if abs(new_ratio - current_ratio) > 0.01:  # Only update if significant change
                    updates["settings.release_strategy.video_release_ratio"] = round(new_ratio, 2)
                    applied_updates.append(f"Updated video release ratio to {round(new_ratio, 2)}")
        
        # Process social media trends if present
        if "social_media_trends" in trend_data:
            social_trends = trend_data["social_media_trends"]
            
            # Check if platform trends are present and significant
            if "platforms" in social_trends:
                for platform, score in social_trends["platforms"].items():
                    if score > adaptation_threshold:
                        current_platforms = artist.get_value("settings.social_media_presence.platforms", [])
                        if platform not in current_platforms:
                            updates["settings.social_media_presence.platforms"] = current_platforms + [platform]
                            applied_updates.append(f"Added {platform} to social media platforms")
            
            # Check if posting style trend is present and significant
            if "posting_style" in social_trends and social_trends["posting_style"] > adaptation_threshold:
                current_style = artist.get_value("settings.social_media_presence.posting_style", "casual")
                
                # Determine new style based on trend value
                trend_value = social_trends["posting_style"]
                if trend_value > 0.7:
                    new_style = "professional"
                elif trend_value < 0.4:
                    new_style = "mysterious"
                else:
                    new_style = "casual"
                
                if new_style != current_style:
                    updates["settings.social_media_presence.posting_style"] = new_style
                    applied_updates.append(f"Updated social media posting style to {new_style}")
        
        # If no updates were generated, add a warning
        if not updates:
            warnings.append("No updates were applied based on trend data")
            logger.info("No updates were applied based on trend data")
            return True, [], warnings
        
        # Apply the updates
        success = artist.update(updates, "Trend-based evolution", "trend_analyzer")
        
        if not success:
            error_msg = "Failed to apply trend-based updates"
            logger.error(error_msg)
            return False, [], [error_msg]
        
        # Validate the updated profile
        is_valid, errors = artist.validate()
        
        if not is_valid:
            warnings.append(f"Updated profile has validation errors: {errors}")
            logger.warning(f"Updated profile has validation errors: {errors}")
        
        logger.info(f"Applied {len(applied_updates)} trend-based updates to artist profile")
        return True, applied_updates, warnings
    
    def save_update_log(self, artist: Artist, updates: List[str], log_dir: str) -> bool:
        """
        Save a log of applied updates for transparency and analysis.
        
        Args:
            artist: The Artist instance that was updated
            updates: List of update descriptions
            log_dir: Directory to save the log file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)
            
            # Create log entry
            log_entry = {
                "artist_id": artist.get_value("artist_id"),
                "stage_name": artist.get_value("stage_name"),
                "timestamp": datetime.now().isoformat(),
                "updates": updates
            }
            
            # Generate log filename
            filename = f"{log_entry['artist_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_update.json"
            file_path = os.path.join(log_dir, filename)
            
            # Write log file
            with open(file_path, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            logger.info(f"Saved update log to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving update log: {str(e)}")
            return False
    
    def load_artist_from_file(self, file_path: str) -> Artist:
        """
        Load an artist profile from a file.
        
        Args:
            file_path: Path to the artist profile file (JSON or YAML)
            
        Returns:
            Artist instance with the loaded profile
        """
        return Artist.load(file_path, self.schema_path)
    
    def save_artist_to_file(self, artist: Artist, file_path: str, format: str = "json") -> bool:
        """
        Save an artist profile to a file.
        
        Args:
            artist: The Artist instance to save
            file_path: Path to save the file
            format: Format to save as ("json" or "yaml")
            
        Returns:
            True if successful, False otherwise
        """
        return artist.save(file_path, format)
