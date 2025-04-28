"""
Lyrics Generator module for creating song lyrics based on prompts.

This module handles the generation of lyrics from prompt text,
integrating with LLMs and saving the output to the appropriate location.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("lyrics_generator")

class LyricsGenerator:
    """
    Generates song lyrics based on prompt text.
    
    This class handles the creation of lyrics using LLM integration
    and ensures they are stored in the appropriate directory structure.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the LyricsGenerator.
        
        Args:
            base_dir: Base directory for storing artist data. Defaults to project's artists directory.
        """
        if base_dir is None:
            # Use the default artists directory in the project
            self.base_dir = Path(__file__).resolve().parents[1] / "artists"
        else:
            self.base_dir = Path(base_dir)
        
        logger.info(f"Initialized LyricsGenerator with base directory: {self.base_dir}")
    
    def generate_lyrics_from_prompt(self, prompt_text: str, artist_slug: str = None, song_slug: str = None) -> Dict[str, Any]:
        """
        Generate lyrics based on a prompt and save them to the appropriate location.
        
        Args:
            prompt_text: The prompt text to generate lyrics from
            artist_slug: The artist's slug/identifier (if None, will be extracted from prompt)
            song_slug: The song's slug/identifier (if None, will be generated)
            
        Returns:
            Dictionary containing the generated lyrics and metadata
        """
        # Extract artist name from prompt if not provided
        if artist_slug is None:
            artist_slug = self._extract_artist_slug_from_prompt(prompt_text)
            if not artist_slug:
                raise ValueError("Could not extract artist slug from prompt and none was provided")
        
        # Generate song title and slug if not provided
        song_title = self._generate_song_title_from_prompt(prompt_text)
        if song_slug is None:
            song_slug = self._generate_song_slug(song_title)
        
        logger.info(f"Generating lyrics for artist: {artist_slug}, song: {song_slug}")
        
        # Generate the lyrics using LLM integration (stub for now)
        lyrics_content = self._generate_lyrics_with_llm(prompt_text)
        
        # Create the lyrics structure
        lyrics_data = {
            "title": song_title,
            "artist_slug": artist_slug,
            "song_slug": song_slug,
            "prompt_used": prompt_text,
            "lyrics": lyrics_content
        }
        
        # Ensure the lyrics directory exists
        lyrics_dir = self.base_dir / artist_slug / "lyrics"
        lyrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the lyrics to a text file
        lyrics_path = lyrics_dir / f"{song_slug}.txt"
        with open(lyrics_path, 'w') as f:
            f.write(f"# {song_title}\n\n")
            f.write(lyrics_content)
        
        logger.info(f"Lyrics saved to: {lyrics_path}")
        
        return lyrics_data
    
    def _extract_artist_slug_from_prompt(self, prompt_text: str) -> Optional[str]:
        """
        Extract the artist slug from the prompt text.
        
        Args:
            prompt_text: The prompt text to extract from
            
        Returns:
            The extracted artist slug or None if not found
        """
        # Look for artist name in the prompt
        artist_match = re.search(r"for the artist ([A-Za-z0-9 ]+)", prompt_text)
        if artist_match:
            artist_name = artist_match.group(1).strip()
            # Convert to slug format
            return artist_name.lower().replace(' ', '-')
        return None
    
    def _generate_song_title_from_prompt(self, prompt_text: str) -> str:
        """
        Generate a song title based on the prompt text.
        
        Args:
            prompt_text: The prompt text to generate from
            
        Returns:
            A generated song title
        """
        # In a real implementation, this would use more sophisticated NLP
        # or integrate with an LLM to generate a relevant title
        
        # Extract key themes from the prompt
        themes = []
        if "futuristic" in prompt_text.lower():
            themes.append("Future")
        if "night" in prompt_text.lower():
            themes.append("Night")
        if "digital" in prompt_text.lower():
            themes.append("Digital")
        if "urban" in prompt_text.lower():
            themes.append("Urban")
        if "emotion" in prompt_text.lower() or "emotional" in prompt_text.lower():
            themes.append("Emotion")
        if "freedom" in prompt_text.lower():
            themes.append("Freedom")
        if "journey" in prompt_text.lower():
            themes.append("Journey")
        
        # If no themes were extracted, use some generic options
        if not themes:
            themes = ["Horizon", "Reflection", "Moment", "Pulse", "Echo"]
        
        # Generate a simple title by combining themes or using a single theme
        import random
        if len(themes) > 1 and random.random() > 0.5:
            return f"{themes[0]} {themes[1]}"
        else:
            return themes[0]
    
    def _generate_song_slug(self, song_title: str) -> str:
        """
        Generate a URL-friendly slug from the song title.
        
        Args:
            song_title: The song title
            
        Returns:
            A lowercase, hyphenated slug
        """
        # Convert to lowercase, replace spaces with hyphens, remove special characters
        slug = song_title.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        return slug
    
    def _generate_lyrics_with_llm(self, prompt_text: str) -> str:
        """
        Generate lyrics using LLM integration.
        
        Args:
            prompt_text: The prompt text to generate from
            
        Returns:
            The generated lyrics
        """
        # This is a stub implementation - in a real system, this would
        # integrate with an actual LLM API like OpenAI's GPT
        
        logger.info("Using stub LLM integration to generate lyrics")
        
        # Extract genre information from the prompt
        genre = "unknown"
        if "electronic" in prompt_text.lower():
            genre = "electronic"
        elif "rock" in prompt_text.lower():
            genre = "rock"
        elif "hip hop" in prompt_text.lower() or "rap" in prompt_text.lower():
            genre = "hip hop"
        elif "pop" in prompt_text.lower():
            genre = "pop"
        
        # Generate stub lyrics based on genre
        if genre == "electronic":
            return """Verse 1:
