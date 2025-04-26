"""
Specialized prompt generation module for different artist aspects.

This module provides prompt generation capabilities for various aspects of artist creation,
including music creation, visual identity, and artist backstory enhancement.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("prompt_generators")


class MusicPromptGenerator:
    """
    Generates prompts for music creation based on artist profile.
    
    This class creates specialized prompts that can be used with music generation
    systems to create tracks that match the artist's style and genre.
    """
    
    def __init__(self, template_variety: int = 3):
        """
        Initialize the music prompt generator.
        
        Args:
            template_variety: Number of template variations to use
        """
        self.template_variety = template_variety
        logger.info("Initialized MusicPromptGenerator")
    
    def generate_track_prompt(
        self,
        artist_profile: Dict[str, Any],
        track_type: str = "main",
        duration_seconds: int = 180
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating a music track.
        
        Args:
            artist_profile: The artist profile containing genre, style, etc.
            track_type: Type of track (main, intro, outro, etc.)
            duration_seconds: Desired track duration in seconds
            
        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(f"Generating {track_type} track prompt for artist {artist_profile.get('name', 'Unknown')}")
        
        # This is a stub - would be replaced with actual implementation
        # that generates appropriate prompts based on the artist profile
        
        # Mock implementation for structure
        return {
            "prompt": f"Create a {artist_profile.get('genre', 'Unknown')} track with {artist_profile.get('style', 'Unknown')} vibes",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "duration_seconds": duration_seconds,
                "track_type": track_type
            },
            "system_instructions": "The track should match the artist's unique style and sound signature."
        }
    
    def generate_album_concept(
        self,
        artist_profile: Dict[str, Any],
        track_count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a concept for an entire album including track list.
        
        Args:
            artist_profile: The artist profile containing genre, style, etc.
            track_count: Number of tracks to include in the album
            
        Returns:
            Dictionary containing the album concept and track prompts
        """
        logger.info(f"Generating album concept for artist {artist_profile.get('name', 'Unknown')}")
        
        # This is a stub - would be replaced with actual implementation
        
        # Mock implementation for structure
        tracks = []
        for i in range(track_count):
            tracks.append({
                "title": f"Track {i+1}",
                "prompt": f"Create a {artist_profile.get('genre', 'Unknown')} track number {i+1} for the album",
                "duration_seconds": 180 + (i * 30)  # Varying durations
            })
        
        return {
            "album_title": "Album Title",
            "concept": "Album concept description",
            "tracks": tracks,
            "total_duration_minutes": sum(t["duration_seconds"] for t in tracks) // 60
        }


class VisualPromptGenerator:
    """
    Generates prompts for visual asset creation based on artist profile.
    
    This class creates specialized prompts that can be used with image generation
    systems to create visual assets that match the artist's identity.
    """
    
    def __init__(self):
        """Initialize the visual prompt generator."""
        logger.info("Initialized VisualPromptGenerator")
    
    def generate_profile_image_prompt(
        self,
        artist_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating an artist profile image.
        
        Args:
            artist_profile: The artist profile containing style, appearance, etc.
            
        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(f"Generating profile image prompt for artist {artist_profile.get('name', 'Unknown')}")
        
        # This is a stub - would be replaced with actual implementation
        
        # Mock implementation for structure
        return {
            "prompt": f"Create a profile image for a {artist_profile.get('genre', 'Unknown')} artist with {artist_profile.get('style', 'Unknown')} aesthetic",
            "parameters": {
                "style": artist_profile.get("style", "Unknown"),
                "appearance": artist_profile.get("appearance", "Unknown"),
                "mood": "professional, artistic",
                "format": "portrait"
            },
            "negative_prompt": "low quality, blurry, distorted"
        }
    
    def generate_album_cover_prompt(
        self,
        artist_profile: Dict[str, Any],
        album_concept: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating an album cover.
        
        Args:
            artist_profile: The artist profile containing style, genre, etc.
            album_concept: Optional album concept information
            
        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(f"Generating album cover prompt for artist {artist_profile.get('name', 'Unknown')}")
        
        # This is a stub - would be replaced with actual implementation
        
        # Mock implementation for structure
        album_title = album_concept.get("album_title", "Untitled Album") if album_concept else "Untitled Album"
        
        return {
            "prompt": f"Create an album cover for '{album_title}' by {artist_profile.get('name', 'Unknown')}, a {artist_profile.get('genre', 'Unknown')} artist",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "title": album_title,
                "format": "square, high resolution"
            },
            "negative_prompt": "text, words, low quality, blurry"
        }


class BackstoryPromptGenerator:
    """
    Generates prompts for enhancing artist backstory and personality.
    
    This class creates specialized prompts that can be used to develop
    rich backstories and personalities for artists.
    """
    
    def __init__(self):
        """Initialize the backstory prompt generator."""
        logger.info("Initialized BackstoryPromptGenerator")
    
    def generate_backstory_prompt(
        self,
        artist_profile: Dict[str, Any],
        depth: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating or enhancing an artist backstory.
        
        Args:
            artist_profile: The artist profile containing basic information
            depth: Level of detail for the backstory (brief, detailed, comprehensive)
            
        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(f"Generating {depth} backstory prompt for artist {artist_profile.get('name', 'Unknown')}")
        
        # This is a stub - would be replaced with actual implementation
        
        # Mock implementation for structure
        return {
            "prompt": f"Create a {depth} backstory for {artist_profile.get('name', 'Unknown')}, a {artist_profile.get('genre', 'Unknown')} artist",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "depth": depth,
                "focus_areas": ["origin", "influences", "journey", "philosophy"]
            },
            "system_instructions": "Create a compelling and authentic backstory that aligns with the artist's musical style and genre."
        }
    
    def generate_social_media_persona_prompt(
        self,
        artist_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating a social media persona for the artist.
        
        Args:
            artist_profile: The artist profile containing style, genre, etc.
            
        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(f"Generating social media persona prompt for artist {artist_profile.get('name', 'Unknown')}")
        
        # This is a stub - would be replaced with actual implementation
        
        # Mock implementation for structure
        return {
            "prompt": f"Create a social media persona for {artist_profile.get('name', 'Unknown')}, a {artist_profile.get('genre', 'Unknown')} artist",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "platforms": ["Instagram", "Twitter", "TikTok"],
                "tone": "authentic, engaging, mysterious"
            },
            "system_instructions": "Create a consistent and engaging social media persona that will resonate with fans of the genre."
        }


# Factory function to get appropriate prompt generator
def get_prompt_generator(generator_type: str) -> Any:
    """
    Factory function to get the appropriate prompt generator.
    
    Args:
        generator_type: Type of generator to return (music, visual, backstory)
        
    Returns:
        Instance of the requested generator
    """
    generators = {
        "music": MusicPromptGenerator(),
        "visual": VisualPromptGenerator(),
        "backstory": BackstoryPromptGenerator()
    }
    
    return generators.get(generator_type.lower(), MusicPromptGenerator())


# Example usage
if __name__ == "__main__":
    # Example artist profile
    example_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "background": "Urban night life"
    }
    
    # Get a music prompt generator
    music_gen = get_prompt_generator("music")
    
    # Generate a track prompt
    track_prompt = music_gen.generate_track_prompt(example_profile)
    
    # Print the result
    import json
    print(json.dumps(track_prompt, indent=2))
