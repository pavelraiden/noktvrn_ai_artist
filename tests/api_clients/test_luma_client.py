import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import time

# Add relevant paths to sys.path to allow imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
streamlit_app_root = os.path.abspath(os.path.join(project_root, "..", "streamlit_app"))
sys.path.insert(0, streamlit_app_root)

# Need requests for the side_effect
import requests

from api_clients.luma_client import LumaApiClient, LumaApiError
from config import settings

# Mock settings for testing
settings.LUMA_API_KEY = "TEST_LUMA_KEY"

class TestLumaApiClient(unittest.TestCase):

    def setUp(self):
        """Set up the test client before each test."""
        self.client = LumaApiClient(api_key="TEST_LUMA_KEY")

    # Corrected patch target to where requests.request is looked up
    @patch("api_clients.base_client.requests.request")
    def test_start_video_generation_success(self, mock_request):
        """Test successful initiation of video generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "gen_xyz",
                "state": "pending",
                "prompt": "A test video",
            }
        ]
        mock_request.return_value = mock_response

        response = self.client.start_video_generation(
            prompt="A test video",
            aspect_ratio="16:9"
        )

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST") # Check method
        self.assertEqual(args[1], f"{self.client.base_url}/generations") # Check URL
        self.assertIn("prompt", kwargs["json"])
        self.assertEqual(kwargs["json"]["prompt"], "A test video")
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {settings.LUMA_API_KEY}")

        self.assertIsInstance(response, dict)
        self.assertEqual(response["id"], "gen_xyz")

    # Corrected patch target
    @patch("api_clients.base_client.requests.request")
    def test_start_video_generation_api_error(self, mock_request):
        """Test API error during video generation start."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid prompt"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_request.return_value = mock_response

        with self.assertRaises(LumaApiError) as cm:
            self.client.start_video_generation(prompt="Invalid")
        self.assertIn("Failed to start Luma video generation", str(cm.exception))
        # Check the underlying HTTP error message
        self.assertIn("Bad Request", str(cm.exception.__cause__))

    # Corrected patch target
    @patch("api_clients.base_client.requests.request")
    def test_get_generation_details_success(self, mock_request):
        """Test successful retrieval of generation details."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "gen_xyz",
            "state": "completed",
            "video": {
                "url": "http://example.com/video.mp4",
                "thumbnail_url": "http://example.com/thumb.jpg"
            },
        }
        mock_request.return_value = mock_response

        generation_id = "gen_xyz"
        response = self.client.get_generation_details(generation_id)

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET") # Check method
        self.assertEqual(args[1], f"{self.client.base_url}/generations/{generation_id}") # Check URL
        self.assertIn("Authorization", kwargs["headers"])

        self.assertIsInstance(response, dict)
        self.assertEqual(response["id"], "gen_xyz")
        self.assertEqual(response["video"]["url"], "http://example.com/video.mp4")

    # Corrected patch target
    @patch("api_clients.base_client.requests.request")
    def test_get_generation_details_api_error(self, mock_request):
        """Test API error during retrieval of generation details."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Generation not found"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_request.return_value = mock_response

        with self.assertRaises(LumaApiError) as cm:
            self.client.get_generation_details("gen_not_found")
        self.assertIn("Failed to get Luma generation details", str(cm.exception))
        # Check the underlying HTTP error message
        self.assertIn("Not Found", str(cm.exception.__cause__))

    def test_initialization_no_api_key(self):
        """Test client initialization raises error if API key is missing."""
        original_key = settings.LUMA_API_KEY
        settings.LUMA_API_KEY = None
        with self.assertRaises(ValueError) as cm:
            LumaApiClient()
        self.assertIn("Luma API Key must be provided", str(cm.exception))
        settings.LUMA_API_KEY = original_key # Restore for other tests

if __name__ == '__main__':
    unittest.main(argv=["first-arg-is-ignored"], exit=False)

