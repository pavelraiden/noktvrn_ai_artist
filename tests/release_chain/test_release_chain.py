#!/usr/bin/env python3

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, call
from datetime import datetime

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.append(PROJECT_ROOT)

# --- Module to test ---
# We need to modify sys.path *before* importing the module
RELEASE_CHAIN_DIR = os.path.join(PROJECT_ROOT, "release_chain")
if RELEASE_CHAIN_DIR not in sys.path:
    sys.path.insert(
        0, RELEASE_CHAIN_DIR
    )  # Prepend to ensure our module is found first

# Mock modules that might not be fully available or needed for unit tests
# Mock the actual schema module if it exists and causes issues, or mock its contents
# For simplicity, we will mock the classes directly in the release_chain module after import.

# Now import the module under test
import release_chain  # This should now find release_chain.py


# Mock the schema classes directly if needed for type hints or instantiation
# These mocks should be as close as possible to the real Pydantic models
class MockReleaseMetadata:
    def __init__(self, **kwargs):
        self.release_id = kwargs.get("release_id", "default_test_id")
        self.artist_name = kwargs.get("artist_name", "Default Test Artist")
        self.artist_id = kwargs.get("artist_id", "default_artist_id")
        self.genre = kwargs.get("genre", "test-genre")
        self.release_date = kwargs.get(
            "release_date",
            datetime.utcnow()
            .date()
            .isoformat(),  # Ensure it's date string as in implementation
        )
        self.track_title = kwargs.get("track_title", "Test Track")
        self.generation_run_id = kwargs.get(
            "generation_run_id", "default_run_id"
        )
        self.track_structure_summary = kwargs.get(
            "track_structure_summary", "Simulated Structure"
        )
        self.audio_file = kwargs.get("audio_file", "path/to/audio.mp3")
        self.video_file = kwargs.get("video_file", "path/to/video.mp4")
        self.cover_art_file = kwargs.get("cover_art_file", "path/to/cover.png")
        # Update with any other kwargs provided
        self.__dict__.update(kwargs)

    def model_dump_json(self, indent=None):
        # Convert datetime to string for JSON serialization if any datetime objects are present
        data = self.__dict__.copy()
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Path):
                data[key] = str(value)  # Ensure Paths are strings
        return json.dumps(data, indent=indent)


class MockPromptsUsed:
    def __init__(self, **kwargs):
        self.generation_run_id = kwargs.get(
            "generation_run_id", "default_run_id"
        )
        self.suno_prompt = kwargs.get("suno_prompt", "Default Suno Prompt")
        self.video_keywords = kwargs.get(
            "video_keywords", ["default", "keywords"]
        )
        self.cover_prompt = kwargs.get("cover_prompt", "Default Cover Prompt")
        self.__dict__.update(kwargs)

    def model_dump_json(self, indent=None):
        return json.dumps(self.__dict__, indent=indent)


# Apply mocks to the imported module *after* it has been imported
# This ensures that the module itself is loaded, and then we replace its attributes.
if hasattr(release_chain, "ReleaseMetadata"):
    release_chain.ReleaseMetadata = MockReleaseMetadata
if hasattr(release_chain, "PromptsUsed"):
    release_chain.PromptsUsed = MockPromptsUsed


