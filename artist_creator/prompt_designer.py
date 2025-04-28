"""
Prompt Designer module for generating creative prompts based on artist profiles.

This module handles the generation of various prompt types for an artist,
including song prompts, video concept prompts, and social media content prompts.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prompt_designer")

class PromptDesigner:
    """
    Generates creative prompts for various content types based on artist profiles.
    
    This class handles the creation of prompts for songs, video concepts, and
    social media content, tailored to the artist's profile characteristics.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the PromptDesigner.
        
        Args:
            base_dir: Base directory for storing artist data. Defaults to project's artists directory.
        """
        if base_dir is None:
            # Use the default artists directory in the project
            self.base_dir = Path(__file__).resolve().parents[1] / "artists"
        else:
            self.base_dir = Path(base_dir)
        
        logger.info(f"Initialized PromptDesigner with base directory: {self.base_dir}")
    
    def generate_prompts_for_artist_profile(self, artist_profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate various prompts based on an artist profile and save them to the appropriate location.
        
        Args:
            artist_profile: The complete artist profile dictionary
            
        Returns:
            Dictionary containing the generated prompts
        """
        artist_slug = artist_profile.get("slug")
        if not artist_slug:
            raise ValueError("Artist profile must contain a 'slug' field")
        
        logger.info(f"Generating prompts for artist: {artist_profile.get('name', artist_slug)}")
        
        # Generate the different prompt types
        song_prompt = self._generate_song_prompt(artist_profile)
        video_prompt = self._generate_video_prompt(artist_profile)
        social_prompt = self._generate_social_media_prompt(artist_profile)
        
        # Ensure the prompts directory exists
        prompts_dir = self.base_dir / artist_slug / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the prompts to files
        self._save_prompt(prompts_dir / "song_prompt.txt", song_prompt)
        self._save_prompt(prompts_dir / "video_prompt.txt", video_prompt)
        self._save_prompt(prompts_dir / "social_prompt.txt", social_prompt)
        
        # Return all prompts in a dictionary
        return {
            "song_prompt": song_prompt,
            "video_prompt": video_prompt,
            "social_prompt": social_prompt
        }
    
    def _generate_song_prompt(self, artist_profile: Dict[str, Any]) -> str:
        """
        Generate a prompt for the artist's first song.
        
        Args:
            artist_profile: The complete artist profile dictionary
            
        Returns:
            A detailed prompt for song creation
        """
        # Extract relevant information from the profile
        artist_name = artist_profile.get("name", "")
        main_genre = artist_profile.get("music", {}).get("main_genre", "")
        subgenres = artist_profile.get("music", {}).get("subgenres", [])
        style_tags = artist_profile.get("music", {}).get("style_tags", [])
        vibe = artist_profile.get("music", {}).get("vibe", "")
        personality = artist_profile.get("personality", {})
        traits = personality.get("traits", [])
        
        # Construct the song prompt
        prompt = f"Create a {main_genre} song for the artist {artist_name}.\n\n"
        
        # Add genre context
        if subgenres:
            prompt += f"The song should blend {main_genre} with elements of {', '.join(subgenres)}.\n"
        
        # Add style information
        if style_tags:
            prompt += f"The musical style should be {', '.join(style_tags)}.\n"
        
        # Add vibe description
        if vibe:
            prompt += f"The overall vibe should be: {vibe}\n"
        
        # Add personality influence
        if traits:
            prompt += f"\nThe lyrics should reflect the artist's {', '.join(traits)} personality.\n"
        
        # Add backstory context if available
        if personality.get("backstory"):
            prompt += f"Consider the artist's background: {personality.get('backstory')}\n"
        
        # Add structural guidance
        prompt += "\nThe song should include:\n"
        prompt += "- A memorable hook/chorus\n"
        prompt += "- Verses that develop a cohesive narrative or theme\n"
        prompt += "- Production elements that enhance the artist's unique sound\n"
        
        # Add thematic suggestions based on genre
        prompt += "\nPossible themes could include:\n"
        
        if "electronic" in main_genre.lower():
            prompt += "- Futuristic landscapes\n- Digital transformation\n- Night city experiences\n"
        elif "rock" in main_genre.lower():
            prompt += "- Personal freedom\n- Rebellion against norms\n- Emotional intensity\n"
        elif "hip hop" in main_genre.lower() or "rap" in main_genre.lower():
            prompt += "- Urban experiences\n- Personal growth\n- Social commentary\n"
        elif "pop" in main_genre.lower():
            prompt += "- Relationships\n- Self-discovery\n- Celebration of life moments\n"
        else:
            prompt += "- Universal human experiences\n- Emotional journeys\n- Personal reflections\n"
        
        return prompt
    
    def _generate_video_prompt(self, artist_profile: Dict[str, Any]) -> str:
        """
        Generate a prompt for a video concept.
        
        Args:
            artist_profile: The complete artist profile dictionary
            
        Returns:
            A detailed prompt for video concept creation
        """
        # Extract relevant information from the profile
        artist_name = artist_profile.get("name", "")
        visual_style = artist_profile.get("visual_style", {})
        color_palette = visual_style.get("color_palette", [])
        imagery_themes = visual_style.get("imagery_themes", [])
        composition = visual_style.get("composition", "")
        
        # Construct the video prompt
        prompt = f"Create a video concept for {artist_name}'s first release.\n\n"
        
        # Add visual style guidance
        prompt += "Visual Style Guidelines:\n"
        
        if color_palette:
            prompt += f"- Color Palette: {', '.join(color_palette)}\n"
        
        if imagery_themes:
            prompt += f"- Imagery Themes: {', '.join(imagery_themes)}\n"
        
        if composition:
            prompt += f"- Composition: {composition}\n"
        
        # Add structural elements
        prompt += "\nThe video should include:\n"
        prompt += "- A compelling visual narrative that complements the music\n"
        prompt += "- Scenes that establish the artist's visual identity\n"
        prompt += "- Transitions that match the rhythm and energy of the song\n"
        
        # Add technical considerations
        prompt += "\nTechnical Considerations:\n"
        prompt += "- Aspect ratio: 16:9 for standard platforms, with potential for 9:16 vertical edits\n"
        prompt += "- Duration: 3-4 minutes for the full video, with 30-60 second teaser edits\n"
        prompt += "- Key moments should be identifiable for promotional clips\n"
        
        # Add platform-specific guidance
        prompt += "\nPlatform Optimization:\n"
        prompt += "- YouTube: Include thumbnail-worthy moments and clear artist branding\n"
        prompt += "- Instagram: Consider 60-second highlight clips with visual impact\n"
        prompt += "- TikTok: Identify 15-30 second segments with viral potential\n"
        
        return prompt
    
    def _generate_social_media_prompt(self, artist_profile: Dict[str, Any]) -> str:
        """
        Generate a prompt for social media content.
        
        Args:
            artist_profile: The complete artist profile dictionary
            
        Returns:
            A detailed prompt for social media content creation
        """
        # Extract relevant information from the profile
        artist_name = artist_profile.get("name", "")
        personality = artist_profile.get("personality", {})
        communication_style = personality.get("communication_style", "")
        public_persona = personality.get("public_persona", "")
        audience = artist_profile.get("audience", {})
        target_description = audience.get("target_description", "")
        platforms = audience.get("platforms", [])
        
        # Construct the social media prompt
        prompt = f"Create social media content strategy for {artist_name}.\n\n"
        
        # Add personality and communication guidance
        if communication_style:
            prompt += f"Communication Style: {communication_style}\n"
        
        if public_persona:
            prompt += f"Public Persona: {public_persona}\n"
        
        # Add audience information
        if target_description:
            prompt += f"\nTarget Audience: {target_description}\n"
        
        # Add platform-specific guidance
        if platforms:
            prompt += f"\nFocus on these platforms: {', '.join(platforms)}\n"
            prompt += "\nPlatform-specific content ideas:\n"
            
            for platform in platforms:
                if platform.lower() == "instagram":
                    prompt += "- Instagram: Visual artist journey, behind-the-scenes, aesthetic mood boards\n"
                elif platform.lower() == "tiktok":
                    prompt += "- TikTok: Short-form creative content, music teasers, trend participation\n"
                elif platform.lower() == "twitter":
                    prompt += "- Twitter: Artist thoughts, music industry commentary, fan engagement\n"
                elif platform.lower() == "youtube":
                    prompt += "- YouTube: Music videos, extended content, artist documentaries\n"
                elif platform.lower() == "soundcloud":
                    prompt += "- SoundCloud: Exclusive mixes, demos, collaborations\n"
        
        # Add content pillars
        prompt += "\nContent Pillars:\n"
        prompt += "1. Artist Identity: Content that establishes who the artist is and their unique perspective\n"
        prompt += "2. Music Promotion: Content directly related to releases and musical work\n"
        prompt += "3. Behind-the-Scenes: Content showing the creative process and daily life\n"
        prompt += "4. Fan Engagement: Interactive content that builds community\n"
        
        # Add posting cadence
        prompt += "\nRecommended Posting Cadence:\n"
        prompt += "- Pre-Release Phase: Increasing frequency building up to release\n"
        prompt += "- Release Phase: High frequency across all platforms\n"
        prompt += "- Sustain Phase: Regular posting to maintain presence\n"
        
        return prompt
    
    def _save_prompt(self, file_path: Path, content: str) -> None:
        """
        Save a prompt to a text file.
        
        Args:
            file_path: Path where the prompt should be saved
            content: The prompt content to save
        """
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Saved prompt to: {file_path}")


