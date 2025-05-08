#!/usr/bin/env python3

import unittest
import os
import sys
import shutil
from unittest.mock import patch # Removed MagicMock, mock_open, call
# Removed json, time, datetime

# --- Add project root to sys.path for imports ---
# Adjust path based on where tests are run from
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(
    0, os.path.join(PROJECT_ROOT, "..")
)  # Add ai_artist_system root
sys.path.insert(
    0, os.path.join(PROJECT_ROOT, "..", "batch_runner")
)  # Add batch_runner dir
sys.path.insert(
    0, os.path.join(PROJECT_ROOT, "..", "streamlit_app")
)  # Add streamlit_app dir

# Import the script to be tested
# We need to mock imports within the script *before* importing it if they cause issues
# For now, assume imports work or are handled by placeholders
try:
    import artist_batch_runner
except ImportError as e:
    print(f"Initial import failed: {e}. Defining dummy module.")

    # Define dummy module/functions if import fails during test collection
    class DummyArtistBatchRunner:
        OUTPUT_DIR = "dummy_output"
        RUN_STATUS_DIR = "dummy_run_status"
        MAX_APPROVAL_WAIT_TIME = 10  # Dummy value
        POLL_INTERVAL = 1  # Dummy value

        def select_next_artist(self, *args, **kwargs):
            return None

        def get_adapted_parameters(self, *args, **kwargs):
            return None

        def generate_track(self, *args, **kwargs):
            return None

        def select_video(self, *args, **kwargs):
            return None

        def create_initial_run_status(self, *args, **kwargs):
            return False

        def send_to_telegram_for_approval(self, *args, **kwargs):
            return False

        def check_approval_status(self, *args, **kwargs):
            return None

        def update_run_status(self, *args, **kwargs):
            pass

        def save_approved_content(self, *args, **kwargs):
            return False

        def trigger_release_logic(self, *args, **kwargs):
            pass

        def run_batch_cycle(self, *args, **kwargs):
            pass

    artist_batch_runner = DummyArtistBatchRunner()

# --- Test Class --- #


