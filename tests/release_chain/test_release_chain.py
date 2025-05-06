#!/usr/bin/env python3

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.append(PROJECT_ROOT)

# --- Module to test ---
# We need to modify sys.path *before* importing the module
RELEASE_CHAIN_DIR = os.path.join(PROJECT_ROOT, "release_chain")
sys.path.insert(
    0, RELEASE_CHAIN_DIR
)  # Prepend to ensure our module is found first

# Mock modules that might not be fully available or needed for unit tests
sys.modules["release_chain.schemas"] = MagicMock()

# Now import the module under test
import release_chain

# Restore sys.path if necessary (though usually not critical for tests)
# sys.path.pop(0)


# Mock the schema classes directly if needed for type hints or instantiation
class MockReleaseMetadata:
    def __init__(self, **kwargs):
        # Add default attributes expected by tests
        self.artist_name = kwargs.get("artist_name", "Default Test Artist")
        self.release_id = kwargs.get("release_id", "default_test_id")
        self.release_date = kwargs.get(
            "release_date", datetime.utcnow().isoformat()
        )
        self.genre = kwargs.get("genre", "test-genre")
        self.track_title = kwargs.get("track_title", "Test Track")
        self.generation_run_id = kwargs.get(
            "generation_run_id", "default_run_id"
        )
        self.track_structure_summary = kwargs.get(
            "track_structure_summary", None
        )
        # Update with any other kwargs provided
        self.__dict__.update(kwargs)

    def model_dump_json(self, indent=None):
        # Convert datetime to string for JSON serialization
        data = self.__dict__.copy()
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return json.dumps(data, indent=indent)


class MockPromptsUsed:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump_json(self, indent=None):
        return json.dumps(self.__dict__, indent=indent)


# Apply mocks to the imported module
release_chain.ReleaseMetadata = MockReleaseMetadata
release_chain.PromptsUsed = MockPromptsUsed


