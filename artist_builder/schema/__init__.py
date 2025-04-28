"""
Artist Profile Schema Module

This module provides schema definitions, validation, and conversion utilities
for artist profiles in the AI Artist Creation and Management System.
"""

from .artist_profile_schema import (
    ArtistProfile,
    ArtistProfileSettings,
    validate_artist_profile,
)
from .schema_converter import legacy_to_new_schema, new_to_legacy_schema
from .schema_defaults import create_default_settings

__all__ = [
    "ArtistProfile",
    "ArtistProfileSettings",
    "validate_artist_profile",
    "legacy_to_new_schema",
    "new_to_legacy_schema",
    "create_default_settings",
]
