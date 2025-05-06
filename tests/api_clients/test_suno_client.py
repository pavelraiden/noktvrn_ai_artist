import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add relevant paths to sys.path to allow imports
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, project_root)
streamlit_app_root = os.path.abspath(
    os.path.join(project_root, "..", "streamlit_app")
)
sys.path.insert(0, streamlit_app_root)

# Need requests for the side_effect
import requests

from api_clients.suno_client import SunoApiClient, SunoApiError

# Removed: from config import settings


# Mock settings for testing
class MockSettings:
    SUNO_API_KEY = "TEST_SUNO_KEY"


settings = MockSettings()  # Instantiate the mock


class TestSunoApiClient(unittest.TestCase):

    def setUp(self):
        """Set up the test client before each test."""
        # Ensure the mock settings object has the default key for each test
        settings.SUNO_API_KEY = "TEST_SUNO_KEY"
        self.client = SunoApiClient(api_key=settings.SUNO_API_KEY)

    # Corrected patch target to where requests.request is looked up
    @patch("api_clients.base_client.requests.request")
    def test_start_audio_generation_success(self, mock_request):
        """Test successful initiation of audio generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "clip_123",
                "status": "queued",
                "title": "Test Song",
            }
        ]
        mock_request.return_value = mock_response

        response = self.client.start_audio_generation(
            prompt="A test song", make_instrumental=False, wait_audio=False
        )

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")  # Check method
        self.assertEqual(
            args[1], f"{self.client.base_url}/generate"
        )  # Check URL
        self.assertIn("prompt", kwargs["json"])
        self.assertEqual(kwargs["json"]["prompt"], "A test song")
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(
            kwargs["headers"]["Authorization"],
            f"Bearer {settings.SUNO_API_KEY}",  # Use the mock settings object
        )

        self.assertIsInstance(response, list)
        self.assertEqual(response[0]["id"], "clip_123")

    # Corrected patch target
    @patch("api_clients.base_client.requests.request")
    def test_start_audio_generation_api_error(self, mock_request):
        """Test API error during audio generation start."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid input"}
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("Bad Request")
        )
        mock_request.return_value = mock_response

        with self.assertRaises(SunoApiError) as cm:
            self.client.start_audio_generation(prompt="Invalid")
        self.assertIn(
            "Failed to start Suno audio generation", str(cm.exception)
        )
        # Check the underlying HTTP error message if possible
        self.assertIn("Bad Request", str(cm.exception.__cause__))

    # Corrected patch target
    @patch("api_clients.base_client.requests.request")
    def test_get_generation_details_success(self, mock_request):
        """Test successful retrieval of generation details."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "clip_123",
                "status": "complete",
                "audio_url": "http://example.com/audio.mp3",
            }
        ]
        mock_request.return_value = mock_response

        clip_ids = ["clip_123"]
        response = self.client.get_generation_details(clip_ids)

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")  # Check method
        self.assertEqual(args[1], f"{self.client.base_url}/feed")  # Check URL
        self.assertEqual(kwargs["params"], {"ids": ",".join(clip_ids)})
        self.assertIn("Authorization", kwargs["headers"])

        self.assertIsInstance(response, list)
        self.assertEqual(response[0]["id"], "clip_123")
        self.assertEqual(
            response[0]["audio_url"], "http://example.com/audio.mp3"
        )

    # Corrected patch target
    @patch("api_clients.base_client.requests.request")
    def test_get_generation_details_api_error(self, mock_request):
        """Test API error during retrieval of generation details."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Not Found"}
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("Not Found")
        )
        mock_request.return_value = mock_response

        with self.assertRaises(SunoApiError) as cm:
            self.client.get_generation_details(["clip_not_found"])
        self.assertIn(
            "Failed to get Suno generation details", str(cm.exception)
        )
        self.assertIn("Not Found", str(cm.exception.__cause__))

    def test_initialization_no_api_key(self):
        """Test client initialization raises error if API key is missing."""
        original_key = settings.SUNO_API_KEY
        settings.SUNO_API_KEY = None  # Modify the mock settings object
        with self.assertRaises(ValueError) as cm:
            SunoApiClient(
                api_key=None
            )  # Pass None explicitly to trigger error
        self.assertIn("Suno API Key must be provided", str(cm.exception))
        settings.SUNO_API_KEY = (
            original_key  # Restore mock value for other tests
        )


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
