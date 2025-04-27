"""
Backward Compatibility Test Module

This module tests backward compatibility of the new artist profile schema
with existing code and profiles.
"""

import unittest
import json
from datetime import datetime, date
from typing import Dict, Any, List

from artist_builder.schema.schema_converter import (
    legacy_to_new_schema,
    new_to_legacy_schema
)
from artist_builder.composer.artist_profile_composer import ArtistProfileComposer


class TestBackwardCompatibility(unittest.TestCase):
    """Test cases for backward compatibility with existing code and profiles."""
    
    def setUp(self):
        """Set up test fixtures."""
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
    
    def test_legacy_profile_conversion_roundtrip(self):
        """Test that a legacy profile can be converted to new schema and back without data loss."""
        # Convert legacy to new schema
        new_profile = legacy_to_new_schema(self.legacy_profile)
        
        # Convert back to legacy
        roundtrip_profile = new_to_legacy_schema(new_profile)
        
        # Check that essential fields are preserved
        self.assertEqual(roundtrip_profile["id"], self.legacy_profile["id"])
        self.assertEqual(roundtrip_profile["name"], self.legacy_profile["name"])
        self.assertEqual(roundtrip_profile["genre"], self.legacy_profile["genre"])
        self.assertEqual(roundtrip_profile["vibe"], self.legacy_profile["vibe"])
        self.assertEqual(roundtrip_profile["backstory"], self.legacy_profile["backstory"])
        self.assertEqual(roundtrip_profile["style"], self.legacy_profile["style"])
        self.assertEqual(roundtrip_profile["visual"], self.legacy_profile["visual"])
        self.assertEqual(roundtrip_profile["voice"], self.legacy_profile["voice"])
        
        # Check that some key tags are preserved (complete set might differ due to generation algorithm)
        for key_tag in ["trap", "mysterious", "intense", "phantomshadow"]:
            self.assertIn(key_tag, roundtrip_profile["tags"], f"Key tag {key_tag} missing from roundtrip profile")
    
    def test_composer_with_legacy_format_output(self):
        """Test that the composer can still output legacy format profiles if needed."""
        # Generate a new schema profile
        new_profile = self.composer.compose_profile(self.example_prompt, session_id="test_session_123")
        
        # Convert to legacy format
        legacy_profile = new_to_legacy_schema(new_profile)
        
        # Check that the legacy profile has all required fields
        required_fields = [
            "id", "name", "genre", "vibe", "backstory", "style", 
            "visual", "voice", "created_at", "source_prompt", 
            "session_id", "metadata", "version", "last_updated", 
            "status", "summary", "tags"
        ]
        
        for field in required_fields:
            self.assertIn(field, legacy_profile, f"Legacy profile missing required field: {field}")
    
    def test_legacy_code_compatibility(self):
        """Test that legacy code can still work with profiles from the new system."""
        # This simulates legacy code that expects specific fields
        def legacy_code_function(profile):
            # Legacy code might access these fields directly
            artist_name = profile["name"]
            genre = profile["genre"]
            vibe = profile["vibe"]
            
            # Legacy code might combine fields in specific ways
            description = f"{artist_name} is a {genre} artist with a {vibe} vibe."
            
            # Legacy code might expect specific nested fields
            tags = profile["tags"]
            
            return {
                "name": artist_name,
                "genre": genre,
                "vibe": vibe,
                "description": description,
                "tag_count": len(tags)
            }
        
        # Generate a new schema profile
        new_profile = self.composer.compose_profile(self.example_prompt, session_id="test_session_123")
        
        # Convert to legacy format for legacy code
        legacy_profile = new_to_legacy_schema(new_profile)
        
        # Test that legacy code can process the converted profile without errors
        try:
            result = legacy_code_function(legacy_profile)
            self.assertIsNotNone(result)
            self.assertEqual(result["name"], legacy_profile["name"])
            self.assertEqual(result["genre"], legacy_profile["genre"])
            self.assertEqual(result["vibe"], legacy_profile["vibe"])
        except Exception as e:
            self.fail(f"Legacy code failed to process converted profile: {e}")
    
    def test_metadata_preservation(self):
        """Test that custom metadata is preserved during conversion."""
        # Add custom metadata to legacy profile
        self.legacy_profile["metadata"] = {
            "custom_field": "custom_value",
            "numeric_field": 123,
            "nested_field": {
                "inner_field": "inner_value"
            }
        }
        
        # Convert to new schema and back
        new_profile = legacy_to_new_schema(self.legacy_profile)
        roundtrip_profile = new_to_legacy_schema(new_profile)
        
        # Check that metadata is preserved
        self.assertEqual(roundtrip_profile["metadata"]["custom_field"], "custom_value")
        self.assertEqual(roundtrip_profile["metadata"]["numeric_field"], 123)
        self.assertEqual(roundtrip_profile["metadata"]["nested_field"]["inner_field"], "inner_value")
    
    def test_backward_compatibility_with_minimal_legacy_profile(self):
        """Test backward compatibility with a minimal legacy profile."""
        # Create a minimal legacy profile with only required fields
        minimal_legacy_profile = {
            "id": "artist_minimal",
            "name": "Minimal Artist",
            "genre": "Electronic",
            "created_at": datetime.now().isoformat()
        }
        
        # Convert to new schema
        try:
            new_profile = legacy_to_new_schema(minimal_legacy_profile)
            self.assertEqual(new_profile["artist_id"], minimal_legacy_profile["id"])
            self.assertEqual(new_profile["stage_name"], minimal_legacy_profile["name"])
            self.assertEqual(new_profile["genre"], minimal_legacy_profile["genre"])
            
            # Check that required fields are filled with defaults
            self.assertIsNotNone(new_profile["subgenres"])
            self.assertIsNotNone(new_profile["personality_traits"])
            self.assertIsNotNone(new_profile["target_audience"])
            self.assertIsNotNone(new_profile["settings"])
        except Exception as e:
            self.fail(f"Failed to convert minimal legacy profile: {e}")


if __name__ == "__main__":
    unittest.main()
