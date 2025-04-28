"""
Backward Compatibility Test Suite for the Artist Builder and Evolution System.

This module contains tests to ensure that the enhanced Artist Builder and Evolution System
maintains backward compatibility with existing artist profiles, APIs, and workflows.
"""

import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import components to test
from artist_builder.trend_analyzer import TrendAnalyzer
from artist_builder.role_optimizer import RoleDynamicOptimizer
from artist_builder.llm_collaboration import LLMCollaboration
from artist_builder.artist_analytics import ArtistAnalytics
from artist_builder.artist_interface import ArtistCreationInterface
from artist_builder.schema.artist_profile_schema import ArtistProfile
from artist_builder.schema.schema_converter import convert_profile_to_latest


class TestBackwardCompatibility(unittest.TestCase):
    """Test cases for backward compatibility of the Artist Builder and Evolution System."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "artists"), exist_ok=True)
        
        # Create legacy artist profile (v1 format)
        self.legacy_artist_slug = "legacy-artist"
        os.makedirs(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug), exist_ok=True)
        
        self.legacy_profile = {
            "name": "Legacy Artist",
            "genre": "Electronic",
            "subgenres": ["Ambient", "Downtempo"],
            "style": ["Atmospheric", "Melodic", "Experimental"],
            "description": "An atmospheric electronic artist with melodic elements",
            "audience": "Electronic music enthusiasts",
            "created_at": "2024-01-15T12:00:00Z",
            "version": 1
        }
        
        with open(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "profile.json"), "w") as f:
            json.dump(self.legacy_profile, f)
        
        # Create v2 format artist profile
        self.v2_artist_slug = "v2-artist"
        os.makedirs(os.path.join(self.temp_dir, "artists", self.v2_artist_slug), exist_ok=True)
        
        self.v2_profile = {
            "name": "V2 Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Electropop"]
            },
            "style_tags": ["Upbeat", "Melodic", "Catchy"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing",
            "metadata": {
                "created_at": "2024-06-15T12:00:00Z",
                "version": 2
            }
        }
        
        with open(os.path.join(self.temp_dir, "artists", self.v2_artist_slug, "profile.json"), "w") as f:
            json.dump(self.v2_profile, f)
        
        # Initialize components
        self.trend_analyzer = TrendAnalyzer(config={"cache_dir": os.path.join(self.temp_dir, "cache")})
        self.role_optimizer = RoleDynamicOptimizer()
        self.llm_collaboration = LLMCollaboration()
        self.analytics = ArtistAnalytics(config={
            "artists_dir": os.path.join(self.temp_dir, "artists"),
            "analytics_dir": os.path.join(self.temp_dir, "analytics")
        })
        self.interface = ArtistCreationInterface(config={
            "artists_dir": os.path.join(self.temp_dir, "artists"),
            "analytics_dir": os.path.join(self.temp_dir, "analytics")
        })

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_schema_conversion(self):
        """Test conversion of legacy artist profiles to the latest schema."""
        # Convert legacy profile to latest schema
        converted_profile = convert_profile_to_latest(self.legacy_profile)
        
        # Verify conversion
        self.assertIsNotNone(converted_profile)
        self.assertEqual(converted_profile["name"], "Legacy Artist")
        
        # Check new schema structure
        self.assertIn("genre", converted_profile)
        self.assertIsInstance(converted_profile["genre"], dict)
        self.assertEqual(converted_profile["genre"]["main"], "Electronic")
        self.assertIn("subgenres", converted_profile["genre"])
        self.assertIn("Ambient", converted_profile["genre"]["subgenres"])
        
        # Check style tags
        self.assertIn("style_tags", converted_profile)
        self.assertIn("Atmospheric", converted_profile["style_tags"])
        
        # Check vibe (converted from description)
        self.assertIn("vibe", converted_profile)
        
        # Check target audience (converted from audience)
        self.assertIn("target_audience", converted_profile)
        
        # Check metadata
        self.assertIn("metadata", converted_profile)
        self.assertIn("created_at", converted_profile["metadata"])
        self.assertIn("version", converted_profile["metadata"])
        
        # Validate with Pydantic model
        artist_profile = ArtistProfile(**converted_profile)
        self.assertEqual(artist_profile.name, "Legacy Artist")
        self.assertEqual(artist_profile.genre.main, "Electronic")

    def test_trend_analyzer_with_legacy_profiles(self):
        """Test trend analyzer compatibility with legacy artist profiles."""
        # Mock trend data
        trend_data = {
            "trending_genres": ["Electronic", "Ambient", "Downtempo"],
            "trending_styles": ["Atmospheric", "Melodic", "Experimental"],
            "trending_topics": ["Nature", "Space", "Meditation"]
        }
        
        # Analyze compatibility with legacy profile
        compatibility = self.trend_analyzer.analyze_artist_compatibility(
            artist_slug=self.legacy_artist_slug,
            artist_profile=self.legacy_profile,
            trend_data=trend_data
        )
        
        # Verify compatibility analysis
        self.assertIsNotNone(compatibility)
        self.assertIn("overall_score", compatibility)
        self.assertIn("aspect_scores", compatibility)
        self.assertGreaterEqual(compatibility["overall_score"], 0)
        self.assertLessEqual(compatibility["overall_score"], 1)

    @patch('artist_builder.artist_interface.LLMOrchestrator')
    def test_artist_evolution_with_legacy_profiles(self, mock_orchestrator):
        """Test artist evolution compatibility with legacy artist profiles."""
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "name": "Legacy Artist",
            "genre": {
                "main": "Electronic",
                "subgenres": ["Ambient", "Downtempo", "Chillwave"]
            },
            "style_tags": ["Atmospheric", "Melodic", "Experimental", "Dreamy"],
            "vibe": "An atmospheric electronic artist with melodic and dreamy elements",
            "target_audience": "Electronic music enthusiasts and meditation practitioners"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Evolve legacy artist
        result = self.interface.evolve_artist(
            artist_slug=self.legacy_artist_slug,
            evolution_strength=0.3,
            trend_sensitivity=0.5,
            target_aspects=["style", "vibe"],
            preserve_aspects=["genre", "name"]
        )
        
        # Verify evolution result
        self.assertIsNotNone(result)
        self.assertIn("new_version", result)
        self.assertIn("evolution_report", result)
        self.assertIn("artist_profile", result)
        
        # Check if profile was updated to latest schema
        evolved_profile = result["artist_profile"]
        self.assertIn("genre", evolved_profile)
        self.assertIsInstance(evolved_profile["genre"], dict)
        self.assertIn("style_tags", evolved_profile)
        self.assertIn("vibe", evolved_profile)
        self.assertIn("target_audience", evolved_profile)
        self.assertIn("metadata", evolved_profile)
        
        # Check if new version was created
        self.assertTrue(os.path.exists(os.path.join(
            self.temp_dir, "artists", self.legacy_artist_slug, "versions", f"profile_v{result['new_version']}.json"
        )))

    @patch('artist_builder.artist_analytics.TrendAnalyzer')
    def test_analytics_with_legacy_profiles(self, mock_trend_analyzer):
        """Test analytics compatibility with legacy artist profiles."""
        # Mock trend analyzer
        mock_trend_analyzer_instance = MagicMock()
        mock_trend_analyzer_instance.analyze_trends.return_value = {
            "trending_genres": ["Electronic", "Ambient", "Downtempo"],
            "trending_styles": ["Atmospheric", "Melodic", "Experimental"],
            "trending_topics": ["Nature", "Space", "Meditation"]
        }
        mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
            "overall_score": 0.8,
            "aspect_scores": {
                "genre": 0.9,
                "style": 0.7
            }
        }
        mock_trend_analyzer.return_value = mock_trend_analyzer_instance
        
        # Generate analytics for legacy artist
        report = self.analytics.generate_artist_analytics_report(
            artist_slug=self.legacy_artist_slug,
            report_type="comprehensive",
            time_period="all",
            output_format="json",
            save_report=True
        )
        
        # Verify report
        self.assertIsNotNone(report)
        self.assertIn("artist_slug", report)
        self.assertIn("report_type", report)
        self.assertIn("trend_analysis", report)
        self.assertIn("recommendations", report)
        
        # Check if report was saved
        self.assertIn("save_path", report)
        self.assertTrue(os.path.exists(report["save_path"]))

    def test_mixed_version_artist_comparison(self):
        """Test comparison between different schema version artists."""
        # Create directories for analytics
        os.makedirs(os.path.join(self.temp_dir, "analytics"), exist_ok=True)
        
        # Mock trend analyzer
        with patch('artist_builder.artist_analytics.TrendAnalyzer') as mock_trend_analyzer:
            mock_trend_analyzer_instance = MagicMock()
            mock_trend_analyzer_instance.analyze_trends.return_value = {}
            mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
                "overall_score": 0.7,
                "aspect_scores": {}
            }
            mock_trend_analyzer.return_value = mock_trend_analyzer_instance
            
            # Compare legacy and v2 artists
            comparison = self.analytics.compare_artists(
                artist_slugs=[self.legacy_artist_slug, self.v2_artist_slug],
                comparison_aspects=["genre", "style"],
                output_format="json",
                save_report=True
            )
            
            # Verify comparison
            self.assertIsNotNone(comparison)
            self.assertIn("artist_slugs", comparison)
            self.assertIn("comparison_aspects", comparison)
            self.assertIn("genre_comparison", comparison)
            self.assertIn("style_comparison", comparison)
            self.assertIn("comparison_summary", comparison)
            
            # Check if comparison was saved
            self.assertIn("save_path", comparison)
            self.assertTrue(os.path.exists(comparison["save_path"]))

    @patch('artist_builder.llm_collaboration.llm_collaboration.LLMOrchestrator')
    def test_llm_collaboration_with_legacy_profiles(self, mock_orchestrator):
        """Test LLM collaboration compatibility with legacy artist profiles."""
        # Mock LLM responses
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.side_effect = [
            "The artist should incorporate more ambient elements.",
            "The artist should explore more experimental sounds.",
            "The artist should blend ambient and experimental elements while maintaining the core electronic sound."
        ]
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Collaborative creation for legacy artist
        result = self.llm_collaboration.collaborative_create(
            params={
                "content_type": "artist_evolution",
                "artist_slug": self.legacy_artist_slug,
                "artist_profile": self.legacy_profile,
                "target_aspects": ["style", "sound"]
            },
            num_collaborators=2,
            iterations=1
        )
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIn("final_content", result)
        self.assertIn("iteration_history", result)

    def test_role_optimizer_with_legacy_tasks(self):
        """Test role optimizer compatibility with legacy task formats."""
        # Legacy task format
        legacy_task = {
            "type": "artist_creation",
            "genre": "Electronic",
            "style": ["Atmospheric", "Melodic", "Experimental"],
            "complexity": "medium"
        }
        
        # Get role assignment
        assignment = self.role_optimizer.assign_roles(legacy_task)
        
        # Verify assignment
        self.assertIsNotNone(assignment)
        self.assertIn("primary_role", assignment)
        self.assertIn("supporting_roles", assignment)
        self.assertIsInstance(assignment["supporting_roles"], list)

    def test_api_backward_compatibility(self):
        """Test backward compatibility of the API interfaces."""
        # Test with legacy parameter names
        with patch('artist_builder.artist_interface.ArtistProfileBuilder') as mock_builder:
            mock_builder_instance = MagicMock()
            mock_builder_instance.build_profile.return_value = {
                "name": "API Test Artist",
                "genre": {
                    "main": "Electronic",
                    "subgenres": ["Ambient", "Downtempo"]
                },
                "style_tags": ["Atmospheric", "Melodic", "Experimental"],
                "vibe": "An atmospheric electronic artist with melodic elements",
                "target_audience": "Electronic music enthusiasts"
            }
            mock_builder_instance.save_profile.return_value = "api-test-artist"
            mock_builder.return_value = mock_builder_instance
            
            # Call with legacy parameter names
            result = self.interface.create_artist(
                artist_name="API Test Artist",
                genre="Electronic",  # Legacy parameter name
                subgenres=["Ambient", "Downtempo"],  # Legacy parameter name
                style=["Atmospheric", "Melodic", "Experimental"],  # Legacy parameter name
                description="An atmospheric electronic artist with melodic elements",  # Legacy parameter name
                audience="Electronic music enthusiasts"  # Legacy parameter name
            )
            
            # Verify result
            self.assertIsNotNone(result)
            self.assertIn("artist_slug", result)
            self.assertIn("artist_profile", result)
            
            # Check parameter conversion
            mock_builder_instance.build_profile.assert_called_once()
            args, kwargs = mock_builder_instance.build_profile.call_args
            self.assertIn("main_genre", kwargs)
            self.assertIn("style_tags", kwargs)
            self.assertIn("vibe_description", kwargs)
            self.assertIn("target_audience", kwargs)


class TestFileSystemCompatibility(unittest.TestCase):
    """Test cases for file system compatibility with existing artist structures."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create legacy file structure
        self.legacy_artist_slug = "legacy-artist"
        os.makedirs(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "assets"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "songs"), exist_ok=True)
        
        # Create legacy profile
        self.legacy_profile = {
            "name": "Legacy Artist",
            "genre": "Electronic",
            "subgenres": ["Ambient", "Downtempo"],
            "style": ["Atmospheric", "Melodic", "Experimental"],
            "description": "An atmospheric electronic artist with melodic elements",
            "audience": "Electronic music enthusiasts",
            "created_at": "2024-01-15T12:00:00Z",
            "version": 1
        }
        
        with open(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "profile.json"), "w") as f:
            json.dump(self.legacy_profile, f)
        
        # Create legacy song file
        legacy_song = {
            "title": "Ethereal Journey",
            "lyrics": "Sample lyrics...",
            "created_at": "2024-01-20T12:00:00Z"
        }
        
        with open(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "songs", "ethereal_journey.json"), "w") as f:
            json.dump(legacy_song, f)
        
        # Initialize interface
        self.interface = ArtistCreationInterface(config={
            "artists_dir": os.path.join(self.temp_dir, "artists"),
            "analytics_dir": os.path.join(self.temp_dir, "analytics")
        })

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('artist_builder.artist_interface.LLMOrchestrator')
    def test_file_structure_preservation(self, mock_orchestrator):
        """Test preservation of existing file structure during evolution."""
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "name": "Legacy Artist",
            "genre": {
                "main": "Electronic",
                "subgenres": ["Ambient", "Downtempo", "Chillwave"]
            },
            "style_tags": ["Atmospheric", "Melodic", "Experimental", "Dreamy"],
            "vibe": "An atmospheric electronic artist with melodic and dreamy elements",
            "target_audience": "Electronic music enthusiasts and meditation practitioners"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Evolve legacy artist
        result = self.interface.evolve_artist(
            artist_slug=self.legacy_artist_slug,
            evolution_strength=0.3,
            trend_sensitivity=0.5,
            target_aspects=["style", "vibe"],
            preserve_aspects=["genre", "name"]
        )
        
        # Verify evolution result
        self.assertIsNotNone(result)
        
        # Check if legacy directories are preserved
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "assets")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "songs")))
        
        # Check if legacy files are preserved
        self.assertTrue(os.path.exists(os.path.join(
            self.temp_dir, "artists", self.legacy_artist_slug, "songs", "ethereal_journey.json"
        )))
        
        # Check if new directories are created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "versions")))

    @patch('artist_builder.artist_interface.LLMOrchestrator')
    def test_new_directory_creation(self, mock_orchestrator):
        """Test creation of new directories while preserving existing structure."""
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "name": "Legacy Artist",
            "genre": {
                "main": "Electronic",
                "subgenres": ["Ambient", "Downtempo", "Chillwave"]
            },
            "style_tags": ["Atmospheric", "Melodic", "Experimental", "Dreamy"],
            "vibe": "An atmospheric electronic artist with melodic and dreamy elements",
            "target_audience": "Electronic music enthusiasts and meditation practitioners"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Evolve legacy artist with new directories
        result = self.interface.evolve_artist(
            artist_slug=self.legacy_artist_slug,
            evolution_strength=0.3,
            trend_sensitivity=0.5,
            target_aspects=["style", "vibe"],
            preserve_aspects=["genre", "name"],
            create_directories=["prompts", "lyrics"]  # New directories to create
        )
        
        # Verify evolution result
        self.assertIsNotNone(result)
        
        # Check if legacy directories are preserved
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "assets")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "songs")))
        
        # Check if new directories are created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "prompts")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", self.legacy_artist_slug, "lyrics")))


