"""
Initialize the artist_manager package.

This module provides functionality for creating, validating, managing,
and evolving AI artist profiles.
"""

from .artist import Artist
from .artist_initializer import ArtistInitializer
from .artist_updater import ArtistUpdater

__all__ = ['Artist', 'ArtistInitializer', 'ArtistUpdater']
