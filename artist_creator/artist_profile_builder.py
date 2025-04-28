"""
Artist Profile Builder module for creating comprehensive artist profiles.

This module handles the creation of artist profiles with specified characteristics
and stores them in the appropriate directory structure.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_profile_builder")

class ArtistProfileBuilder:
    """
    Creates and manages artist profiles with specified characteristics.
    
    This class handles the creation of detailed artist profiles based on input parameters
    and ensures they are stored in the appropriate directory structure.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the ArtistProfileBuilder.
        
        Args:
            base_dir: Base directory for storing artist profiles. Defaults to project's artists directory.
        """
        if base_dir is None:
            # Use the default artists directory in the project
            self.base_dir = Path(__file__).resolve().parents[1] / "artists"
        else:
            self.base_dir = Path(base_dir)
        
        logger.info(f"Initialized ArtistProfileBuilder with base directory: {self.base_dir}")
    
    def create_artist_profile(
        self,
        artist_name: str,
        main_genre: str,
        subgenres: List[str],
        style_tags: List[str],
        vibe_description: str,
        target_audience: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive artist profile and save it to the appropriate location.
        
        Args:
            artist_name: Name of the artist
            main_genre: Primary music genre
            subgenres: List of secondary genres
            style_tags: List of style descriptors
            vibe_description: Textual description of the artist's vibe/atmosphere
            target_audience: Description of the target audience
            additional_info: Optional additional information to include in the profile
            
        Returns:
            Dictionary containing the complete artist profile
        """
        logger.info(f"Creating artist profile for: {artist_name}")
        
        # Generate artist slug from name
        artist_slug = self._generate_artist_slug(artist_name)
        
        # Create the artist profile
        profile = {
            "artist_id": str(uuid.uuid4()),
            "name": artist_name,
            "slug": artist_slug,
            "music": {
                "main_genre": main_genre,
                "subgenres": subgenres,
                "style_tags": style_tags,
                "vibe": vibe_description
            },
            "audience": {
                "target_description": target_audience,
                "platforms": self._suggest_platforms(main_genre, target_audience)
            },
            "personality": self._generate_personality(main_genre, style_tags, vibe_description),
            "visual_style": self._generate_visual_style(main_genre, style_tags, vibe_description),
            "creation_info": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Add any additional information if provided
        if additional_info:
            profile.update(additional_info)
        
        # Ensure the artist directory exists
        artist_dir = self.base_dir / artist_slug
        artist_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (artist_dir / "prompts").mkdir(exist_ok=True)
        (artist_dir / "lyrics").mkdir(exist_ok=True)
        
        # Save the profile to a JSON file
        profile_path = artist_dir / "profile.json"
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
        
        logger.info(f"Artist profile created and saved to: {profile_path}")
        
        return profile
    
    def _generate_artist_slug(self, artist_name: str) -> str:
        """
        Generate a URL-friendly slug from the artist name.
        
        Args:
            artist_name: The artist's name
            
        Returns:
            A lowercase, hyphenated slug
        """
        # Convert to lowercase, replace spaces with hyphens, remove special characters
        slug = artist_name.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        return slug
    
    def _suggest_platforms(self, genre: str, target_audience: str) -> List[str]:
        """
        Suggest appropriate platforms based on genre and target audience.
        
        Args:
            genre: The artist's main genre
            target_audience: Description of the target audience
            
        Returns:
            List of suggested platforms
        """
        # This is a simplified implementation - would be more sophisticated in production
        platforms = ["Spotify", "YouTube"]
        
        # Add genre-specific platforms
        if "electronic" in genre.lower() or "edm" in genre.lower() or "techno" in genre.lower():
            platforms.append("SoundCloud")
            platforms.append("Beatport")
        
        if "hip hop" in genre.lower() or "rap" in genre.lower():
            platforms.append("SoundCloud")
            platforms.append("TikTok")
        
        if "indie" in genre.lower() or "alternative" in genre.lower():
            platforms.append("Bandcamp")
        
        # Add audience-specific platforms
        if "young" in target_audience.lower() or "teen" in target_audience.lower():
            platforms.append("TikTok")
            platforms.append("Instagram")
        
        if "professional" in target_audience.lower() or "adult" in target_audience.lower():
            platforms.append("Apple Music")
        
        return list(set(platforms))  # Remove duplicates
    
    def _generate_personality(self, genre: str, style_tags: List[str], vibe: str) -> Dict[str, Any]:
        """
        Generate a personality profile based on musical characteristics.
        
        Args:
            genre: The artist's main genre
            style_tags: List of style descriptors
            vibe: Description of the artist's vibe/atmosphere
            
        Returns:
            Dictionary containing personality traits
        """
        # This is a simplified implementation - would be more sophisticated in production
        # In a real implementation, this would use more advanced NLP or a dedicated model
        
        # Extract key words from inputs
        all_inputs = f"{genre} {' '.join(style_tags)} {vibe}".lower()
        
        # Define base personality
        personality = {
            "traits": [],
            "communication_style": "",
            "public_persona": "",
            "backstory": ""
        }
        
        # Assign traits based on keywords
        if any(word in all_inputs for word in ["dark", "mysterious", "enigmatic", "shadowy"]):
            personality["traits"].extend(["mysterious", "reserved", "introspective"])
            personality["communication_style"] = "cryptic and minimal"
            personality["public_persona"] = "enigmatic figure who rarely reveals personal details"
        
        elif any(word in all_inputs for word in ["energetic", "upbeat", "bright", "positive"]):
            personality["traits"].extend(["energetic", "optimistic", "outgoing"])
            personality["communication_style"] = "enthusiastic and direct"
            personality["public_persona"] = "vibrant personality who engages actively with fans"
        
        elif any(word in all_inputs for word in ["chill", "relaxed", "calm", "ambient"]):
            personality["traits"].extend(["laid-back", "thoughtful", "peaceful"])
            personality["communication_style"] = "calm and measured"
            personality["public_persona"] = "serene presence focused on the art"
        
        elif any(word in all_inputs for word in ["intense", "aggressive", "powerful", "heavy"]):
            personality["traits"].extend(["intense", "passionate", "determined"])
            personality["communication_style"] = "bold and assertive"
            personality["public_persona"] = "powerful presence with strong opinions"
        
        else:
            # Default personality if no specific keywords match
            personality["traits"].extend(["creative", "authentic", "passionate"])
            personality["communication_style"] = "genuine and thoughtful"
            personality["public_persona"] = "artist focused on musical expression"
        
        # Generate a basic backstory based on genre
        if "electronic" in genre.lower():
            personality["backstory"] = "Began producing music in their bedroom studio, gradually developing a unique sound that caught attention online."
        elif "rock" in genre.lower():
            personality["backstory"] = "Started in small local venues, building a following through energetic live performances and authentic songwriting."
        elif "hip hop" in genre.lower() or "rap" in genre.lower():
            personality["backstory"] = "Emerged from the underground scene with distinctive flow and lyrical prowess, gaining recognition through mixtapes and collaborations."
        else:
            personality["backstory"] = "Developed their musical style through years of experimentation, drawing inspiration from diverse influences to create a unique sound."
        
        return personality
    
    def _generate_visual_style(self, genre: str, style_tags: List[str], vibe: str) -> Dict[str, Any]:
        """
        Generate visual style guidelines based on musical characteristics.
        
        Args:
            genre: The artist's main genre
            style_tags: List of style descriptors
            vibe: Description of the artist's vibe/atmosphere
            
        Returns:
            Dictionary containing visual style guidelines
        """
        # This is a simplified implementation - would be more sophisticated in production
        # In a real implementation, this would use more advanced NLP or a dedicated model
        
        # Extract key words from inputs
        all_inputs = f"{genre} {' '.join(style_tags)} {vibe}".lower()
        
        # Define base visual style
        visual_style = {
            "color_palette": [],
            "imagery_themes": [],
            "typography": "",
            "composition": ""
        }
        
        # Assign visual elements based on keywords
        if any(word in all_inputs for word in ["dark", "mysterious", "enigmatic", "shadowy"]):
            visual_style["color_palette"] = ["deep blue", "black", "purple", "dark gray"]
            visual_style["imagery_themes"] = ["night scenes", "shadows", "abstract patterns", "minimal landscapes"]
            visual_style["typography"] = "elegant serif or thin sans-serif, often in uppercase with significant spacing"
            visual_style["composition"] = "minimalist with significant negative space, often asymmetrical"
        
        elif any(word in all_inputs for word in ["energetic", "upbeat", "bright", "positive"]):
            visual_style["color_palette"] = ["vibrant red", "yellow", "electric blue", "bright orange"]
            visual_style["imagery_themes"] = ["dynamic motion", "bright lighting", "urban environments", "crowds"]
            visual_style["typography"] = "bold sans-serif with tight spacing, often with creative distortions"
            visual_style["composition"] = "dynamic and energetic with diagonal elements and motion"
        
        elif any(word in all_inputs for word in ["chill", "relaxed", "calm", "ambient"]):
            visual_style["color_palette"] = ["soft blue", "pastel tones", "light gray", "muted green"]
            visual_style["imagery_themes"] = ["natural landscapes", "water", "clouds", "soft lighting"]
            visual_style["typography"] = "light weight sans-serif with generous spacing"
            visual_style["composition"] = "balanced and harmonious with flowing elements"
        
        elif any(word in all_inputs for word in ["intense", "aggressive", "powerful", "heavy"]):
            visual_style["color_palette"] = ["deep red", "black", "metallic silver", "dark orange"]
            visual_style["imagery_themes"] = ["industrial elements", "fire", "distressed textures", "strong contrast"]
            visual_style["typography"] = "heavy weight, often distressed or industrial"
            visual_style["composition"] = "powerful central elements with strong symmetry or intentional imbalance"
        
        else:
            # Default visual style if no specific keywords match
            visual_style["color_palette"] = ["balanced mix of dark and light tones", "accent color based on genre"]
            visual_style["imagery_themes"] = ["authentic representation of the artist", "musical elements", "environmental contexts"]
            visual_style["typography"] = "clean and readable with distinctive character"
            visual_style["composition"] = "balanced with clear focal points"
        
        return visual_style


def create_artist_profile(
    artist_name: str,
    main_genre: str,
    subgenres: List[str],
    style_tags: List[str],
    vibe_description: str,
    target_audience: str,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to create an artist profile.
    
    Args:
        artist_name: Name of the artist
        main_genre: Primary music genre
        subgenres: List of secondary genres
        style_tags: List of style descriptors
        vibe_description: Textual description of the artist's vibe/atmosphere
        target_audience: Description of the target audience
        additional_info: Optional additional information to include in the profile
        
    Returns:
        Dictionary containing the complete artist profile
    """
    builder = ArtistProfileBuilder()
    return builder.create_artist_profile(
        artist_name=artist_name,
        main_genre=main_genre,
        subgenres=subgenres,
        style_tags=style_tags,
        vibe_description=vibe_description,
        target_audience=target_audience,
        additional_info=additional_info
    )


if __name__ == "__main__":
    # Example usage
    profile = create_artist_profile(
        artist_name="Nebula Drift",
        main_genre="Electronic",
        subgenres=["Ambient", "Downtempo"],
        style_tags=["atmospheric", "ethereal", "cinematic"],
        vibe_description="Dreamy soundscapes with pulsing rhythms that evoke cosmic journeys",
        target_audience="Young adults and professionals who enjoy immersive listening experiences"
    )
    
    print(json.dumps(profile, indent=2))
