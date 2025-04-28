"""
Initialization file for the artist_creator package.

This file makes the package importable and defines the public interface.
"""

from .artist_profile_builder import create_artist_profile
from .prompt_designer import generate_prompts_for_artist_profile
from .lyrics_generator import generate_lyrics_from_prompt

__all__ = [
    'create_artist_profile',
    'generate_prompts_for_artist_profile',
    'generate_lyrics_from_prompt',
]
