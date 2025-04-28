"""
Schema Defaults Module

This module provides default values and factory functions for creating
schema-compliant artist profiles and settings.
"""

from datetime import datetime
from typing import Dict, Any, List
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("schema_defaults")


def create_default_settings() -> Dict[str, Any]:
    """
    Create default settings for a new artist profile.

    Returns:
        A dictionary with default settings values
    """
    logger.info("Creating default artist profile settings")

    return {
        "release_strategy": {
            "track_release_random_days": [3, 15],
            "video_release_ratio": 0.7,
        },
        "llm_assignments": {
            "artist_prompt_llm": "gpt-4",
            "song_prompt_llm": "gpt-4",
            "video_prompt_llm": "gpt-4",
            "final_validator_llm": "gpt-4",
        },
        "training_data_version": "1.0",
        "trend_alignment_behavior": "soft",
        "behavior_evolution_settings": {
            "allow_minor_genre_shifts": True,
            "allow_personality_shifts": True,
            "safe_mode": True,
        },
    }


def create_default_artist_profile(stage_name: str, genre: str) -> Dict[str, Any]:
    """
    Create a default artist profile with minimal required information.

    Args:
        stage_name: The artist's stage name
        genre: The artist's primary genre

    Returns:
        A dictionary with a minimal valid artist profile
    """
    logger.info(f"Creating default artist profile for {stage_name} ({genre})")

    # Generate a unique ID
    artist_id = (
        f"artist_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
    )

    # Default subgenres based on genre
    subgenres = get_default_subgenres(genre)

    # Default personality traits based on genre
    personality_traits = get_default_personality_traits(genre)

    # Create the profile
    profile = {
        "artist_id": artist_id,
        "stage_name": stage_name,
        "real_name": None,
        "genre": genre,
        "subgenres": subgenres,
        "style_description": f"A {genre} artist with a unique sound that blends traditional elements with modern production techniques.",
        "voice_type": f"Distinctive {genre.lower()} vocal style that resonates with listeners.",
        "personality_traits": personality_traits,
        "target_audience": get_default_target_audience(genre),
        "visual_identity_prompt": f"Professional portrait photograph of a {genre} artist with a distinctive style and presence.",
        "song_prompt_generator": f"Create a {genre} track that showcases the artist's unique sound and style.",
        "video_prompt_generator": f"Create a music video teaser for a {genre} track that captures the essence of the artist's identity.",
        "creation_date": datetime.now().date(),
        "update_history": [],
        "notes": f"Default profile created for {stage_name}, a {genre} artist.",
        "settings": create_default_settings(),
        "source_prompt": "",
        "session_id": "",
        "metadata": {},
    }

    # Add initial update history entry
    profile["update_history"].append(
        {"update_date": datetime.now().date(), "updated_fields": ["initial_creation"]}
    )

    return profile


def get_default_subgenres(genre: str) -> List[str]:
    """
    Get default subgenres based on a primary genre.

    Args:
        genre: The primary genre

    Returns:
        A list of related subgenres
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
        return [genre] + subgenre_map[genre_lower][:2]  # Primary genre + 2 subgenres
    else:
        return [genre, "Alternative", "Fusion"]


def get_default_personality_traits(genre: str) -> List[str]:
    """
    Get default personality traits based on a genre.

    Args:
        genre: The artist's genre

    Returns:
        A list of personality traits
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


def get_default_target_audience(genre: str) -> str:
    """
    Get default target audience based on a genre.

    Args:
        genre: The artist's genre

    Returns:
        A target audience description
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
