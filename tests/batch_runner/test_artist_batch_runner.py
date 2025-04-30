#!/usr/bin/env python3

import unittest
import os
import sys
import json
import time
import shutil
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime

# --- Add project root to sys.path for imports ---
# Adjust path based on where tests are run from
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..")) # Add ai_artist_system root
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", "batch_runner")) # Add batch_runner dir
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", "streamlit_app")) # Add streamlit_app dir

# Import the script to be tested
# We need to mock imports within the script *before* importing it if they cause issues
# For now, assume imports work or are handled by placeholders
import artist_batch_runner

# --- Test Class --- #

class TestArtistBatchRunner(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directories for testing file operations
        self.test_output_dir = os.path.join(os.path.dirname(__file__), "test_output")
        self.test_run_status_dir = os.path.join(self.test_output_dir, "run_status")
        os.makedirs(self.test_run_status_dir, exist_ok=True)

        # Override the directories used by the script
        artist_batch_runner.OUTPUT_DIR = self.test_output_dir
        artist_batch_runner.RUN_STATUS_DIR = self.test_run_status_dir
        
        # Reset any global state if necessary (e.g., logging setup)
        # For simplicity, we assume logging setup is idempotent

        # Mock external dependencies that are always called
        self.patcher_select_artist = patch("artist_batch_runner.select_next_artist")
        self.mock_select_artist = self.patcher_select_artist.start()
        self.mock_select_artist.return_value = {"artist_id": 99, "name": "Test Artist", "genre": "testwave"}

        self.patcher_get_params = patch("artist_batch_runner.get_adapted_parameters")
        self.mock_get_params = self.patcher_get_params.start()
        self.mock_get_params.return_value = {"suno_prompt": "test", "video_keywords": ["test"]}

        self.patcher_gen_track = patch("artist_batch_runner.generate_track")
        self.mock_gen_track = self.patcher_gen_track.start()
        self.mock_gen_track.return_value = {"track_id": "t123", "track_url": "http://fake-track"}

        self.patcher_sel_video = patch("artist_batch_runner.select_video")
        self.mock_sel_video = self.patcher_sel_video.start()
        self.mock_sel_video.return_value = {"video_url": "http://fake-video", "source": "test-src"}

        self.patcher_send_telegram = patch("artist_batch_runner.send_to_telegram_for_approval")
        self.mock_send_telegram = self.patcher_send_telegram.start()
        self.mock_send_telegram.return_value = True

        self.patcher_check_approval = patch("artist_batch_runner.check_approval_status")
        self.mock_check_approval = self.patcher_check_approval.start()
        # Default to approved after first check
        self.mock_check_approval.side_effect = [None, True] 

        self.patcher_save_content = patch("artist_batch_runner.save_approved_content")
        self.mock_save_content = self.patcher_save_content.start()
        self.mock_save_content.return_value = True

        self.patcher_trigger_release = patch("artist_batch_runner.trigger_release_logic")
        self.mock_trigger_release = self.patcher_trigger_release.start()
        
        self.patcher_time_sleep = patch("time.sleep") # Mock sleep to speed up tests
        self.mock_time_sleep = self.patcher_time_sleep.start()
        
        self.patcher_time_time = patch("time.time")
        self.mock_time_time = self.patcher_time_time.start()
        # Simulate time passing during polling
        self.mock_time_time.side_effect = [1000.0, 1000.0, 1005.0, 1010.0] # Start, check 1, check 2

    def tearDown(self):
        """Clean up test environment after each test."""
        # Stop all patchers
        self.patcher_select_artist.stop()
        self.patcher_get_params.stop()
        self.patcher_gen_track.stop()
        self.patcher_sel_video.stop()
        self.patcher_send_telegram.stop()
        self.patcher_check_approval.stop()
        self.patcher_save_content.stop()
        self.patcher_trigger_release.stop()
        self.patcher_time_sleep.stop()
        self.patcher_time_time.stop()

        # Remove temporary directories
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    # --- Individual Function Tests --- #

    def test_create_initial_run_status(self):
        """Test creating the initial status file."""
        run_id = "test001"
        artist = {"artist_id": 1, "name": "A"}
        track = {"track_id": "t1", "track_url": "url_t"}
        video = {"video_url": "url_v", "source": "s"}
        
        with patch("builtins.open", mock_open()) as mock_file:
            result = artist_batch_runner.create_initial_run_status(run_id, artist, track, video)
            
            self.assertTrue(result)
            mock_file.assert_called_once_with(os.path.join(self.test_run_status_dir, f"run_{run_id}.json"), "w")
            # Check if json.dump was called with the correct data structure (simplified check)
            args, kwargs = mock_file().write.call_args
            written_data = json.loads(args[0])
            self.assertEqual(written_data["run_id"], run_id)
            self.assertEqual(written_data["status"], "pending_approval")
            self.assertEqual(written_data["artist_id"], 1)
            self.assertEqual(written_data["track_url"], "url_t")
            self.assertEqual(written_data["video_url"], "url_v")

    def test_update_run_status(self):
        """Test updating an existing status file."""
        run_id = "test002"
        initial_path = os.path.join(self.test_run_status_dir, f"run_{run_id}.json")
        initial_data = {"run_id": run_id, "status": "pending_approval", "created_at": "sometime"}
        with open(initial_path, "w") as f:
            json.dump(initial_data, f)
            
        artist_batch_runner.update_run_status(run_id, "approved", "User approved")
        
        with open(initial_path, "r") as f:
            updated_data = json.load(f)
            
        self.assertEqual(updated_data["status"], "approved")
        self.assertEqual(updated_data["final_status_reason"], "User approved")
        self.assertIn("updated_at", updated_data)
        self.assertIn("approved_at", updated_data)

    @patch("os.path.exists")
    def test_check_approval_status_approved(self, mock_exists):
        """Test checking status when file shows approved."""
        run_id = "test003"
        mock_exists.return_value = True
        mock_data = json.dumps({"status": "approved"})
        with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
            status = artist_batch_runner.check_approval_status(run_id)
            self.assertTrue(status)
            mock_file.assert_called_once_with(os.path.join(self.test_run_status_dir, f"run_{run_id}.json"), "r")

    @patch("os.path.exists")
    def test_check_approval_status_rejected(self, mock_exists):
        """Test checking status when file shows rejected."""
        run_id = "test004"
        mock_exists.return_value = True
        mock_data = json.dumps({"status": "rejected"})
        with patch("builtins.open", mock_open(read_data=mock_data)):
            status = artist_batch_runner.check_approval_status(run_id)
            self.assertFalse(status)

    @patch("os.path.exists")
    def test_check_approval_status_pending(self, mock_exists):
        """Test checking status when file shows pending."""
        run_id = "test005"
        mock_exists.return_value = True
        mock_data = json.dumps({"status": "pending_approval"})
        with patch("builtins.open", mock_open(read_data=mock_data)):
            status = artist_batch_runner.check_approval_status(run_id)
            self.assertIsNone(status)
            
    @patch("os.path.exists")
    def test_check_approval_status_file_not_found(self, mock_exists):
        """Test checking status when file doesn't exist."""
        run_id = "test006"
        mock_exists.return_value = False
        status = artist_batch_runner.check_approval_status(run_id)
        self.assertIsNone(status)

    # --- Main Cycle Tests --- #

    def test_run_batch_cycle_success_approved(self):
        """Test a successful run cycle where content is approved."""
        # Mocks already set up for success, approval happens on second check
        self.mock_check_approval.side_effect = [None, True]
        self.mock_time_time.side_effect = [1000.0, 1000.0, 1005.0, 1010.0] 
        
        artist_batch_runner.run_batch_cycle()

        self.mock_select_artist.assert_called_once()
        self.mock_get_params.assert_called_once()
        self.mock_gen_track.assert_called_once()
        self.mock_sel_video.assert_called_once()
        self.mock_send_telegram.assert_called_once() # Checks if telegram sending was attempted
        self.assertEqual(self.mock_check_approval.call_count, 2) # Called twice before approval
        self.mock_save_content.assert_called_once() # Should be called on approval
        self.mock_trigger_release.assert_called_once() # Should be called on approval

    def test_run_batch_cycle_rejected(self):
        """Test a run cycle where content is rejected."""
        self.mock_check_approval.side_effect = [None, False] # Reject on second check
        self.mock_time_time.side_effect = [1000.0, 1000.0, 1005.0, 1010.0] 
        
        artist_batch_runner.run_batch_cycle()

        self.assertEqual(self.mock_check_approval.call_count, 2)
        self.mock_save_content.assert_not_called() # Should NOT be called on rejection
        self.mock_trigger_release.assert_not_called() # Should NOT be called on rejection

    def test_run_batch_cycle_timeout(self):
        """Test a run cycle where approval times out."""
        # Simulate always pending until timeout
        self.mock_check_approval.side_effect = [None] * 10 # More checks than needed for timeout
        # Simulate time exceeding MAX_APPROVAL_WAIT_TIME
        wait_time = artist_batch_runner.MAX_APPROVAL_WAIT_TIME
        poll_interval = artist_batch_runner.POLL_INTERVAL
        time_calls = [1000.0] + [1000.0 + i * poll_interval for i in range(int(wait_time / poll_interval) + 2)]
        self.mock_time_time.side_effect = time_calls
        
        with patch("artist_batch_runner.update_run_status") as mock_update_status:
            artist_batch_runner.run_batch_cycle()

            self.assertGreater(self.mock_check_approval.call_count, 2) # Ensure polling happened
            self.mock_save_content.assert_not_called()
            self.mock_trigger_release.assert_not_called()
            # Check if status was updated to rejected due to timeout
            mock_update_status.assert_called_with(unittest.mock.ANY, "rejected", "Timeout waiting for approval")

    def test_run_batch_cycle_track_generation_fails(self):
        """Test cycle when track generation returns None."""
        self.mock_gen_track.return_value = None
        
        with patch("artist_batch_runner.update_run_status") as mock_update_status:
            artist_batch_runner.run_batch_cycle()

            self.mock_gen_track.assert_called_once()
            self.mock_sel_video.assert_not_called()
            self.mock_send_telegram.assert_not_called()
            self.mock_check_approval.assert_not_called()
            self.mock_save_content.assert_not_called()
            self.mock_trigger_release.assert_not_called()
            # Check if status updated to failure
            mock_update_status.assert_called_with(unittest.mock.ANY, "failed_generation", "Track generation failed")

    def test_run_batch_cycle_video_selection_fails(self):
        """Test cycle when video selection returns None."""
        self.mock_sel_video.return_value = None
        
        with patch("artist_batch_runner.update_run_status") as mock_update_status:
            artist_batch_runner.run_batch_cycle()

            self.mock_gen_track.assert_called_once()
            self.mock_sel_video.assert_called_once()
            self.mock_send_telegram.assert_not_called()
            # Check if status updated to failure
            mock_update_status.assert_called_with(unittest.mock.ANY, "failed_generation", "Video selection failed")

    def test_run_batch_cycle_telegram_send_fails(self):
        """Test cycle when sending to Telegram fails."""
        self.mock_send_telegram.return_value = False
        
        with patch("artist_batch_runner.update_run_status") as mock_update_status:
            artist_batch_runner.run_batch_cycle()

            self.mock_send_telegram.assert_called_once()
            self.mock_check_approval.assert_not_called()
            self.mock_save_content.assert_not_called()
            # Check if status updated to failure (done inside send_to_telegram mock in real code)
            # Here we check if update_run_status was called by the mocked send_to_telegram
            # Note: This depends on how send_to_telegram is mocked/implemented
            # A better approach might be to mock update_run_status directly inside send_to_telegram mock if needed
            # For this test structure, we assume send_to_telegram logs the error and returns False
            # We can check that the subsequent steps (polling, saving) are not called.

if __name__ == "__main__":
    unittest.main()