Digital waves wash over me
In the glow of neon dreams
Synthetic pulse, electric heart
Where the future and I start

Chorus:
Beyond the horizon of light
We dance in the digital night
Signals calling through the void
A new reality deployed

Verse 2:
Binary code becomes a song
Frequencies where we belong
In this space between the real
And the worlds that we can feel

(Chorus repeats)

Bridge:
Breaking down the barriers
Of time and space and sound
In this moment, infinite
Where lost becomes found

(Chorus repeats)

Outro:
Digital waves wash over me..."""
        
        elif genre == "rock":
            return """Verse 1:
Standing at the edge of everything
With my back against the wall
These chains that once defined me
Are beginning to fall

Chorus:
Freedom calls my name
Like thunder in my veins
No more living in the shadows
No more carrying these chains

Verse 2:
Every step against the current
Every voice that tried to drown
Couldn't keep my spirit under
Couldn't keep my fire down

(Chorus repeats)

Bridge:
They said I'd never make it
They said I'd fade away
But here I stand before you
In the light of a brand new day

(Chorus repeats)

Outro:
Freedom calls my name..."""
        
        elif genre == "hip hop":
            return """Verse 1:
Streets talking, I'm just translating the code
Carrying weight that could bend a steel road
Every bar is a chapter, every line is true
Building my legacy, what else can I do?

Chorus:
Rise up from the concrete
Vision clear, mind complete
From nothing to something
The journey's bittersweet

Verse 2:
They wonder how I made it, how I broke the ceiling
When pressure makes diamonds, that's just the beginning
Each obstacle faced is a lesson learned
Success is the fire from the bridges I burned

(Chorus repeats)

Bridge:
They never saw me coming
Underestimated, overlooked
Now my name's in the conversation
My chapter can't be unbooked

(Chorus repeats)

Outro:
From nothing to something..."""
        
        else:
            return """Verse 1:
Words unspoken between us
Hanging in the midnight air
Moments frozen in time
Memories beyond compare

Chorus:
This is our moment
This is our time
Everything changes
When your heart meets mine

Verse 2:
Searching through the darkness
For a light to guide the way
Found it in your presence
Where night turns into day

(Chorus repeats)

Bridge:
Through all the noise
Through all the doubt
You're the melody
I can't live without

(Chorus repeats)

Outro:
This is our moment
This is our time..."""


def generate_lyrics_from_prompt(prompt_text: str, artist_slug: str = None, song_slug: str = None) -> Dict[str, Any]:
    """
    Convenience function to generate lyrics from a prompt.
    
    Args:
        prompt_text: The prompt text to generate lyrics from
        artist_slug: The artist's slug/identifier (if None, will be extracted from prompt)
        song_slug: The song's slug/identifier (if None, will be generated)
        
    Returns:
        Dictionary containing the generated lyrics and metadata
    """
    generator = LyricsGenerator()
    return generator.generate_lyrics_from_prompt(
        prompt_text=prompt_text,
        artist_slug=artist_slug,
        song_slug=song_slug
    )


if __name__ == "__main__":
    # Example usage
    sample_prompt = """Create an electronic song for the artist Nebula Drift.

The song should blend Electronic with elements of Ambient, Downtempo.
The musical style should be atmospheric, ethereal, cinematic.
The overall vibe should be: Dreamy soundscapes with pulsing rhythms that evoke cosmic journeys

The lyrics should reflect the artist's mysterious, introspective, visionary personality.
Consider the artist's background: Emerged from obscurity with a debut EP that caught attention for its unique sound design

The song should include:
- A memorable hook/chorus
- Verses that develop a cohesive narrative or theme
- Production elements that enhance the artist's unique sound

Possible themes could include:
- Futuristic landscapes
- Digital transformation
- Night city experiences"""
    
    lyrics_data = generate_lyrics_from_prompt(sample_prompt)
    
    print(f"Generated song: {lyrics_data['title']}")
    print("\nLYRICS:\n")
    print(lyrics_data['lyrics'])
