"""
Unit tests for the Artist class.

This module contains tests for the Artist class functionality including
creation, validation, serialization, and profile management.
"""

import os
import json
import yaml
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open

# Add parent directory to path to import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artist_manager.artist import Artist


class TestArtist(unittest.TestCase):
    """Test cases for the Artist class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a valid minimal artist profile for testing
        self.valid_profile = {
            "artist_id": "test-artist-123",
            "stage_name": "Test Artist",
            "genre": "Electronic",
            "subgenres": ["Synthwave", "Chillwave"],
            "style_description": "A unique electronic sound with retro influences",
            "voice_type": "Ethereal vocals with digital effects",
            "personality_traits": ["Mysterious", "Innovative", "Calm"],
            "target_audience": "Electronic music fans who appreciate atmospheric sounds",
            "visual_identity_prompt": "Neon cityscape with retro-futuristic elements",
            "settings": {
                "release_strategy": {
                    "track_release_random_days": [5, 20],
                    "video_release_ratio": 0.6
                },
                "llm_assignments": {
                    "artist_prompt_llm": "gpt-4",
                    "song_prompt_llm": "gpt-4",
                    "video_prompt_llm": "gpt-4",
                    "final_validator_llm": "gpt-4"
                },
                "training_data_version": "1.0"
            },
            "creation_date": datetime.now().isoformat()
        }
        
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

    @patch('artist_manager.artist.Artist._load_schema')
    def test_init_with_valid_profile(self, mock_load_schema):
        """Test initializing an Artist with a valid profile."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        self.assertEqual(artist.profile["stage_name"], "Test Artist")
        self.assertEqual(artist.profile["genre"], "Electronic")

    @patch('artist_manager.artist.Artist._load_schema')
    def test_init_without_profile(self, mock_load_schema):
        """Test initializing an Artist without a profile."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist()
        self.assertIn("artist_id", artist.profile)
        self.assertIn("creation_date", artist.profile)

    @patch('artist_manager.artist.Artist._load_schema')
    def test_validate_valid_profile(self, mock_load_schema):
        """Test validating a valid profile."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        is_valid, errors = artist.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    @patch('artist_manager.artist.Artist._load_schema')
    def test_validate_invalid_profile(self, mock_load_schema):
        """Test validating an invalid profile."""
        mock_load_schema.return_value = self.mock_schema
        # Create an invalid profile missing required fields
        invalid_profile = {
            "artist_id": "test-artist-123",
            "stage_name": "Test Artist"
            # Missing other required fields
        }
        artist = Artist(invalid_profile)
        is_valid, errors = artist.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    @patch('artist_manager.artist.Artist._load_schema')
    def test_to_dict(self, mock_load_schema):
        """Test converting an artist profile to a dictionary."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        profile_dict = artist.to_dict()
        self.assertEqual(profile_dict["stage_name"], "Test Artist")
        self.assertEqual(profile_dict["genre"], "Electronic")

    @patch('artist_manager.artist.Artist._load_schema')
    def test_to_json(self, mock_load_schema):
        """Test converting an artist profile to JSON."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        json_str = artist.to_json()
        # Parse the JSON string back to a dictionary
        parsed_json = json.loads(json_str)
        self.assertEqual(parsed_json["stage_name"], "Test Artist")
        self.assertEqual(parsed_json["genre"], "Electronic")

    @patch('artist_manager.artist.Artist._load_schema')
    def test_to_yaml(self, mock_load_schema):
        """Test converting an artist profile to YAML."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        yaml_str = artist.to_yaml()
        # Parse the YAML string back to a dictionary
        parsed_yaml = yaml.safe_load(yaml_str)
        self.assertEqual(parsed_yaml["stage_name"], "Test Artist")
        self.assertEqual(parsed_yaml["genre"], "Electronic")

    @patch('artist_manager.artist.Artist._load_schema')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_json(self, mock_makedirs, mock_file, mock_load_schema):
        """Test saving an artist profile to a JSON file."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        result = artist.save("/path/to/artist.json", "json")
        self.assertTrue(result)
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once_with("/path/to/artist.json", 'w')

    @patch('artist_manager.artist.Artist._load_schema')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_yaml(self, mock_makedirs, mock_file, mock_load_schema):
        """Test saving an artist profile to a YAML file."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        result = artist.save("/path/to/artist.yaml", "yaml")
        self.assertTrue(result)
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once_with("/path/to/artist.yaml", 'w')

    @patch('artist_manager.artist.Artist._load_schema')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({"stage_name": "Loaded Artist", "genre": "Rock"}))
    def test_load_json(self, mock_file, mock_load_schema):
        """Test loading an artist profile from a JSON file."""
        mock_load_schema.return_value = self.mock_schema
        with patch('json.load', return_value={"stage_name": "Loaded Artist", "genre": "Rock"}):
            artist = Artist.load("/path/to/artist.json")
            self.assertEqual(artist.profile["stage_name"], "Loaded Artist")
            self.assertEqual(artist.profile["genre"], "Rock")

    @patch('artist_manager.artist.Artist._load_schema')
    def test_update(self, mock_load_schema):
        """Test updating an artist profile."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        updates = {
            "stage_name": "Updated Artist",
            "settings.release_strategy.video_release_ratio": 0.8
        }
        result = artist.update(updates, "Test update", "unit_test")
        self.assertTrue(result)
        self.assertEqual(artist.profile["stage_name"], "Updated Artist")
        self.assertEqual(artist.profile["settings"]["release_strategy"]["video_release_ratio"], 0.8)
        # Check that update history was recorded
        self.assertGreaterEqual(len(artist.profile["update_history"]), 1)
        last_update = artist.profile["update_history"][-1]
        self.assertEqual(last_update["update_reason"], "Test update")
        self.assertEqual(last_update["update_source"], "unit_test")

    @patch('artist_manager.artist.Artist._load_schema')
    def test_get_value(self, mock_load_schema):
        """Test getting values from an artist profile."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        # Test getting top-level field
        self.assertEqual(artist.get_value("stage_name"), "Test Artist")
        # Test getting nested field
        self.assertEqual(artist.get_value("settings.release_strategy.video_release_ratio"), 0.6)
        # Test getting non-existent field
        self.assertIsNone(artist.get_value("non_existent_field"))
        # Test getting non-existent field with default
        self.assertEqual(artist.get_value("non_existent_field", "default"), "default")

    @patch('artist_manager.artist.Artist._load_schema')
    def test_set_value(self, mock_load_schema):
        """Test setting values in an artist profile."""
        mock_load_schema.return_value = self.mock_schema
        artist = Artist(self.valid_profile)
        # Test setting top-level field
        result = artist.set_value("stage_name", "New Name")
        self.assertTrue(result)
        self.assertEqual(artist.profile["stage_name"], "New Name")
        # Test setting nested field
        result = artist.set_value("settings.release_strategy.video_release_ratio", 0.9)
        self.assertTrue(result)
        self.assertEqual(artist.profile["settings"]["release_strategy"]["video_release_ratio"], 0.9)


if __name__ == '__main__':
    unittest.main()