class TestReleaseChain(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp(dir=PROJECT_ROOT)
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
        # Ensure directories exist within the temp dir
        os.makedirs(release_chain.RELEASES_DIR, exist_ok=True)
        os.makedirs(release_chain.RUN_STATUS_DIR, exist_ok=True)
        # Create empty initial files
        with open(release_chain.RELEASE_LOG_FILE, "w") as f:
            f.write("")
        with open(release_chain.RELEASE_QUEUE_FILE, "w") as f:
            f.write("[]")

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

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
        # Check if mkdir was called for the main dir and subdirs
        self.assertEqual(
            mock_mkdir.call_count, 4
        )  # release_path, audio, video, cover
        mock_mkdir.assert_any_call(
            parents=True, exist_ok=True
        )  # For the main path
        mock_mkdir.assert_any_call(exist_ok=True)  # For subdirs

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
        mock_file().write.assert_called_once()
        # Check if the content written is valid JSON
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
            f"- **Directory:** `{release_dir_path}`", written_content
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
        # Check open calls: once for read, once for write
        self.assertEqual(mock_file.call_count, 2)
        mock_file.assert_any_call(release_chain.RELEASE_QUEUE_FILE, "r")
        mock_file.assert_any_call(release_chain.RELEASE_QUEUE_FILE, "w")

        # Check that json.load was called (even if file was empty initially)
        mock_load.assert_called_once()

        # Check that json.dump was called with the new entry
        mock_dump.assert_called_once()
        dumped_data = mock_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 1)
        self.assertEqual(dumped_data[0]["release_id"], "test_q_1")
        self.assertEqual(
            dumped_data[0]["release_directory"],
            str(release_dir_path.resolve()),
        )

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load", return_value=[{"release_id": "existing_1"}])
    @patch("json.dump")
    def test_add_release_to_queue_success_existing(
        self, mock_dump, mock_load, mock_file
    ):
        metadata = MockReleaseMetadata(
            release_id="test_q_2", artist_name="Queue Artist 2"
        )
        release_dir_path = (
            Path(self.test_dir) / "releases" / "queue_artist_2_20250501"
        )
        success = release_chain.add_release_to_queue(
            metadata, release_dir_path
        )

        self.assertTrue(success)
        mock_load.assert_called_once()
        mock_dump.assert_called_once()
        dumped_data = mock_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 2)
        self.assertEqual(dumped_data[0]["release_id"], "existing_1")
        self.assertEqual(dumped_data[1]["release_id"], "test_q_2")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load", side_effect=json.JSONDecodeError("bad json", "", 0))
    @patch("json.dump")
    def test_add_release_to_queue_decode_error(
        self, mock_dump, mock_load, mock_file
    ):
        # Test that it recovers from a bad JSON file and overwrites
        metadata = MockReleaseMetadata(release_id="test_q_3")
        release_dir_path = Path(self.test_dir) / "releases" / "q3"
        success = release_chain.add_release_to_queue(
            metadata, release_dir_path
        )
        self.assertTrue(success)
        mock_load.assert_called_once()
        mock_dump.assert_called_once()
        dumped_data = mock_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 1)
        self.assertEqual(dumped_data[0]["release_id"], "test_q_3")

    # --- Test process_approved_run (Integration-like unit test) --- #

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
    def test_process_approved_run_success(
        self,
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
        artist_slug = "processor_artist"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        release_id = f"{artist_slug}_{date_str}_{run_id[:4]}"
        mock_release_dir = (
            Path(self.test_dir) / "releases" / f"{artist_slug}_{date_str}"
        )
        mock_create_dir.return_value = mock_release_dir

        mock_prompts_dict = {"suno_prompt": "p1", "video_keywords": ["k1"]}
        mock_get_prompts.return_value = mock_prompts_dict

        # Create dummy run status file
        run_data = {
            "run_id": run_id,
            "status": "approved",
            "artist_name": artist_name,
            "track_url": "t_url",
            "video_url": "v_url",
        }
        run_status_filepath = (
            Path(release_chain.RUN_STATUS_DIR) / f"run_{run_id}.json"
        )
        with open(run_status_filepath, "w") as f:
            json.dump(run_data, f)

        success = release_chain.process_approved_run(run_id)

        self.assertTrue(success)
        mock_create_dir.assert_called_once_with(artist_slug, date_str)
        self.assertEqual(mock_dl_asset.call_count, 2)  # Audio and Video
        mock_gen_cover.assert_called_once()
        mock_analyze_track.assert_called_once()
        mock_get_prompts.assert_called_once_with(run_data)
        mock_save_meta.assert_called_once()
        mock_save_prompts.assert_called_once()
        mock_log_md.assert_called_once()
        mock_add_queue.assert_called_once()

        # Check metadata passed to save function
        saved_metadata = mock_save_meta.call_args[0][0]
        self.assertEqual(saved_metadata.release_id, release_id)
        self.assertEqual(saved_metadata.artist_name, artist_name)
        self.assertEqual(saved_metadata.generation_run_id, run_id)
        self.assertEqual(
            saved_metadata.track_structure_summary, "Mock Structure"
        )

        # Check prompts passed to save function
        saved_prompts = mock_save_prompts.call_args[0][0]
        self.assertEqual(saved_prompts.generation_run_id, run_id)
        self.assertEqual(saved_prompts.suno_prompt, "p1")

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

    @patch(
        "release_chain.create_release_directory", return_value=Path("mock/dir")
    )
    @patch(
        "release_chain.download_asset", return_value=False
    )  # Simulate asset download failure
    def test_process_approved_run_asset_failure(
        self, mock_dl_asset, mock_create_dir
    ):
        run_id = "proc_asset_fail"
        run_data = {
            "run_id": run_id,
            "status": "approved",
            "artist_name": "Fail Artist",
        }
        run_status_filepath = (
            Path(release_chain.RUN_STATUS_DIR) / f"run_{run_id}.json"
        )
        with open(run_status_filepath, "w") as f:
            json.dump(run_data, f)
        success = release_chain.process_approved_run(run_id)
        self.assertFalse(success)
        mock_dl_asset.assert_called()  # Ensure it was called


if __name__ == "__main__":
    unittest.main()
