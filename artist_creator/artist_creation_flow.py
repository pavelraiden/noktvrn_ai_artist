"""
Integration script for the Artist Full Creation Flow.

This script demonstrates the full flow from artist profile creation
to prompt generation and lyrics creation.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from artist_creator import (
    create_artist_profile,
    generate_prompts_for_artist_profile,
    generate_lyrics_from_prompt
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_creation_flow")

def run_full_artist_creation_flow(
    artist_name: str,
    main_genre: str,
    subgenres: List[str],
    style_tags: List[str],
    vibe_description: str,
    target_audience: str
) -> Dict[str, Any]:
    """
    Run the full artist creation flow from profile to lyrics.
    
    Args:
        artist_name: Name of the artist
        main_genre: Primary music genre
        subgenres: List of secondary genres
        style_tags: List of style descriptors
        vibe_description: Textual description of the artist's vibe/atmosphere
        target_audience: Description of the target audience
        
    Returns:
        Dictionary containing all generated artifacts
    """
    logger.info(f"Starting full artist creation flow for: {artist_name}")
    
    # Step 1: Create the artist profile
    logger.info("Step 1: Creating artist profile")
    artist_profile = create_artist_profile(
        artist_name=artist_name,
        main_genre=main_genre,
        subgenres=subgenres,
        style_tags=style_tags,
        vibe_description=vibe_description,
        target_audience=target_audience
    )
    
    # Step 2: Generate prompts based on the artist profile
    logger.info("Step 2: Generating prompts")
    prompts = generate_prompts_for_artist_profile(artist_profile)
    
    # Step 3: Generate lyrics from the song prompt
    logger.info("Step 3: Generating lyrics")
    song_prompt = prompts["song_prompt"]
    lyrics_data = generate_lyrics_from_prompt(
        prompt_text=song_prompt,
        artist_slug=artist_profile["slug"]
    )
    
    # Compile all results
    result = {
        "artist_profile": artist_profile,
        "prompts": prompts,
        "lyrics": lyrics_data,
        "file_paths": {
            "profile": f"artists/{artist_profile['slug']}/profile.json",
            "song_prompt": f"artists/{artist_profile['slug']}/prompts/song_prompt.txt",
            "video_prompt": f"artists/{artist_profile['slug']}/prompts/video_prompt.txt",
            "social_prompt": f"artists/{artist_profile['slug']}/prompts/social_prompt.txt",
            "lyrics": f"artists/{artist_profile['slug']}/lyrics/{lyrics_data['song_slug']}.txt"
        }
    }
    
    logger.info(f"Completed full artist creation flow for: {artist_name}")
    return result

if __name__ == "__main__":
    # Example usage
    result = run_full_artist_creation_flow(
        artist_name="Nebula Drift",
        main_genre="Electronic",
        subgenres=["Ambient", "Downtempo"],
        style_tags=["atmospheric", "ethereal", "cinematic"],
        vibe_description="Dreamy soundscapes with pulsing rhythms that evoke cosmic journeys",
        target_audience="Young adults and professionals who enjoy immersive listening experiences"
    )
    
    # Print a summary of the results
    print("\n=== ARTIST CREATION FLOW SUMMARY ===\n")
    print(f"Artist: {result['artist_profile']['name']}")
    print(f"Genre: {result['artist_profile']['music']['main_genre']}")
    print(f"Song Title: {result['lyrics']['title']}")
    print("\nGenerated Files:")
    for file_type, file_path in result['file_paths'].items():
        print(f"- {file_type}: {file_path}")