class TestConfigurationCompatibility(unittest.TestCase):
    """Test cases for configuration compatibility."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "config"), exist_ok=True)
        
        # Create legacy configuration file
        self.legacy_config = {
            "artists_directory": os.path.join(self.temp_dir, "artists"),
            "llm_api_key": "test_api_key",
            "llm_model": "gpt-3.5-turbo",
            "log_level": "INFO"
        }
        
        with open(os.path.join(self.temp_dir, "config", "config.json"), "w") as f:
            json.dump(self.legacy_config, f)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('artist_builder.artist_interface.os.environ', {})
    def test_legacy_config_loading(self):
        """Test loading of legacy configuration format."""
        # Initialize interface with legacy config path
        with patch('artist_builder.artist_interface.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(self.legacy_config)
            
            interface = ArtistCreationInterface(config_path=os.path.join(self.temp_dir, "config", "config.json"))
            
            # Verify config loading
            self.assertEqual(interface.config.get("artists_dir"), self.legacy_config["artists_directory"])
            self.assertEqual(interface.config.get("llm_api_key"), self.legacy_config["llm_api_key"])
            self.assertEqual(interface.config.get("llm_model"), self.legacy_config["llm_model"])

    @patch('artist_builder.artist_interface.os.environ', {
        "NOKTVRN_ARTISTS_DIRECTORY": "/legacy/path/artists",
        "NOKTVRN_LLM_API_KEY": "legacy_api_key",
        "NOKTVRN_LLM_MODEL": "legacy-model"
    })
    def test_legacy_environment_variables(self):
        """Test loading of legacy environment variable names."""
        # Initialize interface
        interface = ArtistCreationInterface()
        
        # Verify environment variable loading
        self.assertEqual(interface.config.get("artists_dir"), "/legacy/path/artists")
        self.assertEqual(interface.config.get("llm_api_key"), "legacy_api_key")
        self.assertEqual(interface.config.get("llm_model"), "legacy-model")


if __name__ == '__main__':
    unittest.main()
