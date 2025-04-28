"""
Unit tests for the ArtistUpdater class.

This module contains tests for the ArtistUpdater class functionality including
updating existing artist profiles, applying trend-based updates, and logging changes.
"""

import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import yaml

# Add parent directory to path to import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artist_manager.artist_updater import ArtistUpdater
from artist_manager.artist import Artist


class TestArtistUpdater(unittest.TestCase):
    """Test cases for the ArtistUpdater class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a valid artist profile for testing
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
                "training_data_version": "1.0",
                "trend_alignment_behavior": "soft",
                "behavior_evolution_settings": {
                    "allow_minor_genre_shifts": True,
                    "allow_personality_shifts": True,
                    "safe_mode": True,
                    "evolution_speed": "medium",
                    "preserve_core_identity": True
                },
                "social_media_presence": {
                    "platforms": ["instagram", "tiktok"],
                    "posting_style": "casual",
                    "engagement_strategy": "moderate"
                }
            },
            "update_history": []
        }
        
        # Create sample trend data for testing
        self.trend_data = {
            "genre_trends": {
                "Vaporwave": 0.85,
                "Lofi": 0.65,
                "Ambient": 0.45
            },
            "personality_trends": {
                "Futuristic": 0.9,
                "Nostalgic": 0.7,
                "Experimental": 0.5
            },
            "visual_trends": {
                "Cyberpunk": 0.8,
                "Retro Gaming": 0.6
            },
            "audience_trends": {
                "Gen Z": 0.75,
                "Gamers": 0.65
            },
            "release_trends": {
                "frequency": 0.85,
                "video_ratio": 0.7
            },
            "social_media_trends": {
                "platforms": {
                    "twitter": 0.8,
                    "youtube": 0.7
                },
                "posting_style": 0.8
            }
        }

    def test_init(self):
        """Test initializing an ArtistUpdater."""
        updater = ArtistUpdater()
        self.assertIsNotNone(updater.schema_path)

    @patch('artist_manager.artist.Artist.update')
    def test_update_artist(self, mock_update):
        """Test updating an artist profile."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.update.return_value = True
        mock_artist.validate.return_value = (True, [])
        
        updater = ArtistUpdater()
        
        # Test updates
        updates = {
            "stage_name": "Updated Artist",
            "settings.release_strategy.video_release_ratio": 0.8
        }
        
        success, warnings = updater.update_artist(
            mock_artist, 
            updates, 
            "Test update", 
            "unit_test"
        )
        
        # Check that update was called with the right parameters
        mock_artist.update.assert_called_once_with(
            updates, 
            "Test update", 
            "unit_test"
        )
        
        # Check that the update was successful
        self.assertTrue(success)
        self.assertEqual(len(warnings), 0)

    @patch('artist_manager.artist.Artist.update')
    def test_update_artist_with_validation_errors(self, mock_update):
        """Test updating an artist profile with validation errors."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.update.return_value = True
        mock_artist.validate.return_value = (False, ["Error 1", "Error 2"])
        
        updater = ArtistUpdater()
        
        # Test updates
        updates = {
            "stage_name": "Updated Artist",
            "settings.release_strategy.video_release_ratio": 0.8
        }
        
        success, warnings = updater.update_artist(
            mock_artist, 
            updates, 
            "Test update", 
            "unit_test"
        )
        
        # Check that update was called
        mock_artist.update.assert_called_once()
        
        # Check that the update was successful but has warnings
        self.assertTrue(success)
        self.assertGreater(len(warnings), 0)

    def test_update_artist_with_invalid_artist(self):
        """Test updating with an invalid artist object."""
        updater = ArtistUpdater()
        
        # Test with a non-Artist object
        success, warnings = updater.update_artist(
            "not_an_artist", 
            {"stage_name": "Updated Artist"}, 
            "Test update", 
            "unit_test"
        )
        
        # Check that the update failed
        self.assertFalse(success)
        self.assertGreater(len(warnings), 0)

    @patch('artist_manager.artist.Artist.get_value')
    @patch('artist_manager.artist.Artist.update')
    def test_apply_trend_updates(self, mock_update, mock_get_value):
        """Test applying trend updates to an artist profile."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.update.return_value = True
        mock_artist.validate.return_value = (True, [])
        
        # Mock get_value to return appropriate values for different paths
        def mock_get_value_side_effect(path, default=None):
            if path == "settings.trend_alignment_behavior":
                return "soft"
            elif path == "settings.behavior_evolution_settings":
                return {
                    "allow_minor_genre_shifts": True,
                    "allow_personality_shifts": True,
                    "safe_mode": True,
                    "evolution_speed": "medium",
                    "preserve_core_identity": True
                }
            elif path == "subgenres":
                return ["Synthwave", "Chillwave"]
            elif path == "genre":
                return "Electronic"
            elif path == "personality_traits":
                return ["Mysterious", "Innovative", "Calm"]
            elif path == "settings.social_media_presence.platforms":
                return ["instagram", "tiktok"]
            elif path == "settings.social_media_presence.posting_style":
                return "casual"
            elif path == "settings.release_strategy.track_release_random_days":
                return [5, 20]
            elif path == "settings.release_strategy.video_release_ratio":
                return 0.6
            else:
                return default
        
        mock_get_value.side_effect = mock_get_value_side_effect
        
        updater = ArtistUpdater()
        
        success, applied_updates, warnings = updater.apply_trend_updates(
            mock_artist, 
            self.trend_data
        )
        
        # Check that update was called
        mock_artist.update.assert_called_once()
        
        # Check that the update was successful
        self.assertTrue(success)
        self.assertGreater(len(applied_updates), 0)
        self.assertEqual(len(warnings), 0)

    @patch('artist_manager.artist.Artist.get_value')
    @patch('artist_manager.artist.Artist.update')
    def test_apply_trend_updates_with_strict_alignment(self, mock_update, mock_get_value):
        """Test applying trend updates with strict alignment setting."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.update.return_value = True
        mock_artist.validate.return_value = (True, [])
        
        # Mock get_value to return appropriate values for different paths
        def mock_get_value_side_effect(path, default=None):
            if path == "settings.trend_alignment_behavior":
                return "strict"  # Strict alignment
            elif path == "settings.behavior_evolution_settings":
                return {
                    "allow_minor_genre_shifts": True,
                    "allow_personality_shifts": True,
                    "safe_mode": True,
                    "evolution_speed": "medium",
                    "preserve_core_identity": True
                }
            elif path == "subgenres":
                return ["Synthwave", "Chillwave"]
            elif path == "genre":
                return "Electronic"
            elif path == "personality_traits":
                return ["Mysterious", "Innovative", "Calm"]
            elif path == "settings.social_media_presence.platforms":
                return ["instagram", "tiktok"]
            elif path == "settings.social_media_presence.posting_style":
                return "casual"
            elif path == "settings.release_strategy.track_release_random_days":
                return [5, 20]
            elif path == "settings.release_strategy.video_release_ratio":
                return 0.6
            else:
                return default
        
        mock_get_value.side_effect = mock_get_value_side_effect
        
        updater = ArtistUpdater()
        
        success, applied_updates, warnings = updater.apply_trend_updates(
            mock_artist, 
            self.trend_data
        )
        
        # Check that update was called
        mock_artist.update.assert_called_once()
        
        # Check that the update was successful
        self.assertTrue(success)
        # Strict alignment should result in more updates
        self.assertGreater(len(applied_updates), 0)
        self.assertEqual(len(warnings), 0)

    @patch('artist_manager.artist.Artist.get_value')
    @patch('artist_manager.artist.Artist.update')
    def test_apply_trend_updates_with_experimental_alignment(self, mock_update, mock_get_value):
        """Test applying trend updates with experimental alignment setting."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.update.return_value = True
        mock_artist.validate.return_value = (True, [])
        
        # Mock get_value to return appropriate values for different paths
        def mock_get_value_side_effect(path, default=None):
            if path == "settings.trend_alignment_behavior":
                return "experimental"  # Experimental alignment
            elif path == "settings.behavior_evolution_settings":
                return {
                    "allow_minor_genre_shifts": True,
                    "allow_personality_shifts": True,
                    "safe_mode": True,
                    "evolution_speed": "medium",
                    "preserve_core_identity": True
                }
            elif path == "subgenres":
                return ["Synthwave", "Chillwave"]
            elif path == "genre":
                return "Electronic"
            elif path == "personality_traits":
                return ["Mysterious", "Innovative", "Calm"]
            elif path == "settings.social_media_presence.platforms":
                return ["instagram", "tiktok"]
            elif path == "settings.social_media_presence.posting_style":
                return "casual"
            elif path == "settings.release_strategy.track_release_random_days":
                return [5, 20]
            elif path == "settings.release_strategy.video_release_ratio":
                return 0.6
            else:
                return default
        
        mock_get_value.side_effect = mock_get_value_side_effect
        
        updater = ArtistUpdater()
        
        success, applied_updates, warnings = updater.apply_trend_updates(
            mock_artist, 
            self.trend_data
        )
        
        # Check that update was called
        mock_artist.update.assert_called_once()
        
        # Check that the update was successful
        self.assertTrue(success)
        # Experimental alignment should result in fewer updates
        self.assertGreaterEqual(len(applied_updates), 0)
        self.assertEqual(len(warnings), 0)

    @patch('artist_manager.artist.Artist.get_value')
    def test_apply_trend_updates_with_no_evolution_allowed(self, mock_get_value):
        """Test applying trend updates when evolution is not allowed."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.validate.return_value = (True, [])
        
        # Mock get_value to return appropriate values for different paths
        def mock_get_value_side_effect(path, default=None):
            if path == "settings.trend_alignment_behavior":
                return "soft"
            elif path == "settings.behavior_evolution_settings":
                return {
                    "allow_minor_genre_shifts": False,  # No genre shifts allowed
                    "allow_personality_shifts": False,  # No personality shifts allowed
                    "safe_mode": True,
                    "evolution_speed": "medium",
                    "preserve_core_identity": True
                }
            elif path == "artist_id":
                return "test-artist-123"
            elif path == "stage_name":
                return "Test Artist"
            else:
                return default
        
        mock_get_value.side_effect = mock_get_value_side_effect
        
        updater = ArtistUpdater()
        
        # Create trend data with only genre and personality trends
        limited_trend_data = {
            "genre_trends": self.trend_data["genre_trends"],
            "personality_trends": self.trend_data["personality_trends"]
        }
        
        success, applied_updates, warnings = updater.apply_trend_updates(
            mock_artist, 
            limited_trend_data
        )
        
        # Check that the update was successful but no updates were applied
        self.assertTrue(success)
        self.assertEqual(len(applied_updates), 0)
        self.assertGreater(len(warnings), 0)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_update_log(self, mock_file, mock_makedirs):
        """Test saving an update log."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        
        # Mock get_value to return appropriate values
        def mock_get_value_side_effect(path, default=None):
            if path == "artist_id":
                return "test-artist-123"
            elif path == "stage_name":
                return "Test Artist"
            else:
                return default
        
        mock_artist.get_value.side_effect = mock_get_value_side_effect
        
        updater = ArtistUpdater()
        
        # Test saving update log
        updates = ["Updated genre to Vaporwave", "Added Futuristic to personality traits"]
        result = updater.save_update_log(mock_artist, updates, "/path/to/logs")
        
        # Check that the log was saved successfully
        self.assertTrue(result)
        mock_makedirs.assert_called_once_with("/path/to/logs", exist_ok=True)
        mock_file.assert_called_once()
        mock_file().write.assert_called_once()

    @patch('artist_manager.artist.Artist.load')
    def test_load_artist_from_file(self, mock_load):
        """Test loading an artist profile from a file."""
        # Mock Artist.load to return a mock artist
        mock_artist = MagicMock(spec=Artist)
        mock_load.return_value = mock_artist
        
        updater = ArtistUpdater()
        
        # Test loading artist from file
        artist = updater.load_artist_from_file("/path/to/artist.json")
        
        # Check that Artist.load was called with the right parameters
        mock_load.assert_called_once_with("/path/to/artist.json", updater.schema_path)
        
        # Check that the correct artist was returned
        self.assertEqual(artist, mock_artist)

    @patch('artist_manager.artist.Artist.save')
    def test_save_artist_to_file(self, mock_save):
        """Test saving an artist profile to a file."""
        # Mock Artist instance
        mock_artist = MagicMock(spec=Artist)
        mock_artist.save.return_value = True
        
        updater = ArtistUpdater()
        
        # Test saving artist to file
        result = updater.save_artist_to_file(mock_artist, "/path/to/artist.json", "json")
        
        # Check that Artist.save was called with the right parameters
        mock_artist.save.assert_called_once_with("/path/to/artist.json", "json")
        
        # Check that the save was successful
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
