"""
Artist Profile Schema Test Module

This module provides test cases for validating the artist profile schema
implementation and ensuring that profiles conform to the required schema.
"""

import unittest
import json
from datetime import datetime, date
from typing import Dict, Any, List

from artist_builder.schema.artist_profile_schema import (
    ArtistProfile, 
    ArtistProfileSettings,
    validate_artist_profile
)
from artist_builder.schema.schema_converter import (
    legacy_to_new_schema,
    new_to_legacy_schema
)
from artist_builder.schema.schema_defaults import (
    create_default_settings,
    create_default_artist_profile
)
from artist_builder.composer.artist_profile_composer import ArtistProfileComposer


class TestArtistProfileSchema(unittest.TestCase):
    """Test cases for the artist profile schema."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a valid test profile
        self.valid_profile = {
            "artist_id": "artist_20250427123456_7890",
            "stage_name": "Phantom Shadow",
            "real_name": None,
            "genre": "Trap",
            "subgenres": ["Hip Hop", "Dark Trap"],
            "style_description": "A Trap artist with a Mysterious, Intense vibe.",
            "voice_type": "Deep, raspy voice that delivers lyrics about city life.",
            "personality_traits": ["Mysterious", "Intense", "Authentic"],
            "target_audience": "Young urban listeners who appreciate dark atmospheric beats",
            "visual_identity_prompt": "Professional portrait photograph of a music artist wearing a black hood and mask.",
            "song_prompt_generator": "Create a Trap track with a Mysterious, Intense vibe.",
            "video_prompt_generator": "Create a music video teaser for a Trap track with a Mysterious atmosphere.",
            "creation_date": date.today(),
            "update_history": [
                {
                    "update_date": date.today(),
                    "updated_fields": ["initial_creation"]
                }
            ],
            "notes": "A mysterious dark trap artist who thrives in the urban night scene.",
            "settings": create_default_settings(),
            "source_prompt": "A mysterious dark trap artist who thrives in the urban night scene.",
            "session_id": "test_session_123",
            "metadata": {}
        }
        
        # Create a legacy test profile
        self.legacy_profile = {
            "id": "artist_20250427123456_7890",
            "name": "Phantom Shadow",
            "genre": "Trap",
            "vibe": "Mysterious, Intense",
            "backstory": "A mysterious dark trap artist who thrives in the urban night scene.",
            "style": "Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound.",
            "visual": "Always seen wearing a black hood and mask, their identity remains hidden, adding to their enigmatic presence.",
            "voice": "Their deep, raspy voice delivers lyrics about city life and personal struggles.",
            "created_at": datetime.now().isoformat(),
            "source_prompt": "A mysterious dark trap artist who thrives in the urban night scene.",
            "session_id": "test_session_123",
            "metadata": {},
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "summary": "Phantom Shadow is a Trap artist with a Mysterious, Intense vibe.",
            "tags": ["trap", "mysterious", "intense", "phantomshadow", "808", "beats", "dark", "bass"]
        }
        
        # Create an example prompt
        self.example_prompt = """
        A mysterious dark trap artist who thrives in the urban night scene. 
        Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound.
        Always seen wearing a black hood and mask, their identity remains hidden, adding to their enigmatic presence.
        Their deep, raspy voice delivers lyrics about city life and personal struggles, resonating with listeners
        who connect with the authentic emotion in their music.
        """
        
        # Initialize the composer
        self.composer = ArtistProfileComposer()
    
    def test_valid_profile_validation(self):
        """Test that a valid profile passes validation."""
        is_valid, errors = validate_artist_profile(self.valid_profile)
        self.assertTrue(is_valid, f"Valid profile failed validation: {errors}")
        self.assertEqual(len(errors), 0, "Valid profile should have no validation errors")
    
    def test_invalid_profile_validation(self):
        """Test that an invalid profile fails validation with appropriate errors."""
        # Create an invalid profile by removing required fields
        invalid_profile = self.valid_profile.copy()
        del invalid_profile["stage_name"]
        del invalid_profile["genre"]
        invalid_profile["subgenres"] = []  # Empty array
        
        is_valid, errors = validate_artist_profile(invalid_profile)
        self.assertFalse(is_valid, "Invalid profile should fail validation")
        self.assertGreater(len(errors), 0, "Invalid profile should have validation errors")
        
        # Check for specific error messages
        error_text = "\n".join(errors)
        self.assertIn("stage_name", error_text, "Should report missing stage_name")
        self.assertIn("genre", error_text, "Should report missing genre")
        self.assertIn("subgenres", error_text, "Should report empty subgenres array")
    
    def test_pydantic_model_validation(self):
        """Test that the Pydantic model correctly validates profiles."""
        # Test valid profile
        try:
            profile_model = ArtistProfile(**self.valid_profile)
            self.assertEqual(profile_model.stage_name, "Phantom Shadow")
            self.assertEqual(profile_model.genre, "Trap")
            self.assertEqual(len(profile_model.subgenres), 2)
        except Exception as e:
            self.fail(f"Valid profile failed Pydantic validation: {e}")
        
        # Test invalid profile
        invalid_profile = self.valid_profile.copy()
        del invalid_profile["stage_name"]
        
        with self.assertRaises(Exception):
            ArtistProfile(**invalid_profile)
    
    def test_settings_validation(self):
        """Test validation of the settings object."""
        # Test valid settings
        valid_settings = create_default_settings()
        try:
            settings_model = ArtistProfileSettings(**valid_settings)
            self.assertEqual(settings_model.trend_alignment_behavior, "soft")
            self.assertEqual(settings_model.release_strategy.video_release_ratio, 0.7)
        except Exception as e:
            self.fail(f"Valid settings failed Pydantic validation: {e}")
        
        # Test invalid settings
        invalid_settings = valid_settings.copy()
        invalid_settings["trend_alignment_behavior"] = "invalid_value"
        invalid_settings["release_strategy"]["video_release_ratio"] = 2.0  # Out of range
        
        with self.assertRaises(Exception):
            ArtistProfileSettings(**invalid_settings)
    
    def test_legacy_to_new_schema_conversion(self):
        """Test conversion from legacy to new schema."""
        new_profile = legacy_to_new_schema(self.legacy_profile)
        
        # Validate the converted profile
        is_valid, errors = validate_artist_profile(new_profile)
        self.assertTrue(is_valid, f"Converted profile failed validation: {errors}")
        
        # Check that key fields were properly converted
        self.assertEqual(new_profile["artist_id"], self.legacy_profile["id"])
        self.assertEqual(new_profile["stage_name"], self.legacy_profile["name"])
        self.assertEqual(new_profile["genre"], self.legacy_profile["genre"])
        self.assertIn("settings", new_profile)
        self.assertIn("personality_traits", new_profile)
        self.assertIn("subgenres", new_profile)
    
    def test_new_to_legacy_schema_conversion(self):
        """Test conversion from new schema to legacy format."""
        legacy_profile = new_to_legacy_schema(self.valid_profile)
        
        # Check that key fields were properly converted
        self.assertEqual(legacy_profile["id"], self.valid_profile["artist_id"])
        self.assertEqual(legacy_profile["name"], self.valid_profile["stage_name"])
        self.assertEqual(legacy_profile["genre"], self.valid_profile["genre"])
        self.assertIn("vibe", legacy_profile)
        self.assertIn("backstory", legacy_profile)
        self.assertIn("style", legacy_profile)
    
    def test_composer_profile_generation(self):
        """Test that the composer generates schema-compliant profiles."""
        # Generate a profile using the composer
        profile = self.composer.compose_profile(self.example_prompt, session_id="test_session_123")
        
        # Validate the generated profile
        is_valid, errors = validate_artist_profile(profile)
        self.assertTrue(is_valid, f"Generated profile failed validation: {errors}")
        
        # Check that all required fields are present
        required_fields = [
            "artist_id", "stage_name", "genre", "subgenres", "style_description",
            "voice_type", "personality_traits", "target_audience", "visual_identity_prompt",
            "song_prompt_generator", "video_prompt_generator", "creation_date", "settings"
        ]
        
        for field in required_fields:
            self.assertIn(field, profile, f"Generated profile missing required field: {field}")
    
    def test_default_artist_profile(self):
        """Test creation of a default artist profile."""
        profile = create_default_artist_profile("Test Artist", "Electronic")
        
        # Validate the default profile
        is_valid, errors = validate_artist_profile(profile)
        self.assertTrue(is_valid, f"Default profile failed validation: {errors}")
        
        # Check specific fields
        self.assertEqual(profile["stage_name"], "Test Artist")
        self.assertEqual(profile["genre"], "Electronic")
        self.assertGreaterEqual(len(profile["subgenres"]), 1)
        self.assertGreaterEqual(len(profile["personality_traits"]), 1)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with minimal valid data
        minimal_profile = create_default_artist_profile("Minimal", "Pop")
        is_valid, errors = validate_artist_profile(minimal_profile)
        self.assertTrue(is_valid, f"Minimal profile failed validation: {errors}")
        
        # Test with very long strings
        long_string = "A" * 10000
        long_profile = self.valid_profile.copy()
        long_profile["style_description"] = long_string
        is_valid, errors = validate_artist_profile(long_profile)
        self.assertTrue(is_valid, f"Long string profile failed validation: {errors}")
        
        # Test with special characters
        special_profile = self.valid_profile.copy()
        special_profile["stage_name"] = "Sp3c!@l Ch@r@ct3r$"
        is_valid, errors = validate_artist_profile(special_profile)
        self.assertTrue(is_valid, f"Special character profile failed validation: {errors}")


if __name__ == "__main__":
    unittest.main()