class TestReleaseChain(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp(
            prefix="ai_artist_test_", dir=PROJECT_ROOT
        )  # Create in project root for visibility
        self.output_base_dir_orig = release_chain.OUTPUT_BASE_DIR
        self.releases_dir_orig = release_chain.RELEASES_DIR
        self.run_status_dir_orig = release_chain.RUN_STATUS_DIR
        self.release_log_file_orig = release_chain.RELEASE_LOG_FILE
        self.release_queue_file_orig = release_chain.RELEASE_QUEUE_FILE
        self.evolution_log_file_orig = release_chain.EVOLUTION_LOG_FILE

        # Override config paths in the module to use the temp dir
        release_chain.OUTPUT_BASE_DIR = self.test_dir
        release_chain.RELEASES_DIR = os.path.join(self.test_dir, "releases")
        release_chain.RUN_STATUS_DIR = os.path.join(
            self.test_dir, "run_status"
        )
        release_chain.RELEASE_LOG_FILE = os.path.join(
            self.test_dir, "release_log.md"
        )
        release_chain.RELEASE_QUEUE_FILE = os.path.join(
            self.test_dir, "release_queue.json"
        )
        release_chain.EVOLUTION_LOG_FILE = os.path.join(
            self.test_dir, "evolution_log.md"
        )

        # Ensure directories exist within the temp dir
        os.makedirs(release_chain.RELEASES_DIR, exist_ok=True)
        os.makedirs(release_chain.RUN_STATUS_DIR, exist_ok=True)
        os.makedirs(
            os.path.dirname(release_chain.EVOLUTION_LOG_FILE), exist_ok=True
        )

        # Create empty initial files
        with open(release_chain.RELEASE_LOG_FILE, "w") as f:
            f.write("")
        with open(release_chain.RELEASE_QUEUE_FILE, "w") as f:
            json.dump([], f)
        with open(release_chain.EVOLUTION_LOG_FILE, "w") as f:
            f.write("")

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir)
        # Restore original config paths
        release_chain.release_chain.OUTPUT_BASE_DIR = self.output_base_dir_orig
        release_chain.release_chain.RELEASES_DIR = self.releases_dir_orig
        release_chain.release_chain.RUN_STATUS_DIR = self.run_status_dir_orig
        release_chain.release_chain.RELEASE_LOG_FILE = (
            self.release_log_file_orig
        )
        release_chain.release_chain.RELEASE_QUEUE_FILE = (
            self.release_queue_file_orig
        )
        release_chain.release_chain.EVOLUTION_LOG_FILE = (
            self.evolution_log_file_orig
        )

    def test_generate_artist_slug(self):
        self.assertEqual(
            release_chain.generate_artist_slug("Synthwave Dreamer"),
            "synthwave_dreamer",
        )
        self.assertEqual(
            release_chain.generate_artist_slug("Artist Name!"), "artist_name"
        )
        self.assertEqual(
            release_chain.generate_artist_slug("  Multiple   Spaces  "),
            "multiple_spaces",
        )
        self.assertEqual(
            release_chain.generate_artist_slug(None), "unknown_artist"
        )
        self.assertEqual(
            release_chain.generate_artist_slug(""), "unknown_artist"
        )
        self.assertEqual(
            release_chain.generate_artist_slug("-!-@-"), "unknown_artist"
        )

    @patch("release_chain.Path.mkdir")
    def test_create_release_directory_success(self, mock_mkdir):
        artist_slug = "test_artist"
        date_str = "20250501"
        expected_path = (
            Path(release_chain.RELEASES_DIR) / f"{artist_slug}_{date_str}"
        )
        result_path = release_chain.create_release_directory(
            artist_slug, date_str
        )
        self.assertEqual(result_path, expected_path)
        calls = [
            call(parents=True, exist_ok=True),
            call(exist_ok=True),
            call(exist_ok=True),
            call(exist_ok=True),
        ]
        mock_mkdir.assert_has_calls(
            calls, any_order=False
        )  # Main dir, then audio, video, cover
        self.assertEqual(mock_mkdir.call_count, 4)

    @patch("release_chain.Path.mkdir", side_effect=OSError("Test error"))
    def test_create_release_directory_failure(self, mock_mkdir):
        artist_slug = "test_artist"
        date_str = "20250501"
        result_path = release_chain.create_release_directory(
            artist_slug, date_str
        )
        self.assertIsNone(result_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_metadata_file_success(self, mock_file):
        metadata = MockReleaseMetadata(
            release_id="test_123", artist_name="Test Artist"
        )
        filepath = Path(self.test_dir) / "metadata.json"
        success = release_chain.save_metadata_file(metadata, filepath)
        self.assertTrue(success)
        mock_file.assert_called_once_with(filepath, "w")
        written_content = mock_file().write.call_args[0][0]
        self.assertIn('"release_id": "test_123"', written_content)
        self.assertIn('"artist_name": "Test Artist"', written_content)

    @patch("builtins.open", side_effect=IOError("Test write error"))
    def test_save_metadata_file_failure(self, mock_file):
        metadata = MockReleaseMetadata(release_id="test_123")
        filepath = Path(self.test_dir) / "metadata.json"
        success = release_chain.save_metadata_file(metadata, filepath)
        self.assertFalse(success)

    @patch("builtins.open", new_callable=mock_open)
    def test_log_release_to_markdown_success(self, mock_file):
        metadata = MockReleaseMetadata(
            release_id="test_log_1",
            artist_name="Logger Artist",
            release_date="2025-05-01",
            genre="test-genre",
            track_title="Logging Track",
            generation_run_id="run_log_1",
        )
        release_dir_path = (
            Path(self.test_dir) / "releases" / "logger_artist_20250501"
        )
        success = release_chain.log_release_to_markdown(
            metadata, release_dir_path
        )
        self.assertTrue(success)
        mock_file.assert_called_once_with(release_chain.RELEASE_LOG_FILE, "a")
        written_content = mock_file().write.call_args[0][0]
        self.assertIn("### Release: test_log_1", written_content)
        self.assertIn("- **Artist:** Logger Artist", written_content)
        self.assertIn(
            f"- **Directory:** `{str(release_dir_path)}`", written_content
        )

    @patch("builtins.open", side_effect=IOError("Log write error"))
    def test_log_release_to_markdown_failure(self, mock_file):
        metadata = MockReleaseMetadata(release_id="test_log_fail")
        release_dir_path = (
            Path(self.test_dir) / "releases" / "fail_artist_20250501"
        )
        success = release_chain.log_release_to_markdown(
            metadata, release_dir_path
        )
        self.assertFalse(success)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load", return_value=[])
    @patch("json.dump")
    def test_add_release_to_queue_success_empty(
        self, mock_dump, mock_load, mock_file
    ):
        metadata = MockReleaseMetadata(
            release_id="test_q_1", artist_name="Queue Artist"
        )
        release_dir_path = (
            Path(self.test_dir) / "releases" / "queue_artist_20250501"
        )
        success = release_chain.add_release_to_queue(
            metadata, release_dir_path
        )
        self.assertTrue(success)
        mock_file.assert_any_call(release_chain.RELEASE_QUEUE_FILE, "r")
        mock_file.assert_any_call(release_chain.RELEASE_QUEUE_FILE, "w")
        mock_load.assert_called_once()
        mock_dump.assert_called_once()
        dumped_data = mock_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 1)
        self.assertEqual(dumped_data[0]["release_id"], "test_q_1")
        self.assertEqual(
            dumped_data[0]["release_directory"],
            str(release_dir_path.resolve()),
        )

    @patch("release_chain.create_release_directory")
    @patch("release_chain.download_asset", return_value=True)
    @patch("release_chain.generate_cover_art", return_value=True)
    @patch(
        "release_chain.analyze_track_structure", return_value="Mock Structure"
    )
    @patch("release_chain.get_prompts_from_run_data")
    @patch("release_chain.save_metadata_file", return_value=True)
    @patch("release_chain.save_prompts_file", return_value=True)
    @patch("release_chain.log_release_to_markdown", return_value=True)
    @patch("release_chain.add_release_to_queue", return_value=True)
    @patch("release_chain.create_feedback_placeholder", return_value=True)
    @patch(
        "release_chain.log_learning_entry", return_value=True
    )  # Mock new function
    def test_process_approved_run_success(
        self,
        mock_log_learning,
        mock_create_feedback,
        mock_add_queue,
        mock_log_md,
        mock_save_prompts,
        mock_save_meta,
        mock_get_prompts,
        mock_analyze_track,
        mock_gen_cover,
        mock_dl_asset,
        mock_create_dir,
    ):

        run_id = "proc_ok_1"
        artist_name = "Processor Artist"
        artist_id = "proc_artist_id_001"
        artist_slug = "processor_artist"
        # Use a fixed date_str for predictability, or ensure it matches what process_approved_run generates
        # The implementation now uses datetime.utcnow().strftime("%Y%m%d%H%M%S")
        # For testing, we might want to patch datetime.utcnow() or accept the generated one.
        # Let's assume we can predict it or verify based on the mock_create_dir call.

        mock_release_dir_name_part = f"{artist_slug}_"
        mock_release_dir = (
            Path(self.test_dir) / "releases" / "mock_release_subdir"
        )  # Placeholder
        mock_create_dir.return_value = mock_release_dir

        mock_prompts_obj = MockPromptsUsed(
            suno_prompt="p1",
            video_keywords=["k1"],
            cover_prompt="cp1",
            generation_run_id=run_id,
        )
        mock_get_prompts.return_value = (
            mock_prompts_obj  # Should return the model instance
        )

        run_data = {
            "run_id": run_id,
            "status": "approved",
            "artist_name": artist_name,
            "artist_id": artist_id,
            "track_url": "t_url",
            "video_url": "v_url",
            "genre": "synthwave",
            "track_title": "Galactic Dreams",
            # Add prompts directly if get_prompts_from_run_data is simple, or ensure mock_get_prompts handles it
            "suno_prompt": "p1",
            "video_keywords": ["k1"],
            "cover_prompt": "cp1",
        }
        run_status_filepath = (
            Path(release_chain.RUN_STATUS_DIR) / f"run_{run_id}.json"
        )
        with open(run_status_filepath, "w") as f:
            json.dump(run_data, f)

        success = release_chain.process_approved_run(run_id)
        self.assertTrue(success)

        mock_create_dir.assert_called_once()  # Called with artist_slug and a date_str
        # Verify the date_str format if possible, or that it was called.
        # Example: self.assertRegex(mock_create_dir.call_args[0][1], r"^\d{14}$")

        self.assertEqual(mock_dl_asset.call_count, 2)
        mock_gen_cover.assert_called_once()
        mock_analyze_track.assert_called_once()
        mock_get_prompts.assert_called_once_with(run_data)
        mock_save_meta.assert_called_once()
        mock_save_prompts.assert_called_once()
        mock_log_md.assert_called_once()
        mock_add_queue.assert_called_once()
        mock_create_feedback.assert_called_once()
        mock_log_learning.assert_called_once()

        saved_metadata_arg = mock_save_meta.call_args[0][0]
        self.assertIsInstance(
            saved_metadata_arg, MockReleaseMetadata
        )  # or release_chain.ReleaseMetadata if not mocked
        self.assertEqual(saved_metadata_arg.artist_name, artist_name)
        self.assertEqual(saved_metadata_arg.generation_run_id, run_id)
        self.assertEqual(saved_metadata_arg.track_structure, "Mock Structure")

        saved_prompts_arg = mock_save_prompts.call_args[0][0]
        self.assertIsInstance(
            saved_prompts_arg, MockPromptsUsed
        )  # or release_chain.PromptsUsed
        self.assertEqual(saved_prompts_arg.generation_run_id, run_id)
        self.assertEqual(saved_prompts_arg.suno_prompt, "p1")

    def test_process_approved_run_not_approved(self):
        run_id = "proc_not_appr"
        run_data = {"run_id": run_id, "status": "pending_approval"}
        run_status_filepath = (
            Path(release_chain.RUN_STATUS_DIR) / f"run_{run_id}.json"
        )
        with open(run_status_filepath, "w") as f:
            json.dump(run_data, f)
        success = release_chain.process_approved_run(run_id)
        self.assertFalse(success)

    def test_process_approved_run_no_status_file(self):
        run_id = "proc_no_file"
        success = release_chain.process_approved_run(run_id)
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