class TestArtistBatchRunner(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directories for testing file operations
        self.test_output_dir = os.path.join(
            os.path.dirname(__file__), "test_output"
        )
        self.test_run_status_dir = os.path.join(
            self.test_output_dir, "run_status"
        )
        os.makedirs(self.test_run_status_dir, exist_ok=True)

        # Override the directories used by the script
        artist_batch_runner.OUTPUT_DIR = self.test_output_dir
        artist_batch_runner.RUN_STATUS_DIR = self.test_run_status_dir
        # Set constants for testing
        artist_batch_runner.MAX_APPROVAL_WAIT_TIME = 10  # seconds
        artist_batch_runner.POLL_INTERVAL = 2  # seconds

        # Reset any global state if necessary (e.g., logging setup)
        # For simplicity, we assume logging setup is idempotent

        # Mock external dependencies that are always called
        self.patcher_select_artist = patch(
            "artist_batch_runner.select_next_artist"
        )
        self.mock_select_artist = self.patcher_select_artist.start()
        self.mock_select_artist.return_value = {
            "artist_id": 99,
            "name": "Test Artist",
            "genre": "testwave",
        }

        self.patcher_get_params = patch(
            "artist_batch_runner.get_adapted_parameters"
        )
        self.mock_get_params = self.patcher_get_params.start()
        self.mock_get_params.return_value = {
            "suno_prompt": "test",
            "video_keywords": ["test"],
        }

        self.patcher_gen_track = patch("artist_batch_runner.generate_track")
        self.mock_gen_track = self.patcher_gen_track.start()
        self.mock_gen_track.return_value = {
            "track_id": "t123",
            "track_url": "http://fake-track",
        }

        self.patcher_sel_video = patch("artist_batch_runner.select_video")
        self.mock_sel_video = self.patcher_sel_video.start()
        self.mock_sel_video.return_value = {
            "video_url": "http://fake-video",
            "source": "test-src",
        }

        self.patcher_create_status = patch(
            "artist_batch_runner.create_initial_run_status"
        )
        self.mock_create_status = self.patcher_create_status.start()
        self.mock_create_status.return_value = True

        self.patcher_send_telegram = patch(
            "artist_batch_runner.send_to_telegram_for_approval"
        )
        self.mock_send_telegram = self.patcher_send_telegram.start()
        self.mock_send_telegram.return_value = True

        self.patcher_check_approval = patch(
            "artist_batch_runner.check_approval_status"
        )
        self.mock_check_approval = self.patcher_check_approval.start()
        # Default to approved after first check
        self.mock_check_approval.side_effect = [None, True]

        self.patcher_update_status = patch(
            "artist_batch_runner.update_run_status"
        )
        self.mock_update_status = self.patcher_update_status.start()

        self.patcher_save_content = patch(
            "artist_batch_runner.save_approved_content"
        )
        self.mock_save_content = self.patcher_save_content.start()
        self.mock_save_content.return_value = True

        self.patcher_trigger_release = patch(
            "artist_batch_runner.trigger_release_logic"
        )
        self.mock_trigger_release = self.patcher_trigger_release.start()

        self.patcher_time_sleep = patch(
            "time.sleep"  # Patch time.sleep directly
        )
        self.mock_time_sleep = self.patcher_time_sleep.start()

        self.patcher_time_time = patch("time.time")
        self.mock_time_time = self.patcher_time_time.start()
        # Simulate time passing during polling
        self.mock_time_time.side_effect = [
            1000.0,  # Start time
            1000.0,  # First check
            1002.0,  # Second check (after POLL_INTERVAL)
            1004.0,  # Third check
            1006.0,  # Fourth check
            1008.0,  # Fifth check
            1010.0,  # Sixth check (timeout)
            1012.0,  # Extra calls if needed
        ]

    def tearDown(self):
        """Clean up test environment after each test."""
        # Stop all patchers
        self.patcher_select_artist.stop()
        self.patcher_get_params.stop()
        self.patcher_gen_track.stop()
        self.patcher_sel_video.stop()
        self.patcher_create_status.stop()
        self.patcher_send_telegram.stop()
        self.patcher_check_approval.stop()
        self.patcher_update_status.stop()
        self.patcher_save_content.stop()
        self.patcher_trigger_release.stop()
        self.patcher_time_sleep.stop()
        self.patcher_time_time.stop()

        # Remove temporary directories
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    # --- Individual Function Tests (Keep if useful, but focus on main cycle) --- #

    # Example: Test create_initial_run_status (if not mocked above)
    # def test_create_initial_run_status_logic(self):
    #     run_id = "test001"
    #     artist = {"artist_id": 1, "name": "A"}
    #     track = {"track_id": "t1", "track_url": "url_t"}
    #     video = {"video_url": "url_v", "source": "s"}
    #     expected_path = os.path.join(self.test_run_status_dir, f"run_{run_id}.json")
    #
    #     # Use the real function, but mock open
    #     with patch("builtins.open", mock_open()) as mock_file:
    #         result = artist_batch_runner.create_initial_run_status(
    #             run_id, artist, track, video
    #         )
    #         self.assertTrue(result)
    #         mock_file.assert_called_once_with(expected_path, "w")
    #         args, kwargs = mock_file().write.call_args
    #         written_data = json.loads(args[0])
    #         self.assertEqual(written_data["status"], "pending_approval")
    #         self.assertEqual(written_data["artist_id"], 1)

    # --- Main Cycle Tests --- #

    def test_run_batch_cycle_success_approved(self):
        """Test a successful run cycle where content is approved."""
        # Mocks already set up for success, approval happens on second check
        self.mock_check_approval.side_effect = [None, True]
        self.mock_time_time.side_effect = [1000.0, 1000.0, 1002.0, 1004.0]

        artist_batch_runner.run_batch_cycle()

        self.mock_select_artist.assert_called_once()
        self.mock_get_params.assert_called_once()
        self.mock_gen_track.assert_called_once()
        self.mock_sel_video.assert_called_once()
        self.mock_create_status.assert_called_once()  # Check if initial status creation was called
        self.mock_send_telegram.assert_called_once()  # Checks if telegram sending was attempted
        self.assertEqual(
            self.mock_check_approval.call_count, 2
        )  # Called twice before approval
        # Check update_run_status was called for approval
        self.mock_update_status.assert_any_call(
            unittest.mock.ANY, "approved", "User approved"
        )
        self.mock_save_content.assert_called_once()  # Should be called on approval
        self.mock_trigger_release.assert_called_once()  # Should be called on approval

    def test_run_batch_cycle_rejected(self):
        """Test a run cycle where content is rejected."""
        self.mock_check_approval.side_effect = [
            None,
            False,
        ]  # Reject on second check
        self.mock_time_time.side_effect = [1000.0, 1000.0, 1002.0, 1004.0]

        artist_batch_runner.run_batch_cycle()

        self.assertEqual(self.mock_check_approval.call_count, 2)
        # Check update_run_status was called for rejection
        self.mock_update_status.assert_any_call(
            unittest.mock.ANY, "rejected", "User rejected"
        )
        self.mock_save_content.assert_not_called()  # Should NOT be called on rejection
        self.mock_trigger_release.assert_not_called()  # Should NOT be called on rejection

    def test_run_batch_cycle_timeout(self):
        """Test a run cycle where approval times out."""
        # Simulate always pending until timeout
        self.mock_check_approval.side_effect = [None] * 10  # Always pending
        # Simulate time exceeding MAX_APPROVAL_WAIT_TIME (10s)
        # Start, check 1, check 2, check 3, check 4, check 5 (timeout) ...
        self.mock_time_time.side_effect = [
            1000.0,
            1000.0,
            1002.0,
            1004.0,
            1006.0,
            1008.0,
            1010.0,
            1012.0,
        ]

        artist_batch_runner.run_batch_cycle()

        # Check polling happened multiple times (until timeout)
        # Expected calls = timeout / poll_interval + 1 = 10 / 2 + 1 = 6
        self.assertEqual(self.mock_check_approval.call_count, 6)
        self.mock_save_content.assert_not_called()
        self.mock_trigger_release.assert_not_called()
        # Check if status was updated to rejected due to timeout
        self.mock_update_status.assert_called_with(
            unittest.mock.ANY, "rejected", "Timeout waiting for approval"
        )

    def test_run_batch_cycle_track_generation_fails(self):
        """Test cycle when track generation returns None."""
        self.mock_gen_track.return_value = None

        artist_batch_runner.run_batch_cycle()

        self.mock_gen_track.assert_called_once()
        self.mock_sel_video.assert_not_called()
        self.mock_create_status.assert_not_called()
        self.mock_send_telegram.assert_not_called()
        self.mock_check_approval.assert_not_called()
        self.mock_save_content.assert_not_called()
        self.mock_trigger_release.assert_not_called()
        # Check if status updated to failure
        self.mock_update_status.assert_called_with(
            unittest.mock.ANY,
            "failed_generation",
            "Track generation failed",
        )

    def test_run_batch_cycle_video_selection_fails(self):
        """Test cycle when video selection returns None."""
        self.mock_sel_video.return_value = None

        artist_batch_runner.run_batch_cycle()

        self.mock_gen_track.assert_called_once()
        self.mock_sel_video.assert_called_once()
        self.mock_create_status.assert_not_called()
        self.mock_send_telegram.assert_not_called()
        # Check if status updated to failure
        self.mock_update_status.assert_called_with(
            unittest.mock.ANY,
            "failed_generation",
            "Video selection failed",
        )

    def test_run_batch_cycle_create_status_fails(self):
        """Test cycle when creating initial status file fails."""
        self.mock_create_status.return_value = False  # Simulate failure

        artist_batch_runner.run_batch_cycle()

        self.mock_gen_track.assert_called_once()
        self.mock_sel_video.assert_called_once()
        self.mock_create_status.assert_called_once()
        self.mock_send_telegram.assert_not_called()  # Should not proceed
        self.mock_check_approval.assert_not_called()
        # Check if status updated to failure (implicitly, as cycle stops)
        # No direct update_status call expected here, but subsequent steps are skipped.
        self.mock_update_status.assert_not_called()  # Assuming failure is logged and cycle exits

    def test_run_batch_cycle_telegram_send_fails(self):
        """Test cycle when sending to Telegram fails."""
        self.mock_send_telegram.return_value = False

        artist_batch_runner.run_batch_cycle()

        self.mock_send_telegram.assert_called_once()
        self.mock_check_approval.assert_not_called()  # Polling should not start
        self.mock_save_content.assert_not_called()
        # Check if status updated to failure (should be handled within send_to_telegram or main loop)
        # Assuming the main loop calls update_run_status on failure
        self.mock_update_status.assert_called_with(
            unittest.mock.ANY,
            "failed_approval_send",
            "Failed to send to Telegram",
        )


if __name__ == "__main__":
    unittest.main()