def generate_prompts_for_artist_profile(artist_profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Convenience function to generate prompts for an artist profile.
    
    Args:
        artist_profile: The complete artist profile dictionary
        
    Returns:
        Dictionary containing the generated prompts
    """
    designer = PromptDesigner()
    return designer.generate_prompts_for_artist_profile(artist_profile)


if __name__ == "__main__":
    # Example usage with a sample artist profile
    sample_profile = {
        "name": "Nebula Drift",
        "slug": "nebula-drift",
        "music": {
            "main_genre": "Electronic",
            "subgenres": ["Ambient", "Downtempo"],
            "style_tags": ["atmospheric", "ethereal", "cinematic"],
            "vibe": "Dreamy soundscapes with pulsing rhythms that evoke cosmic journeys"
        },
        "personality": {
            "traits": ["mysterious", "introspective", "visionary"],
            "communication_style": "cryptic and minimal",
            "public_persona": "enigmatic figure who rarely reveals personal details",
            "backstory": "Emerged from obscurity with a debut EP that caught attention for its unique sound design"
        },
        "visual_style": {
            "color_palette": ["deep blue", "purple", "silver", "black"],
            "imagery_themes": ["cosmic imagery", "abstract patterns", "night skies"],
            "composition": "minimalist with significant negative space"
        },
        "audience": {
            "target_description": "Young adults and professionals who enjoy immersive listening experiences",
            "platforms": ["Spotify", "SoundCloud", "YouTube", "Instagram"]
        }
    }
    
    prompts = generate_prompts_for_artist_profile(sample_profile)
    
    # Print the generated prompts
    for prompt_type, content in prompts.items():
        print(f"\n=== {prompt_type.upper()} ===\n")
        print(content)
