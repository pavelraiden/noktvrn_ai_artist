"""
Artist Initializer module for creating new artist profiles.

This module provides functionality for initializing new artist profiles
based on user input, applying default values where needed, and validating
the resulting profiles.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import yaml

from .artist import Artist

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_manager.artist_initializer")


class ArtistInitializer:
    """
    Class for initializing new artist profiles based on user input.
    
    This class provides methods for creating new artist profiles,
    applying default values, and validating the resulting profiles.
    """
    
    def __init__(self, schema_path: Optional[str] = None, defaults_path: Optional[str] = None):
        """
        Initialize an ArtistInitializer instance.
        
        Args:
            schema_path: Optional path to the schema file (uses default if None)
            defaults_path: Optional path to the defaults file (uses default if None)
        """
        # Set default schema path if not provided
        if schema_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(current_dir, "artist_profile_schema.yaml")
        
        self.schema_path = schema_path
        
        # Load schema
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = yaml.safe_load(f)
            logger.debug("Successfully loaded schema")
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            raise ValueError(f"Failed to load schema from {self.schema_path}: {str(e)}")
        
        # Load defaults if provided, otherwise use built-in defaults
        self.defaults = self._get_default_values()
    
    def _get_default_values(self) -> Dict[str, Any]:
        """
        Get default values for artist profile fields.
        
        Returns:
            Dictionary containing default values
        """
        # Default LLM assignments
        default_llm_assignments = {
            "artist_prompt_llm": "gpt-4",
            "song_prompt_llm": "gpt-4",
            "video_prompt_llm": "gpt-4",
            "final_validator_llm": "gpt-4"
        }
        
        # Default release strategy
        default_release_strategy = {
            "track_release_random_days": [3, 15],
            "video_release_ratio": 0.7,
            "content_plan_length_days": 90,
            "social_media_post_frequency": 3
        }
        
        # Default behavior evolution settings
        default_behavior_evolution = {
            "allow_minor_genre_shifts": True,
            "allow_personality_shifts": True,
            "safe_mode": True,
            "evolution_speed": "medium",
            "preserve_core_identity": True
        }
        
        # Default social media presence
        default_social_media = {
            "platforms": ["instagram", "tiktok", "twitter"],
            "posting_style": "casual",
            "engagement_strategy": "moderate"
        }
        
        # Default settings
        default_settings = {
            "release_strategy": default_release_strategy,
            "llm_assignments": default_llm_assignments,
            "training_data_version": "1.0",
            "trend_alignment_behavior": "soft",
            "behavior_evolution_settings": default_behavior_evolution,
            "social_media_presence": default_social_media,
            "performance_metrics_tracking": True
        }
        
        return {
            "settings": default_settings,
            "is_active": True,
            "update_history": [],
            "metadata": {}
        }
    
    def _get_default_subgenres(self, genre: str) -> List[str]:
        """
        Get default subgenres based on a primary genre.
        
        Args:
            genre: The primary genre
            
        Returns:
            List of related subgenres
        """
        genre_lower = genre.lower()
        
        # Define related subgenres for common genres
        subgenre_map = {
            "trap": ["Hip Hop", "Dark Trap", "Cloud Rap"],
            "electronic": ["EDM", "House", "Techno"],
            "hip hop": ["Trap", "Boom Bap", "Conscious"],
            "pop": ["Electropop", "Dance Pop", "Indie Pop"],
            "rock": ["Alternative", "Indie Rock", "Hard Rock"],
            "r&b": ["Soul", "Contemporary R&B", "Neo Soul"],
            "jazz": ["Contemporary Jazz", "Fusion", "Smooth Jazz"],
            "classical": ["Neo-Classical", "Orchestral", "Piano"],
            "country": ["Modern Country", "Folk", "Americana"],
            "metal": ["Heavy Metal", "Thrash", "Metalcore"],
        }
        
        # Return matching subgenres or generic ones
        if genre_lower in subgenre_map:
            return subgenre_map[genre_lower][:2]  # Return 2 subgenres
        else:
            return ["Alternative", "Fusion"]
    
    def _get_default_personality_traits(self, genre: str) -> List[str]:
        """
        Get default personality traits based on a genre.
        
        Args:
            genre: The artist's genre
            
        Returns:
            List of personality traits
        """
        genre_lower = genre.lower()
        
        # Define personality traits for common genres
        trait_map = {
            "trap": ["Mysterious", "Intense", "Authentic"],
            "electronic": ["Innovative", "Energetic", "Futuristic"],
            "hip hop": ["Confident", "Authentic", "Expressive"],
            "pop": ["Charismatic", "Approachable", "Versatile"],
            "rock": ["Passionate", "Rebellious", "Authentic"],
            "r&b": ["Sensual", "Emotional", "Soulful"],
            "jazz": ["Sophisticated", "Improvisational", "Expressive"],
            "classical": ["Disciplined", "Refined", "Emotional"],
            "country": ["Authentic", "Relatable", "Storytelling"],
            "metal": ["Intense", "Powerful", "Technical"],
        }
        
        # Return matching traits or generic ones
        if genre_lower in trait_map:
            return trait_map[genre_lower]
        else:
            return ["Creative", "Unique", "Authentic"]
    
    def _get_default_target_audience(self, genre: str) -> str:
        """
        Get default target audience based on a genre.
        
        Args:
            genre: The artist's genre
            
        Returns:
            Target audience description
        """
        genre_lower = genre.lower()
        
        # Define target audiences for common genres
        audience_map = {
            "trap": "Young urban listeners who appreciate dark atmospheric beats",
            "electronic": "EDM enthusiasts and festival-goers seeking energetic dance music",
            "hip hop": "Hip-hop fans who value authentic storytelling and strong beats",
            "pop": "Mainstream listeners looking for catchy, accessible music",
            "rock": "Rock fans who appreciate guitar-driven music with attitude",
            "r&b": "Listeners who enjoy smooth, soulful vocals and emotional depth",
            "jazz": "Sophisticated listeners who appreciate musical complexity and improvisation",
            "classical": "Classical music enthusiasts and those seeking emotional orchestral pieces",
            "country": "Country music fans who connect with authentic storytelling and traditional sounds",
            "metal": "Metal enthusiasts seeking intense, powerful music with technical skill",
        }
        
        # Return matching audience or generic one
        if genre_lower in audience_map:
            return audience_map[genre_lower]
        else:
            return "Music fans who appreciate unique and creative artistic expression"
    
    def initialize_artist(self, user_input: Dict[str, Any]) -> Tuple[Artist, List[str]]:
        """
        Initialize a new artist profile based on user input.
        
        Args:
            user_input: Dictionary containing user-provided artist information
            
        Returns:
            Tuple containing (Artist instance, warnings list)
        """
        warnings = []
        
        # Start with required fields
        if "stage_name" not in user_input:
            warnings.append("Missing stage_name, using placeholder")
            user_input["stage_name"] = f"Artist_{uuid.uuid4().hex[:8]}"
        
        if "genre" not in user_input:
            warnings.append("Missing genre, using 'Electronic' as default")
            user_input["genre"] = "Electronic"
        
        # Generate artist_id if not provided
        if "artist_id" not in user_input:
            user_input["artist_id"] = str(uuid.uuid4())
        
        # Set creation date
        user_input["creation_date"] = datetime.now().isoformat()
        
        # Apply default subgenres if not provided
        if "subgenres" not in user_input or not user_input["subgenres"]:
            user_input["subgenres"] = self._get_default_subgenres(user_input["genre"])
            warnings.append(f"Using default subgenres for {user_input['genre']}")
        
        # Apply default personality traits if not provided
        if "personality_traits" not in user_input or not user_input["personality_traits"]:
            user_input["personality_traits"] = self._get_default_personality_traits(user_input["genre"])
            warnings.append("Using default personality traits")
        
        # Apply default target audience if not provided
        if "target_audience" not in user_input or not user_input["target_audience"]:
            user_input["target_audience"] = self._get_default_target_audience(user_input["genre"])
            warnings.append("Using default target audience")
        
        # Apply default style description if not provided
        if "style_description" not in user_input or not user_input["style_description"]:
            user_input["style_description"] = f"A {user_input['genre']} artist with a unique sound that blends traditional elements with modern production techniques."
            warnings.append("Using default style description")
        
        # Apply default voice characteristics if not provided
        if "voice_type" not in user_input or not user_input["voice_type"]:
            user_input["voice_type"] = f"Distinctive {user_input['genre'].lower()} vocal style that resonates with listeners."
            warnings.append("Using default voice characteristics")
        
        # Apply default visual identity prompt if not provided
        if "visual_identity_prompt" not in user_input or not user_input["visual_identity_prompt"]:
            user_input["visual_identity_prompt"] = f"Professional portrait photograph of a {user_input['genre']} artist with a distinctive style and presence."
            warnings.append("Using default visual identity prompt")
        
        # Apply default settings if not provided
        if "settings" not in user_input:
            user_input["settings"] = self.defaults["settings"]
            warnings.append("Using default settings")
        else:
            # Merge with default settings for any missing nested settings
            default_settings = self.defaults["settings"]
            
            # Check and apply default release strategy
            if "release_strategy" not in user_input["settings"]:
                user_input["settings"]["release_strategy"] = default_settings["release_strategy"]
                warnings.append("Using default release strategy")
            
            # Check and apply default LLM assignments
            if "llm_assignments" not in user_input["settings"]:
                user_input["settings"]["llm_assignments"] = default_settings["llm_assignments"]
                warnings.append("Using default LLM assignments")
            
            # Check and apply default training data version
            if "training_data_version" not in user_input["settings"]:
                user_input["settings"]["training_data_version"] = default_settings["training_data_version"]
                warnings.append("Using default training data version")
            
            # Check and apply default trend alignment behavior
            if "trend_alignment_behavior" not in user_input["settings"]:
                user_input["settings"]["trend_alignment_behavior"] = default_settings["trend_alignment_behavior"]
                warnings.append("Using default trend alignment behavior")
            
            # Check and apply default behavior evolution settings
            if "behavior_evolution_settings" not in user_input["settings"]:
                user_input["settings"]["behavior_evolution_settings"] = default_settings["behavior_evolution_settings"]
                warnings.append("Using default behavior evolution settings")
            
            # Check and apply default social media presence
            if "social_media_presence" not in user_input["settings"]:
                user_input["settings"]["social_media_presence"] = default_settings["social_media_presence"]
                warnings.append("Using default social media presence")
        
        # Create initial update history entry
        user_input["update_history"] = [{
            "update_date": datetime.now().date().isoformat(),
            "updated_fields": ["initial_creation"],
            "update_source": "artist_initializer"
        }]
        
        # Create and validate the artist profile
        artist = Artist(user_input, self.schema_path)
        is_valid, errors = artist.validate()
        
        if not is_valid:
            warnings.append(f"Validation errors in initialized profile: {errors}")
        
        logger.info(f"Initialized artist profile for {user_input.get('stage_name')} with {len(warnings)} warnings")
        return artist, warnings
    
    def create_minimal_artist(self, stage_name: str, genre: str) -> Artist:
        """
        Create a minimal valid artist profile with just stage name and genre.
        
        Args:
            stage_name: The artist's stage name
            genre: The artist's primary genre
            
        Returns:
            Artist instance with a valid minimal profile
        """
        user_input = {
            "stage_name": stage_name,
            "genre": genre
        }
        
        artist, warnings = self.initialize_artist(user_input)
        if warnings:
            logger.info(f"Created minimal artist with {len(warnings)} warnings")
        
        return artist
