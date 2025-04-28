"""
Test script for the real prompt generation functions in prompt_generators.py.

This script tests the functionality of the four main prompt generation functions:
- generate_artist_profile_prompt
- generate_song_prompt
- generate_profile_cover_prompt
- generate_track_cover_prompt
"""

import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prompt_generators_test")

# Import the functions to test
try:
    from artist_flow.prompt_generators import (
        generate_artist_profile_prompt,
        generate_song_prompt,
        generate_profile_cover_prompt,
        generate_track_cover_prompt,
    )

    logger.info("Successfully imported all prompt generation functions")
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    sys.exit(1)


def test_generate_artist_profile_prompt():
    """Test the generate_artist_profile_prompt function with various inputs."""
    logger.info("Testing generate_artist_profile_prompt function")

    # Test case 1: Complete artist brief
    complete_brief = {
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "atmosphere": "Nocturnal, Urban",
        "vibe": "Introspective, Intense",
    }

    # Test case 2: Minimal artist brief
    minimal_brief = {"genre": "Phonk"}

    # Test case 3: Alternative genre
    alt_genre_brief = {
        "genre": "Lofi",
        "style": "Nostalgic, Warm",
        "atmosphere": "Relaxed",
        "vibe": "Chill",
    }

    # Run tests
    test_cases = [
        ("Complete brief", complete_brief),
        ("Minimal brief", minimal_brief),
        ("Alternative genre", alt_genre_brief),
    ]

    for test_name, brief in test_cases:
        logger.info(f"Running test: {test_name}")
        try:
            prompt = generate_artist_profile_prompt(brief)

            # Verify prompt is a non-empty string
            assert isinstance(prompt, str), "Prompt should be a string"
            assert len(prompt) > 100, "Prompt should be substantial in length"

            # Verify genre is included in the prompt
            assert (
                brief.get("genre", "").lower() in prompt.lower()
            ), "Genre should be included in prompt"

            logger.info(f"Test passed: {test_name}")
            logger.info(f"Prompt length: {len(prompt)} characters")

            # Print a snippet of the prompt
            print(f"\n--- {test_name} Prompt Snippet ---")
            print(prompt[:200] + "...\n")

        except Exception as e:
            logger.error(f"Test failed: {test_name} - {str(e)}")
            return False

    return True


def test_generate_song_prompt():
    """Test the generate_song_prompt function with various inputs."""
    logger.info("Testing generate_song_prompt function")

    # Test case 1: Complete artist profile
    complete_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "themes": ["isolation", "night life", "inner demons"],
        "sound": ["distorted bass", "atmospheric pads", "haunting melodies"],
    }

    # Test case 2: Minimal artist profile
    minimal_profile = {"name": "LofiDreamer", "genre": "Lofi"}

    # Test case 3: Nested structure profile
    nested_profile = {
        "name": "PhonkRider",
        "genre": "Phonk",
        "style": "Retro, Aggressive",
        "musical_identity": {
            "signature_sound": "Memphis drums, pitched vocals, heavy bass"
        },
        "thematic_elements": {
            "lyrical_themes": ["night driving", "nostalgia", "urban legends"]
        },
    }

    # Run tests
    test_cases = [
        ("Complete profile", complete_profile),
        ("Minimal profile", minimal_profile),
        ("Nested structure profile", nested_profile),
    ]

    for test_name, profile in test_cases:
        logger.info(f"Running test: {test_name}")
        try:
            prompt = generate_song_prompt(profile)

            # Verify prompt is a non-empty string
            assert isinstance(prompt, str), "Prompt should be a string"
            assert len(prompt) > 100, "Prompt should be substantial in length"

            # Verify artist name and genre are included in the prompt
            assert (
                profile.get("name", "").lower() in prompt.lower()
            ), "Artist name should be included in prompt"
            assert (
                profile.get("genre", "").lower() in prompt.lower()
            ), "Genre should be included in prompt"

            logger.info(f"Test passed: {test_name}")
            logger.info(f"Prompt length: {len(prompt)} characters")

            # Print a snippet of the prompt
            print(f"\n--- {test_name} Prompt Snippet ---")
            print(prompt[:200] + "...\n")

        except Exception as e:
            logger.error(f"Test failed: {test_name} - {str(e)}")
            return False

    return True


