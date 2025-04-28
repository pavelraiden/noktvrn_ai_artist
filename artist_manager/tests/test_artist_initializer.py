"""
Unit tests for the ArtistInitializer class.

This module contains tests for the ArtistInitializer class functionality including
creating new artist profiles, applying default values, and validating profiles.
"""

import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import yaml

# Add parent directory to path to import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artist_manager.artist_initializer import ArtistInitializer
from artist_manager.artist import Artist


class TestArtistInitializer(unittest.TestCase):
    """Test cases for the ArtistInitializer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock schema for testing
        self.mock_schema = {
            "artist_profile": {
                "required": [
                    "artist_id", "stage_name", "genre", "subgenres", 
                    "style_description", "voice_type", "personality_traits", 
                    "target_audience", "visual_identity_prompt", "settings"
                ]
            }
        }

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_init(self, mock_file, mock_yaml_load):
        """Test initializing an ArtistInitializer."""
        mock_yaml_load.return_value = self.mock_schema
        initializer = ArtistInitializer()
        self.assertEqual(initializer.schema, self.mock_schema)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_default_values(self, mock_file, mock_yaml_load):
        """Test getting default values for artist profile fields."""
        mock_yaml_load.return_value = self.mock_schema
        initializer = ArtistInitializer()
        defaults = initializer._get_default_values()
        
        # Check that defaults include expected sections
        self.assertIn("settings", defaults)
        self.assertIn("is_active", defaults)
        self.assertIn("update_history", defaults)
        self.assertIn("metadata", defaults)
        
        # Check that settings include expected subsections
        settings = defaults["settings"]
        self.assertIn("release_strategy", settings)
        self.assertIn("llm_assignments", settings)
        self.assertIn("training_data_version", settings)
        self.assertIn("trend_alignment_behavior", settings)
        self.assertIn("behavior_evolution_settings", settings)
        self.assertIn("social_media_presence", settings)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_default_subgenres(self, mock_file, mock_yaml_load):
        """Test getting default subgenres based on a primary genre."""
        mock_yaml_load.return_value = self.mock_schema
        initializer = ArtistInitializer()
        
        # Test with known genre
        subgenres = initializer._get_default_subgenres("trap")
        self.assertIsInstance(subgenres, list)
        self.assertGreater(len(subgenres), 0)
        
        # Test with unknown genre
        subgenres = initializer._get_default_subgenres("unknown_genre")
        self.assertIsInstance(subgenres, list)
        self.assertGreater(len(subgenres), 0)
        self.assertEqual(len(subgenres), 2)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_default_personality_traits(self, mock_file, mock_yaml_load):
        """Test getting default personality traits based on a genre."""
        mock_yaml_load.return_value = self.mock_schema
        initializer = ArtistInitializer()
        
        # Test with known genre
        traits = initializer._get_default_personality_traits("rock")
        self.assertIsInstance(traits, list)
        self.assertGreater(len(traits), 0)
        
        # Test with unknown genre
        traits = initializer._get_default_personality_traits("unknown_genre")
        self.assertIsInstance(traits, list)
        self.assertGreater(len(traits), 0)
        self.assertEqual(len(traits), 3)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_default_target_audience(self, mock_file, mock_yaml_load):
        """Test getting default target audience based on a genre."""
        mock_yaml_load.return_value = self.mock_schema
        initializer = ArtistInitializer()
        
        # Test with known genre
        audience = initializer._get_default_target_audience("electronic")
        self.assertIsInstance(audience, str)
        self.assertGreater(len(audience), 0)
        
        # Test with unknown genre
        audience = initializer._get_default_target_audience("unknown_genre")
        self.assertIsInstance(audience, str)
        self.assertGreater(len(audience), 0)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('artist_manager.artist.Artist')
    def test_initialize_artist_with_minimal_input(self, mock_artist_class, mock_file, mock_yaml_load):
        """Test initializing an artist with minimal input."""
        mock_yaml_load.return_value = self.mock_schema
        
        # Mock Artist instance
        mock_artist = MagicMock()
        mock_artist.validate.return_value = (True, [])
        mock_artist_class.return_value = mock_artist
        
        initializer = ArtistInitializer()
        
        # Minimal input with just stage name and genre
        user_input = {
            "stage_name": "Test Artist",
            "genre": "Electronic"
        }
        
        artist, warnings = initializer.initialize_artist(user_input)
        
        # Check that Artist was created with the right data
        self.assertEqual(artist, mock_artist)
        
        # Check that the profile was validated
        mock_artist.validate.assert_called_once()
        
        # Check that warnings were generated for default values
        self.assertGreater(len(warnings), 0)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('artist_manager.artist.Artist')
    def test_initialize_artist_with_complete_input(self, mock_artist_class, mock_file, mock_yaml_load):
        """Test initializing an artist with complete input."""
        mock_yaml_load.return_value = self.mock_schema
        
        # Mock Artist instance
        mock_artist = MagicMock()
        mock_artist.validate.return_value = (True, [])
        mock_artist_class.return_value = mock_artist
        
        initializer = ArtistInitializer()
        
        # Complete input with all required fields
        user_input = {
            "stage_name": "Complete Artist",
            "genre": "Rock",
            "subgenres": ["Alternative", "Indie"],
            "style_description": "A unique rock sound with indie influences",
            "voice_type": "Powerful vocals with emotional delivery",
            "personality_traits": ["Passionate", "Authentic", "Energetic"],
            "target_audience": "Rock fans who appreciate authentic, emotional music",
            "visual_identity_prompt": "Artist performing on stage with dramatic lighting",
            "settings": {
                "release_strategy": {
                    "track_release_random_days": [7, 21],
                    "video_release_ratio": 0.8
                },
                "llm_assignments": {
                    "artist_prompt_llm": "gpt-4",
                    "song_prompt_llm": "gpt-4",
                    "video_prompt_llm": "gpt-4",
                    "final_validator_llm": "gpt-4"
                },
                "training_data_version": "1.0"
            }
        }
        
        artist, warnings = initializer.initialize_artist(user_input)
        
        # Check that Artist was created with the right data
        self.assertEqual(artist, mock_artist)
        
        # Check that the profile was validated
        mock_artist.validate.assert_called_once()
        
        # Check that no warnings were generated for complete input
        self.assertEqual(len(warnings), 0)

    @patch('artist_manager.artist_initializer.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('artist_manager.artist.Artist')
    def test_create_minimal_artist(self, mock_artist_class, mock_file, mock_yaml_load):
        """Test creating a minimal valid artist profile."""
        mock_yaml_load.return_value = self.mock_schema
        
        # Mock Artist instance
        mock_artist = MagicMock()
        mock_artist.validate.return_value = (True, [])
        mock_artist_class.return_value = mock_artist
        
        initializer = ArtistInitializer()
        
        artist = initializer.create_minimal_artist("Minimal Artist", "Pop")
        
        # Check that Artist was created
        self.assertEqual(artist, mock_artist)
        
        # Check that initialize_artist was called with the right data
        mock_artist_class.assert_called_once()


if __name__ == '__main__':
    unittest.main()
