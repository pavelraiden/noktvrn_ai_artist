"""
Artist Passport Generator Module

This module provides a unified system for consolidating all prompts and generated mock assets
into a single structured "Artist Passport" object. It serves as the central integration point
for the artist creation flow, bringing together artist profiles, tracks, visual assets, and
video plans into a comprehensive package.

The Artist Passport contains:
- Artist Profile (name, style, mood, persona, genres, visual identity)
- Initial Song (track prompt, mock track metadata)
- Initial Visual Assets (profile cover prompt, track cover prompt, mock image metadata)
- Initial Video Plan (video prompt linked to the initial song)
"""

from typing import Dict, List, Optional, Any, Union
import logging
import random
import os
import json
from datetime import datetime
import uuid

# Import generator modules
from artist_flow.generators.artist_prompt_generator import generate_artist_prompt
from artist_flow.generators.track_prompt_generator import generate_track_prompt
from artist_flow.generators.video_prompt_generator import generate_video_prompt

# Import mock generators
from artist_flow.mocks.music_generator import generate_mock_track
from artist_flow.mocks.image_generator import generate_mock_image

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_passport_generator")


class ArtistPassportGenerator:
    """
    Generates a comprehensive Artist Passport that consolidates all aspects of an AI artist.

    This class integrates various generator modules to create a unified passport containing
    the artist profile, initial song, visual assets, and video plan.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the artist passport generator.

        Args:
            seed: Optional random seed for reproducible generation
        """
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)

        logger.info("Initialized ArtistPassportGenerator")

    def generate_artist_passport(self, artist_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive Artist Passport based on the provided brief.

        Args:
            artist_brief: Dictionary containing user-provided artist parameters

        Returns:
            Dictionary containing the complete Artist Passport
        """
        logger.info("Generating Artist Passport")

        # Generate a unique session ID for this passport
        session_id = str(uuid.uuid4())

        # Step 1: Generate artist profile
        artist_profile = self._generate_artist_profile(artist_brief)

        # Step 2: Generate initial track
        initial_track = self._generate_initial_track(artist_profile)

        # Step 3: Generate visual assets
        visual_assets = self._generate_visual_assets(artist_profile, initial_track)

        # Step 4: Generate video plan
        video_plan = self._generate_video_plan(artist_profile, initial_track)

        # Assemble the complete passport
        passport = {
            "passport_id": session_id,
            "created_at": datetime.now().isoformat(),
            "artist_profile": artist_profile,
            "initial_track": initial_track,
            "visual_assets": visual_assets,
            "video_plan": video_plan,
            "metadata": {
                "version": "1.0",
                "source": "artist_passport_generator",
                "is_mock": True,  # Will be set to False when real APIs are integrated
            },
        }

        logger.info(
            f"Generated Artist Passport for {artist_profile['profile']['name']}"
        )
        return passport

    def _generate_artist_profile(self, artist_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the artist profile section of the passport.

        Args:
            artist_brief: Dictionary containing user-provided artist parameters

        Returns:
            Dictionary containing the artist profile
        """
        logger.info("Generating artist profile")

        # Generate artist prompt
        artist_prompt_result = generate_artist_prompt(artist_brief)

        # Extract key elements from the artist prompt result
        prompt = artist_prompt_result["prompt"]
        metadata = artist_prompt_result["metadata"]

        # Create a structured artist profile
        artist_profile = {
            "profile": {
                "name": metadata.get("artist_name", "Unknown Artist"),
                "genre": metadata.get("genre", artist_brief.get("genre", "Electronic")),
                "style": metadata.get("style", artist_brief.get("style", "Unique")),
                "persona": metadata.get("persona", artist_brief.get("persona", "")),
                "target_audience": metadata.get(
                    "target_audience", artist_brief.get("target_audience", "")
                ),
                "visual_identity": metadata.get(
                    "visual_identity", artist_brief.get("visual_identity", "")
                ),
                "lyrics_language": metadata.get(
                    "lyrics_language", artist_brief.get("lyrics_language", "English")
                ),
                "themes": metadata.get("themes", artist_brief.get("themes", "")),
                "lifestyle": metadata.get(
                    "lifestyle", artist_brief.get("lifestyle", "")
                ),
            },
            "prompt": prompt,
            "metadata": metadata,
        }

        return artist_profile

    def _generate_initial_track(self, artist_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the initial track section of the passport.

        Args:
            artist_profile: Dictionary containing the artist profile

        Returns:
            Dictionary containing the initial track
        """
        logger.info("Generating initial track")

        # Extract profile for track generation
        profile = artist_profile["profile"]

        # Generate track prompt
        track_prompt_result = generate_track_prompt(profile)

        # Extract key elements from the track prompt result
        prompt = track_prompt_result["prompt"]
        metadata = track_prompt_result["metadata"]

        # Generate mock track using the prompt
        mock_track = generate_mock_track(prompt)

        # Create a structured initial track
        initial_track = {
            "title": f"First Track by {profile['name']}",
            "prompt": prompt,
            "metadata": metadata,
            "mock_track": mock_track,
        }

        return initial_track

    def _generate_visual_assets(
        self, artist_profile: Dict[str, Any], initial_track: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate the visual assets section of the passport.

        Args:
            artist_profile: Dictionary containing the artist profile
            initial_track: Dictionary containing the initial track

        Returns:
            Dictionary containing the visual assets
        """
        logger.info("Generating visual assets")

        # Extract profile for visual asset generation
        profile = artist_profile["profile"]

        # Create profile cover prompt
        profile_cover_prompt = f"Create a profile image for {profile['name']}, a {profile['genre']} artist with a {profile['style']} style. {profile['visual_identity']}"

        # Create track cover prompt
        track_cover_prompt = f"Create a track cover image for '{initial_track['title']}' by {profile['name']}, a {profile['genre']} track with {profile['style']} style. Should match the mood of the track."

        # Generate mock images using the prompts
        profile_cover_mock = generate_mock_image(profile_cover_prompt)
        track_cover_mock = generate_mock_image(track_cover_prompt)

        # Create a structured visual assets section
        visual_assets = {
            "profile_cover": {
                "prompt": profile_cover_prompt,
                "mock_image": profile_cover_mock,
            },
            "track_cover": {
                "prompt": track_cover_prompt,
                "mock_image": track_cover_mock,
            },
        }

        return visual_assets

    def _generate_video_plan(
        self, artist_profile: Dict[str, Any], initial_track: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate the video plan section of the passport.

        Args:
            artist_profile: Dictionary containing the artist profile
            initial_track: Dictionary containing the initial track

        Returns:
            Dictionary containing the video plan
        """
        logger.info("Generating video plan")

        # Extract profile for video plan generation
        profile = artist_profile["profile"]

        # Create track info for video prompt generation
        track_info = {
            "title": initial_track["title"],
            "mood": initial_track["metadata"].get("mood", profile["style"]),
            "tempo": initial_track["metadata"].get("tempo", "medium"),
            "audience_emotion": initial_track["metadata"].get("audience_emotion", ""),
        }

        # Generate video prompt
        video_prompt_result = generate_video_prompt(profile, track_info, "tiktok")

        # Extract key elements from the video prompt result
        prompt = video_prompt_result["prompt"]
        metadata = video_prompt_result["metadata"]

        # Create a structured video plan
        video_plan = {
            "prompt": prompt,
            "metadata": metadata,
            "platform": "tiktok",
            "track_reference": initial_track["title"],
        }

        return video_plan


# Factory function to create an artist passport generator
def create_artist_passport_generator(
    seed: Optional[int] = None,
) -> ArtistPassportGenerator:
    """
    Factory function to create an artist passport generator.

    Args:
        seed: Optional random seed for reproducible generation

    Returns:
        An artist passport generator instance
    """
    return ArtistPassportGenerator(seed=seed)


# Convenience function for generating artist passports
def generate_artist_passport(artist_brief: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive Artist Passport based on the provided brief.

    This is a convenience function that creates a generator instance and calls
    generate_artist_passport on it.

    Args:
        artist_brief: Dictionary containing user-provided artist parameters

    Returns:
        Dictionary containing the complete Artist Passport
    """
    generator = create_artist_passport_generator()
    return generator.generate_artist_passport(artist_brief)


# Example usage
if __name__ == "__main__":
    # Example artist brief
    example_brief = {
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "persona": "mysterious, energetic",
        "target_audience": "Young adults, night owls",
        "visual_identity": "Always wears a black hood and mask",
        "lyrics_language": "English",
        "themes": "Urban isolation, night life, inner struggles",
        "lifestyle": "Urban night life, digital nomad",
    }

    # Generate an artist passport
    passport = generate_artist_passport(example_brief)

    # Print the result
    print("ARTIST PASSPORT:")
    print(f"Artist: {passport['artist_profile']['profile']['name']}")
    print(f"Genre: {passport['artist_profile']['profile']['genre']}")
    print(f"Initial Track: {passport['initial_track']['title']}")
    print(f"Track URL: {passport['initial_track']['mock_track']['track_url']}")
    print(
        f"Profile Image: {passport['visual_assets']['profile_cover']['mock_image']['image_url']}"
    )
    print(
        f"Track Cover: {passport['visual_assets']['track_cover']['mock_image']['image_url']}"
    )
    print(f"Video Platform: {passport['video_plan']['platform']}")