def test_generate_profile_cover_prompt():
    """Test the generate_profile_cover_prompt function with various inputs."""
    logger.info("Testing generate_profile_cover_prompt function")

    # Test case 1: Complete artist profile with visual identity
    complete_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "visual_identity": {
            "aesthetic": "Nocturnal, Urban",
            "color_palette": ["midnight blue", "silver", "deep purple", "black"],
            "visual_motifs": ["shadows", "city skylines", "masks", "reflections"],
        },
    }

    # Test case 2: Minimal artist profile
    minimal_profile = {"name": "LofiDreamer", "genre": "Lofi"}

    # Test case 3: String visual identity
    string_visual_profile = {
        "name": "PhonkRider",
        "genre": "Phonk",
        "style": "Retro, Aggressive",
        "visual_identity": "Vintage, VHS aesthetic",
    }

    # Run tests
    test_cases = [
        ("Complete profile with visual identity", complete_profile),
        ("Minimal profile", minimal_profile),
        ("String visual identity", string_visual_profile),
    ]

    for test_name, profile in test_cases:
        logger.info(f"Running test: {test_name}")
        try:
            prompt = generate_profile_cover_prompt(profile)

            # Verify prompt is a non-empty string
            assert isinstance(prompt, str), "Prompt should be a string"
            assert len(prompt) > 100, "Prompt should be substantial in length"

            # Verify artist name and genre are included in the prompt
            assert (
                profile.get("name", "").lower() in prompt.lower()
            ), "Artist name should be included in prompt"
            assert (
                profile.get("genre", "").lower() in prompt.lower()
            ), "Genre should be included in prompt"

            # Verify it mentions not showing a real human face
            assert (
                "not show a realistic human face" in prompt.lower()
                or "do not show a realistic human face" in prompt.lower()
            ), "Prompt should specify not to show a real human face"

            logger.info(f"Test passed: {test_name}")
            logger.info(f"Prompt length: {len(prompt)} characters")

            # Print a snippet of the prompt
            print(f"\n--- {test_name} Prompt Snippet ---")
            print(prompt[:200] + "...\n")

        except Exception as e:
            logger.error(f"Test failed: {test_name} - {str(e)}")
            return False

    return True


def test_generate_track_cover_prompt():
    """Test the generate_track_cover_prompt function with various inputs."""
    logger.info("Testing generate_track_cover_prompt function")

    # Test case 1: Complete artist profile with song theme
    complete_test = {
        "profile": {
            "name": "NightShade",
            "genre": "Dark Trap",
            "style": "Mysterious, Cold",
            "visual_identity": {
                "aesthetic": "Nocturnal, Urban",
                "color_palette": ["midnight blue", "silver", "deep purple", "black"],
            },
        },
        "song_theme": "Midnight Shadows",
    }

    # Test case 2: Minimal profile with emotional song theme
    minimal_test = {
        "profile": {"name": "LofiDreamer", "genre": "Lofi"},
        "song_theme": "Melancholic Memories",
    }

    # Test case 3: String visual identity with energetic theme
    string_visual_test = {
        "profile": {
            "name": "PhonkRider",
            "genre": "Phonk",
            "style": "Retro, Aggressive",
            "visual_identity": "Vintage, VHS aesthetic",
        },
        "song_theme": "Energetic Night Drive",
    }

    # Run tests
    test_cases = [
        ("Complete profile with song theme", complete_test),
        ("Minimal profile with emotional theme", minimal_test),
        ("String visual identity with energetic theme", string_visual_test),
    ]

    for test_name, test_data in test_cases:
        logger.info(f"Running test: {test_name}")
        try:
            prompt = generate_track_cover_prompt(
                test_data["profile"], test_data["song_theme"]
            )

            # Verify prompt is a non-empty string
            assert isinstance(prompt, str), "Prompt should be a string"
            assert len(prompt) > 100, "Prompt should be substantial in length"

            # Verify artist name, genre, and song theme are included in the prompt
            assert (
                test_data["profile"].get("name", "").lower() in prompt.lower()
            ), "Artist name should be included in prompt"
            assert (
                test_data["profile"].get("genre", "").lower() in prompt.lower()
            ), "Genre should be included in prompt"
            assert (
                test_data["song_theme"].lower() in prompt.lower()
            ), "Song theme should be included in prompt"

            logger.info(f"Test passed: {test_name}")
            logger.info(f"Prompt length: {len(prompt)} characters")

            # Print a snippet of the prompt
            print(f"\n--- {test_name} Prompt Snippet ---")
            print(prompt[:200] + "...\n")

        except Exception as e:
            logger.error(f"Test failed: {test_name} - {str(e)}")
            return False

    return True


def run_all_tests():
    """Run all tests and report results."""
    logger.info("Starting tests for prompt generation functions")

    # Run all tests
    artist_profile_test = test_generate_artist_profile_prompt()
    song_test = test_generate_song_prompt()
    profile_cover_test = test_generate_profile_cover_prompt()
    track_cover_test = test_generate_track_cover_prompt()

    # Report results
    logger.info("Test results:")
    logger.info(
        f"- generate_artist_profile_prompt: {'PASSED' if artist_profile_test else 'FAILED'}"
    )
    logger.info(f"- generate_song_prompt: {'PASSED' if song_test else 'FAILED'}")
    logger.info(
        f"- generate_profile_cover_prompt: {'PASSED' if profile_cover_test else 'FAILED'}"
    )
    logger.info(
        f"- generate_track_cover_prompt: {'PASSED' if track_cover_test else 'FAILED'}"
    )

    all_passed = (
        artist_profile_test and song_test and profile_cover_test and track_cover_test
    )
    logger.info(f"Overall result: {'PASSED' if all_passed else 'FAILED'}")

    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
