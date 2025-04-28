"""
Test suite for the Artist Builder and Evolution System.

This module contains comprehensive tests for all components of the
Artist Builder and Evolution System, including trend analysis,
role optimization, LLM collaboration, and artist analytics.
"""

import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import components to test
from artist_builder.trend_analyzer.trend_collector import TrendCollector
from artist_builder.trend_analyzer.trend_processor import TrendProcessor
from artist_builder.trend_analyzer.artist_compatibility_analyzer import ArtistCompatibilityAnalyzer
from artist_builder.role_optimizer.role_dynamic_optimizer import RoleDynamicOptimizer
from artist_builder.llm_collaboration.llm_collaboration import LLMCollaboration
from artist_builder.llm_metrics.llm_efficiency_metrics import LLMMetrics
from artist_builder.artist_analytics import ArtistAnalytics
from artist_builder.artist_interface import ArtistCreationInterface

# Import from artist_creator module
from artist_creator.artist_profile_builder import ArtistProfileBuilder
from artist_creator.prompt_designer import PromptDesigner
from artist_creator.lyrics_generator import LyricsGenerator
from artist_creator.artist_creation_flow import ArtistCreationFlow


class TestTrendAnalyzer(unittest.TestCase):
    """Test cases for the Trend Analyzer components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.trend_collector = TrendCollector(config={"cache_dir": self.temp_dir})
        self.trend_processor = TrendProcessor()
        self.compatibility_analyzer = ArtistCompatibilityAnalyzer()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('artist_builder.trend_analyzer.trend_collector.requests.get')
    def test_trend_collection(self, mock_get):
        """Test trend collection from external sources."""
        # Mock response from external API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trends": {
                "genres": ["Pop", "Hip Hop", "Electronic"],
                "styles": ["Minimalist", "Lo-fi", "Ambient"],
                "topics": ["Climate", "Technology", "Relationships"]
            }
        }
        mock_get.return_value = mock_response

        # Test trend collection
        trends = self.trend_collector.collect_trends(source="test_source")
        
        # Verify results
        self.assertIn("genres", trends)
        self.assertIn("styles", trends)
        self.assertIn("topics", trends)
        self.assertEqual(len(trends["genres"]), 3)
        self.assertEqual(trends["genres"][0], "Pop")

    def test_trend_processing(self):
        """Test trend data processing."""
        # Sample raw trend data
        raw_trends = {
            "genres": ["Pop", "Hip Hop", "Electronic", "Pop", "Hip Hop"],
            "styles": ["Minimalist", "Lo-fi", "Ambient", "Lo-fi"],
            "topics": ["Climate", "Technology", "Relationships", "Climate"]
        }
        
        # Process trends
        processed_trends = self.trend_processor.process_trends(raw_trends)
        
        # Verify results
        self.assertIn("trending_genres", processed_trends)
        self.assertIn("trending_styles", processed_trends)
        self.assertIn("trending_topics", processed_trends)
        
        # Check frequency-based sorting
        self.assertEqual(processed_trends["trending_genres"][0], "Pop")
        self.assertEqual(processed_trends["trending_styles"][0], "Lo-fi")
        self.assertEqual(processed_trends["trending_topics"][0], "Climate")

    def test_artist_compatibility_analysis(self):
        """Test artist compatibility analysis with trends."""
        # Sample artist profile
        artist_profile = {
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing"
        }
        
        # Sample trend data
        trend_data = {
            "trending_genres": ["Pop", "Hip Hop", "Electronic"],
            "trending_styles": ["Minimalist", "Lo-fi", "Ambient"],
            "trending_topics": ["Climate", "Technology", "Relationships"]
        }
        
        # Analyze compatibility
        compatibility = self.compatibility_analyzer.analyze_compatibility(
            artist_profile=artist_profile,
            trend_data=trend_data
        )
        
        # Verify results
        self.assertIn("overall_score", compatibility)
        self.assertIn("aspect_scores", compatibility)
        self.assertGreaterEqual(compatibility["overall_score"], 0)
        self.assertLessEqual(compatibility["overall_score"], 1)
        self.assertIn("genre", compatibility["aspect_scores"])
        self.assertIn("style", compatibility["aspect_scores"])


class TestRoleOptimizer(unittest.TestCase):
    """Test cases for the Role Optimizer component."""

    def setUp(self):
        """Set up test environment."""
        self.role_optimizer = RoleDynamicOptimizer()

    def test_role_template_creation(self):
        """Test creation of role templates."""
        # Create a custom role template
        role_template = {
            "name": "TestRole",
            "description": "A test role",
            "prompt_template": "You are a test role...",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        # Register the role
        self.role_optimizer.register_role("test_role", role_template)
        
        # Verify registration
        self.assertIn("test_role", self.role_optimizer.get_available_roles())
        retrieved_template = self.role_optimizer.get_role_template("test_role")
        self.assertEqual(retrieved_template["name"], "TestRole")

    def test_role_assignment(self):
        """Test dynamic role assignment based on task."""
        # Sample task
        task = {
            "type": "lyrics_generation",
            "genre": "Pop",
            "complexity": "high",
            "length": "medium"
        }
        
        # Get role assignment
        assignment = self.role_optimizer.assign_roles(task)
        
        # Verify assignment
        self.assertIsNotNone(assignment)
        self.assertIn("primary_role", assignment)
        self.assertIn("supporting_roles", assignment)
        self.assertIsInstance(assignment["supporting_roles"], list)

    def test_role_performance_tracking(self):
        """Test tracking of role performance."""
        # Sample performance data
        performance_data = {
            "role": "test_role",
            "task_type": "lyrics_generation",
            "success": True,
            "quality_score": 0.85,
            "execution_time": 2.3,
            "token_usage": 320
        }
        
        # Track performance
        self.role_optimizer.track_performance(performance_data)
        
        # Get performance metrics
        metrics = self.role_optimizer.get_role_performance("test_role")
        
        # Verify metrics
        self.assertIsNotNone(metrics)
        self.assertIn("success_rate", metrics)
        self.assertIn("avg_quality_score", metrics)
        self.assertIn("avg_execution_time", metrics)
        self.assertIn("avg_token_usage", metrics)


class TestLLMCollaboration(unittest.TestCase):
    """Test cases for the LLM Collaboration component."""

    def setUp(self):
        """Set up test environment."""
        self.llm_collaboration = LLMCollaboration()

    @patch('artist_builder.llm_collaboration.llm_collaboration.LLMOrchestrator')
    def test_peer_review(self, mock_orchestrator):
        """Test peer review mechanism."""
        # Mock LLM responses
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.side_effect = [
            "The lyrics are excellent but could use more emotional depth.",
            "The chorus is catchy but repetitive. Consider adding variation."
        ]
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Content to review
        content = {
            "type": "lyrics",
            "content": "Sample lyrics for testing...",
            "metadata": {
                "genre": "Pop",
                "theme": "Love"
            }
        }
        
        # Perform peer review
        review_results = self.llm_collaboration.peer_review(
            content=content,
            review_aspects=["quality", "originality"],
            num_reviewers=2
        )
        
        # Verify results
        self.assertIsNotNone(review_results)
        self.assertIn("reviews", review_results)
        self.assertIn("consensus", review_results)
        self.assertEqual(len(review_results["reviews"]), 2)

    @patch('artist_builder.llm_collaboration.llm_collaboration.LLMOrchestrator')
    def test_collaborative_creation(self, mock_orchestrator):
        """Test collaborative content creation."""
        # Mock LLM responses
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.side_effect = [
            "Initial draft of content...",
            "Suggested improvements: add more detail about...",
            "Final version with improvements incorporated..."
        ]
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Creation parameters
        params = {
            "content_type": "artist_bio",
            "genre": "Electronic",
            "style": "Experimental",
            "influences": ["Artist1", "Artist2"]
        }
        
        # Perform collaborative creation
        result = self.llm_collaboration.collaborative_create(
            params=params,
            num_collaborators=2,
            iterations=2
        )
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIn("final_content", result)
        self.assertIn("iteration_history", result)
        self.assertEqual(len(result["iteration_history"]), 2)

    @patch('artist_builder.llm_collaboration.llm_collaboration.LLMOrchestrator')
    def test_conflict_resolution(self, mock_orchestrator):
        """Test conflict resolution between LLMs."""
        # Mock LLM responses
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.side_effect = [
            "The artist should focus on electronic music.",
            "The artist should focus on acoustic music.",
            "The artist should blend electronic and acoustic elements."
        ]
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Conflicting suggestions
        suggestions = [
            "The artist should focus on electronic music.",
            "The artist should focus on acoustic music."
        ]
        
        # Resolve conflict
        resolution = self.llm_collaboration.resolve_conflict(
            suggestions=suggestions,
            context={
                "artist_name": "Test Artist",
                "current_genre": "Pop"
            }
        )
        
        # Verify resolution
        self.assertIsNotNone(resolution)
        self.assertIn("resolved_suggestion", resolution)
        self.assertIn("resolution_method", resolution)


class TestLLMMetrics(unittest.TestCase):
    """Test cases for the LLM Metrics component."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.llm_metrics = LLMMetrics(config={"metrics_dir": self.temp_dir})

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_track_interaction(self):
        """Test tracking of LLM interactions."""
        # Sample interaction data
        interaction = {
            "artist_id": "test-artist",
            "module": "lyrics_generator",
            "operation": "generate_lyrics",
            "prompt_tokens": 150,
            "completion_tokens": 300,
            "duration_ms": 1200,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Track interaction
        interaction_id = self.llm_metrics.track_interaction(interaction)
        
        # Verify tracking
        self.assertIsNotNone(interaction_id)
        retrieved = self.llm_metrics.get_interaction(interaction_id)
        self.assertEqual(retrieved["artist_id"], "test-artist")
        self.assertEqual(retrieved["module"], "lyrics_generator")

    def test_calculate_efficiency_metrics(self):
        """Test calculation of efficiency metrics."""
        # Sample interactions
        interactions = [
            {
                "artist_id": "test-artist",
                "module": "lyrics_generator",
                "operation": "generate_lyrics",
                "prompt_tokens": 150,
                "completion_tokens": 300,
                "duration_ms": 1200,
                "success": True,
                "timestamp": datetime.now().isoformat()
            },
            {
                "artist_id": "test-artist",
                "module": "lyrics_generator",
                "operation": "generate_lyrics",
                "prompt_tokens": 180,
                "completion_tokens": 350,
                "duration_ms": 1500,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Track interactions
        for interaction in interactions:
            self.llm_metrics.track_interaction(interaction)
        
        # Calculate metrics
        metrics = self.llm_metrics.calculate_efficiency_metrics(
            artist_id="test-artist",
            module="lyrics_generator"
        )
        
        # Verify metrics
        self.assertIsNotNone(metrics)
        self.assertIn("total_interactions", metrics)
        self.assertIn("avg_prompt_tokens", metrics)
        self.assertIn("avg_completion_tokens", metrics)
        self.assertIn("avg_duration_ms", metrics)
        self.assertIn("success_rate", metrics)
        self.assertEqual(metrics["total_interactions"], 2)
        self.assertEqual(metrics["success_rate"], 1.0)


class TestArtistAnalytics(unittest.TestCase):
    """Test cases for the Artist Analytics component."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "artists/test-artist"), exist_ok=True)
        
        # Create sample artist profile
        profile = {
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": 1
            }
        }
        
        with open(os.path.join(self.temp_dir, "artists/test-artist/profile.json"), "w") as f:
            json.dump(profile, f)
        
        # Create version history
        os.makedirs(os.path.join(self.temp_dir, "artists/test-artist/versions"), exist_ok=True)
        
        # Version 1
        with open(os.path.join(self.temp_dir, "artists/test-artist/versions/profile_v1.json"), "w") as f:
            json.dump(profile, f)
        
        # Version 2
        profile_v2 = profile.copy()
        profile_v2["style_tags"] = ["Minimalist", "Upbeat", "Melodic", "Electronic"]
        profile_v2["metadata"]["version"] = 2
        profile_v2["metadata"]["evolved_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        
        with open(os.path.join(self.temp_dir, "artists/test-artist/versions/profile_v2.json"), "w") as f:
            json.dump(profile_v2, f)
        
        # Initialize analytics
        self.analytics = ArtistAnalytics(config={
            "artists_dir": os.path.join(self.temp_dir, "artists"),
            "analytics_dir": os.path.join(self.temp_dir, "analytics")
        })

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('artist_builder.artist_analytics.TrendAnalyzer')
    @patch('artist_builder.artist_analytics.LLMMetrics')
    def test_generate_analytics_report(self, mock_metrics, mock_trend_analyzer):
        """Test generation of analytics report."""
        # Mock trend analyzer
        mock_trend_analyzer_instance = MagicMock()
        mock_trend_analyzer_instance.analyze_trends.return_value = {
            "trending_genres": ["Pop", "Hip Hop", "Electronic"],
            "trending_styles": ["Minimalist", "Lo-fi", "Ambient"]
        }
        mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
            "overall_score": 0.75,
            "aspect_scores": {
                "genre": 0.8,
                "style": 0.7
            }
        }
        mock_trend_analyzer.return_value = mock_trend_analyzer_instance
        
        # Mock metrics
        mock_metrics_instance = MagicMock()
        mock_metrics_instance.get_artist_efficiency_metrics.return_value = {
            "total_interactions": 10,
            "avg_prompt_tokens": 150,
            "avg_completion_tokens": 300,
            "avg_duration_ms": 1200,
            "success_rate": 0.9
        }
        mock_metrics_instance.get_interactions.return_value = []
        mock_metrics.return_value = mock_metrics_instance
        
        # Generate report
        report = self.analytics.generate_artist_analytics_report(
            artist_slug="test-artist",
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
        self.assertIn("performance_metrics", report)
        self.assertIn("evolution_tracking", report)
        self.assertIn("audience_insights", report)
        self.assertIn("recommendations", report)
        
        # Check if report was saved
        self.assertIn("save_path", report)
        self.assertTrue(os.path.exists(report["save_path"]))

    @patch('artist_builder.artist_analytics.TrendAnalyzer')
    @patch('artist_builder.artist_analytics.LLMMetrics')
    def test_compare_artists(self, mock_metrics, mock_trend_analyzer):
        """Test artist comparison."""
        # Create another test artist
        os.makedirs(os.path.join(self.temp_dir, "artists/test-artist2"), exist_ok=True)
        
        profile2 = {
            "name": "Test Artist 2",
            "genre": {
                "main": "Electronic",
                "subgenres": ["Techno", "Ambient"]
            },
            "style_tags": ["Experimental", "Dark", "Atmospheric"],
            "vibe": "Mysterious and introspective",
            "target_audience": "Electronic music enthusiasts",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": 1
            }
        }
        
        with open(os.path.join(self.temp_dir, "artists/test-artist2/profile.json"), "w") as f:
            json.dump(profile2, f)
        
        # Mock trend analyzer
        mock_trend_analyzer_instance = MagicMock()
        mock_trend_analyzer_instance.analyze_trends.return_value = {}
        mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
            "overall_score": 0.7,
            "aspect_scores": {}
        }
        mock_trend_analyzer.return_value = mock_trend_analyzer_instance
        
        # Mock metrics
        mock_metrics_instance = MagicMock()
        mock_metrics_instance.get_artist_efficiency_metrics.return_value = {}
        mock_metrics_instance.get_interactions.return_value = []
        mock_metrics.return_value = mock_metrics_instance
        
        # Compare artists
        comparison = self.analytics.compare_artists(
            artist_slugs=["test-artist", "test-artist2"],
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

    @patch('artist_builder.artist_analytics.TrendAnalyzer')
    @patch('artist_builder.artist_analytics.LLMMetrics')
    def test_track_artist_evolution(self, mock_metrics, mock_trend_analyzer):
        """Test tracking of artist evolution."""
        # Mock trend analyzer
        mock_trend_analyzer_instance = MagicMock()
        mock_trend_analyzer_instance.analyze_trends.return_value = {}
        mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
            "overall_score": 0.7,
            "aspect_scores": {}
        }
        mock_trend_analyzer.return_value = mock_trend_analyzer_instance
        
        # Mock metrics
        mock_metrics_instance = MagicMock()
        mock_metrics_instance.get_artist_efficiency_metrics.return_value = {}
        mock_metrics_instance.get_interactions.return_value = []
        mock_metrics.return_value = mock_metrics_instance
        
        # Track evolution
        evolution = self.analytics.track_artist_evolution(
            artist_slug="test-artist",
            track_period="all",
            include_metrics=True,
            include_trends=True,
            output_format="json",
            save_report=True
        )
        
        # Verify evolution tracking
        self.assertIsNotNone(evolution)
        self.assertIn("artist_slug", evolution)
        self.assertIn("track_period", evolution)
        self.assertIn("version_history", evolution)
        self.assertIn("evolution_timeline", evolution)
        
        # Check version history
        self.assertEqual(len(evolution["version_history"]), 2)
        
        # Check if report was saved
        self.assertIn("save_path", evolution)
        self.assertTrue(os.path.exists(evolution["save_path"]))


class TestArtistCreationInterface(unittest.TestCase):
    """Test cases for the Artist Creation Interface."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "artists"), exist_ok=True)
        
        # Initialize interface
        self.interface = ArtistCreationInterface(config={
            "artists_dir": os.path.join(self.temp_dir, "artists"),
            "analytics_dir": os.path.join(self.temp_dir, "analytics")
        })

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('artist_builder.artist_interface.LLMOrchestrator')
    @patch('artist_builder.artist_interface.TrendAnalyzer')
    def test_create_artist(self, mock_trend_analyzer, mock_orchestrator):
        """Test artist creation through the interface."""
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Mock trend analyzer
        mock_trend_analyzer_instance = MagicMock()
        mock_trend_analyzer_instance.analyze_trends.return_value = {}
        mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
            "overall_score": 0.7,
            "aspect_scores": {}
        }
        mock_trend_analyzer.return_value = mock_trend_analyzer_instance
        
        # Create artist
        result = self.interface.create_artist(
            artist_name="Test Artist",
            main_genre="Pop",
            subgenres=["Synth-pop", "Dance-pop"],
            style_tags=["Minimalist", "Upbeat", "Melodic"],
            vibe_description="Energetic and optimistic",
            target_audience="Young adults who enjoy dancing"
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("artist_slug", result)
        self.assertIn("artist_profile", result)
        self.assertIn("creation_report", result)
        
        # Check if artist directory was created
        artist_slug = result["artist_slug"]
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", artist_slug)))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "artists", artist_slug, "profile.json")))

    @patch('artist_builder.artist_interface.LLMOrchestrator')
    @patch('artist_builder.artist_interface.TrendAnalyzer')
    def test_evolve_artist(self, mock_trend_analyzer, mock_orchestrator):
        """Test artist evolution through the interface."""
        # Create test artist
        artist_slug = "test-artist"
        os.makedirs(os.path.join(self.temp_dir, "artists", artist_slug), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "artists", artist_slug, "versions"), exist_ok=True)
        
        # Create profile
        profile = {
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": 1
            }
        }
        
        with open(os.path.join(self.temp_dir, "artists", artist_slug, "profile.json"), "w") as f:
            json.dump(profile, f)
        
        with open(os.path.join(self.temp_dir, "artists", artist_slug, "versions", "profile_v1.json"), "w") as f:
            json.dump(profile, f)
        
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop", "Electropop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic", "Electronic"],
            "vibe": "Energetic and futuristic",
            "target_audience": "Young adults who enjoy electronic dance music"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Mock trend analyzer
        mock_trend_analyzer_instance = MagicMock()
        mock_trend_analyzer_instance.analyze_trends.return_value = {
            "trending_genres": ["Pop", "Electronic", "Hip Hop"],
            "trending_styles": ["Electronic", "Minimalist", "Lo-fi"]
        }
        mock_trend_analyzer_instance.analyze_artist_compatibility.return_value = {
            "overall_score": 0.7,
            "aspect_scores": {}
        }
        mock_trend_analyzer.return_value = mock_trend_analyzer_instance
        
        # Evolve artist
        result = self.interface.evolve_artist(
            artist_slug=artist_slug,
            evolution_strength=0.5,
            trend_sensitivity=0.7,
            target_aspects=["style", "vibe"],
            preserve_aspects=["genre", "name"]
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("new_version", result)
        self.assertIn("evolution_report", result)
        self.assertIn("artist_profile", result)
        
        # Check if new version was created
        self.assertEqual(result["new_version"], 2)
        self.assertTrue(os.path.exists(os.path.join(
            self.temp_dir, "artists", artist_slug, "versions", "profile_v2.json"
        )))
        
        # Check if profile was updated
        with open(os.path.join(self.temp_dir, "artists", artist_slug, "profile.json"), "r") as f:
            updated_profile = json.load(f)
        
        self.assertEqual(updated_profile["metadata"]["version"], 2)


class TestArtistCreator(unittest.TestCase):
    """Test cases for the Artist Creator components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "artists"), exist_ok=True)
        
        # Initialize components
        self.profile_builder = ArtistProfileBuilder(config={"artists_dir": os.path.join(self.temp_dir, "artists")})
        self.prompt_designer = PromptDesigner(config={"artists_dir": os.path.join(self.temp_dir, "artists")})
        self.lyrics_generator = LyricsGenerator(config={"artists_dir": os.path.join(self.temp_dir, "artists")})
        self.creation_flow = ArtistCreationFlow(config={"artists_dir": os.path.join(self.temp_dir, "artists")})

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('artist_creator.artist_profile_builder.LLMOrchestrator')
    def test_profile_building(self, mock_orchestrator):
        """Test artist profile building."""
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Build profile
        profile = self.profile_builder.build_profile(
            artist_name="Test Artist",
            main_genre="Pop",
            subgenres=["Synth-pop", "Dance-pop"],
            style_tags=["Minimalist", "Upbeat", "Melodic"],
            vibe_description="Energetic and optimistic",
            target_audience="Young adults who enjoy dancing"
        )
        
        # Verify profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], "Test Artist")
        self.assertEqual(profile["genre"]["main"], "Pop")
        self.assertIn("Synth-pop", profile["genre"]["subgenres"])
        self.assertIn("Minimalist", profile["style_tags"])
        self.assertEqual(profile["vibe"], "Energetic and optimistic")
        self.assertEqual(profile["target_audience"], "Young adults who enjoy dancing")

    @patch('artist_creator.prompt_designer.LLMOrchestrator')
    def test_prompt_design(self, mock_orchestrator):
        """Test prompt design for an artist."""
        # Create test artist
        artist_slug = "test-artist"
        os.makedirs(os.path.join(self.temp_dir, "artists", artist_slug), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "artists", artist_slug, "prompts"), exist_ok=True)
        
        # Create profile
        profile = {
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing"
        }
        
        with open(os.path.join(self.temp_dir, "artists", artist_slug, "profile.json"), "w") as f:
            json.dump(profile, f)
        
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = json.dumps({
            "title": "Summer Nights",
            "theme": "Carefree summer evenings",
            "mood": "Nostalgic yet upbeat",
            "key_elements": [
                "Dancing under the stars",
                "Warm summer breeze",
                "Memories with friends"
            ],
            "musical_direction": "Upbeat synth-pop with a nostalgic touch"
        })
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Design prompt
        prompt = self.prompt_designer.design_song_prompt(
            artist_slug=artist_slug,
            prompt_type="song",
            theme="summer",
            additional_context="Focus on nostalgic feelings"
        )
        
        # Verify prompt
        self.assertIsNotNone(prompt)
        self.assertIn("title", prompt)
        self.assertIn("theme", prompt)
        self.assertIn("mood", prompt)
        self.assertIn("key_elements", prompt)
        self.assertIn("musical_direction", prompt)
        
        # Check if prompt was saved
        prompt_files = os.listdir(os.path.join(self.temp_dir, "artists", artist_slug, "prompts"))
        self.assertGreaterEqual(len(prompt_files), 1)

    @patch('artist_creator.lyrics_generator.LLMOrchestrator')
    def test_lyrics_generation(self, mock_orchestrator):
        """Test lyrics generation for an artist."""
        # Create test artist
        artist_slug = "test-artist"
        os.makedirs(os.path.join(self.temp_dir, "artists", artist_slug), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "artists", artist_slug, "lyrics"), exist_ok=True)
        
        # Create profile
        profile = {
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing"
        }
        
        with open(os.path.join(self.temp_dir, "artists", artist_slug, "profile.json"), "w") as f:
            json.dump(profile, f)
        
        # Create prompt
        prompt = {
            "title": "Summer Nights",
            "theme": "Carefree summer evenings",
            "mood": "Nostalgic yet upbeat",
            "key_elements": [
                "Dancing under the stars",
                "Warm summer breeze",
                "Memories with friends"
            ],
            "musical_direction": "Upbeat synth-pop with a nostalgic touch"
        }
        
        # Mock LLM orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.generate_response.return_value = """
        [Verse 1]
        Warm breeze on my skin
        City lights begin to dim
        Friends gather 'round
        No better feeling to be found
        
        [Chorus]
        Summer nights, under the stars
        Dancing till dawn, no matter how far
        Summer nights, memories made
        In these moments, we'll always stay
        """
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Generate lyrics
        lyrics = self.lyrics_generator.generate_lyrics(
            artist_slug=artist_slug,
            prompt=prompt,
            structure=["verse", "chorus", "verse", "chorus", "bridge", "chorus"]
        )
        
        # Verify lyrics
        self.assertIsNotNone(lyrics)
        self.assertIn("Verse", lyrics)
        self.assertIn("Chorus", lyrics)
        
        # Check if lyrics were saved
        lyrics_files = os.listdir(os.path.join(self.temp_dir, "artists", artist_slug, "lyrics"))
        self.assertGreaterEqual(len(lyrics_files), 1)

    @patch('artist_creator.artist_creation_flow.ArtistProfileBuilder')
    @patch('artist_creator.artist_creation_flow.PromptDesigner')
    @patch('artist_creator.artist_creation_flow.LyricsGenerator')
    def test_full_creation_flow(self, mock_lyrics_generator, mock_prompt_designer, mock_profile_builder):
        """Test the full artist creation flow."""
        # Mock profile builder
        mock_profile_builder_instance = MagicMock()
        mock_profile_builder_instance.build_profile.return_value = {
            "name": "Test Artist",
            "genre": {
                "main": "Pop",
                "subgenres": ["Synth-pop", "Dance-pop"]
            },
            "style_tags": ["Minimalist", "Upbeat", "Melodic"],
            "vibe": "Energetic and optimistic",
            "target_audience": "Young adults who enjoy dancing"
        }
        mock_profile_builder_instance.save_profile.return_value = "test-artist"
        mock_profile_builder.return_value = mock_profile_builder_instance
        
        # Mock prompt designer
        mock_prompt_designer_instance = MagicMock()
        mock_prompt_designer_instance.design_song_prompt.return_value = {
            "title": "Summer Nights",
            "theme": "Carefree summer evenings",
            "mood": "Nostalgic yet upbeat",
            "key_elements": [
                "Dancing under the stars",
                "Warm summer breeze",
                "Memories with friends"
            ],
            "musical_direction": "Upbeat synth-pop with a nostalgic touch"
        }
        mock_prompt_designer.return_value = mock_prompt_designer_instance
        
        # Mock lyrics generator
        mock_lyrics_generator_instance = MagicMock()
        mock_lyrics_generator_instance.generate_lyrics.return_value = """
        [Verse 1]
        Warm breeze on my skin
        City lights begin to dim
        
        [Chorus]
        Summer nights, under the stars
        Dancing till dawn, no matter how far
        """
        mock_lyrics_generator.return_value = mock_lyrics_generator_instance
        
        # Run full creation flow
        result = self.creation_flow.run_full_artist_creation_flow(
            artist_name="Test Artist",
            main_genre="Pop",
            subgenres=["Synth-pop", "Dance-pop"],
            style_tags=["Minimalist", "Upbeat", "Melodic"],
            vibe_description="Energetic and optimistic",
            target_audience="Young adults who enjoy dancing"
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("artist_slug", result)
        self.assertIn("artist_profile", result)
        self.assertIn("prompts", result)
        self.assertIn("lyrics", result)
        self.assertEqual(result["artist_slug"], "test-artist")


if __name__ == '__main__':
    unittest.main()
