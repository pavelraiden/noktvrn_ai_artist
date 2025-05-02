"""
Test Module for Artist Profile Builder

This module contains tests for the Artist Profile Builder to ensure
all components work together properly.
"""

import logging
import json
import os
import sys
import unittest
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from builder.profile_builder import ArtistProfileBuilder
from builder.error_handler import (
    ArtistBuilderError,
    InputError,
    ValidationError,
    StorageError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.test_profile_builder")


class TestArtistProfileBuilder(unittest.TestCase):
    """Test cases for the Artist Profile Builder."""

    def setUp(self):
        """Set up test environment."""
        self.builder = ArtistProfileBuilder()

        # Example input data for testing
        self.test_input = {
            "stage_name": "Test Artist",
            "genre": "Electronic",
            "subgenres": ["Synthwave", "Chillwave"],
            "style_description": "Test style description",
            "voice_type": "Test voice type",
            "personality_traits": ["Creative", "Innovative"],
            "target_audience": "Test audience",
            "visual_identity_prompt": "Test visual identity",
        }

        # Keep track of created profiles for cleanup
        self.created_profiles = []

    def tearDown(self):
        """Clean up after tests."""
        # Delete any profiles created during tests
        for profile_id in self.created_profiles:
            try:
                self.builder.delete_artist_profile(profile_id)
                logger.info(f"Deleted test profile: {profile_id}")
            except Exception as e:
                logger.warning(f"Error deleting test profile {profile_id}: {e}")

    def test_create_artist_profile(self):
        """Test creating an artist profile."""
        # Create profile
        profile = self.builder.create_artist_profile(self.test_input, "test")

        # Add to cleanup list
        self.created_profiles.append(profile["artist_id"])

        # Verify profile was created
        self.assertIsNotNone(profile)
        self.assertIn("artist_id", profile)
        self.assertEqual(profile["stage_name"], self.test_input["stage_name"])
        self.assertEqual(profile["genre"], self.test_input["genre"])

        logger.info(f"Created test profile: {profile['artist_id']}")
        return profile

    def test_get_artist_profile(self):
        """Test getting an artist profile."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # Get the profile
        retrieved_profile = self.builder.get_artist_profile(
            created_profile["artist_id"]
        )

        # Verify profile was retrieved
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile["artist_id"], created_profile["artist_id"])
        self.assertEqual(retrieved_profile["stage_name"], created_profile["stage_name"])

        logger.info(f"Retrieved test profile: {retrieved_profile['artist_id']}")

    def test_update_artist_profile(self):
        """Test updating an artist profile."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # Update the profile
        updates = {
            "backstory": "This is a test backstory update.",
            "update_reason": "Testing update functionality",
        }
        updated_profile = self.builder.update_artist_profile(
            created_profile["artist_id"], updates
        )

        # Verify profile was updated
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile["artist_id"], created_profile["artist_id"])
        self.assertEqual(updated_profile["backstory"], updates["backstory"])
        self.assertIn("update_history", updated_profile)

        logger.info(f"Updated test profile: {updated_profile['artist_id']}")

    def test_list_artist_profiles(self):
        """Test listing artist profiles."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # List profiles
        profiles = self.builder.list_artist_profiles()

        # Verify profiles were listed
        self.assertIsNotNone(profiles)
        self.assertIsInstance(profiles, list)

        # Check if our created profile is in the list
        found = False
        for profile in profiles:
            if profile["artist_id"] == created_profile["artist_id"]:
                found = True
                break

        self.assertTrue(found, "Created profile not found in list")

        logger.info(f"Listed {len(profiles)} profiles")

    def test_search_artist_profiles(self):
        """Test searching artist profiles."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # Search for profiles
        search_criteria = {"genre": created_profile["genre"]}
        matching_profiles = self.builder.search_artist_profiles(search_criteria)

        # Verify profiles were found
        self.assertIsNotNone(matching_profiles)
        self.assertIsInstance(matching_profiles, list)

        # Check if our created profile is in the results
        found = False
        for profile in matching_profiles:
            if profile["artist_id"] == created_profile["artist_id"]:
                found = True
                break

        self.assertTrue(found, "Created profile not found in search results")

        logger.info(f"Found {len(matching_profiles)} matching profiles")

    def test_apply_trend_analysis(self):
        """Test applying trend analysis to a profile."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # Apply trend analysis
        trend_data = {
            "trending_subgenres": ["Darksynth", "Vaporwave"],
            "genre_compatibility": {"Electronic": {"Darksynth": 0.9, "Vaporwave": 0.8}},
        }
        updated_profile = self.builder.apply_trend_analysis(
            created_profile["artist_id"], trend_data
        )

        # Verify profile was updated
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile["artist_id"], created_profile["artist_id"])

        logger.info(
            f"Applied trend analysis to test profile: {updated_profile['artist_id']}"
        )

    def test_adapt_behavior(self):
        """Test adapting behavior based on performance data."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # Apply behavior adaptation
        performance_data = {"trait_performance": {"Creative": 0.85, "Innovative": 0.65}}
        updated_profile = self.builder.adapt_behavior(
            created_profile["artist_id"], performance_data
        )

        # Verify profile was updated
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile["artist_id"], created_profile["artist_id"])

        logger.info(
            f"Adapted behavior for test profile: {updated_profile['artist_id']}"
        )

    def test_delete_artist_profile(self):
        """Test deleting an artist profile."""
        # Create a profile first
        created_profile = self.test_create_artist_profile()

        # Remove from cleanup list since we're deleting it manually
        self.created_profiles.remove(created_profile["artist_id"])

        # Delete the profile
        success = self.builder.delete_artist_profile(created_profile["artist_id"])

        # Verify profile was deleted
        self.assertTrue(success)

        # Verify profile no longer exists
        with self.assertRaises(Exception):
            self.builder.get_artist_profile(created_profile["artist_id"])

        logger.info(f"Deleted test profile: {created_profile['artist_id']}")

    def test_error_handling(self):
        """Test error handling."""
        # Test handling of non-existent profile
        with self.assertRaises(Exception):
            self.builder.get_artist_profile("non-existent-id")

        logger.info("Error handling test passed")

    def test_full_workflow(self):
        """Test the full workflow from creation to deletion."""
        # Create profile
        profile = self.builder.create_artist_profile(self.test_input, "test")
        self.created_profiles.append(profile["artist_id"])

        # Update profile
        updates = {
            "backstory": "This is a test backstory for the full workflow test.",
            "update_reason": "Testing full workflow",
        }
        updated_profile = self.builder.update_artist_profile(
            profile["artist_id"], updates
        )

        # Apply trend analysis
        trend_data = {
            "trending_subgenres": ["Darksynth"],
            "genre_compatibility": {"Electronic": {"Darksynth": 0.9}},
        }
        trend_profile = self.builder.apply_trend_analysis(
            profile["artist_id"], trend_data
        )

        # Apply behavior adaptation
        performance_data = {"trait_performance": {"Creative": 0.85}}
        behavior_profile = self.builder.adapt_behavior(
            profile["artist_id"], performance_data
        )

        # Get the profile
        retrieved_profile = self.builder.get_artist_profile(profile["artist_id"])

        # Verify the final state
        self.assertEqual(retrieved_profile["artist_id"], profile["artist_id"])
        self.assertEqual(retrieved_profile["backstory"], updates["backstory"])

        # Remove from cleanup list since we're deleting it manually
        self.created_profiles.remove(profile["artist_id"])

        # Delete the profile
        success = self.builder.delete_artist_profile(profile["artist_id"])
        self.assertTrue(success)

        logger.info("Full workflow test passed")


def run_tests():
    """Run the test suite."""
    unittest.main(argv=["first-arg-is-ignored"], exit=False)


if __name__ == "__main__":
    run_tests()
