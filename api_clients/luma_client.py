import logging
import time
import sys
import os

# Add the project root to the Python path to allow importing settings and base_client
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
streamlit_app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "streamlit_app"))
sys.path.insert(0, streamlit_app_root)

from api_clients.base_client import BaseApiClient, ApiClientError
from config import settings # Assuming settings are accessible from streamlit_app/config

logger = logging.getLogger(__name__)

class LumaApiError(ApiClientError):
    """Custom exception for Luma API errors."""
    pass

class LumaApiClient(BaseApiClient):
    """Client for interacting with the Luma Labs Dream Machine API."""

    # Based on https://docs.lumalabs.ai/docs/video-generation
    DEFAULT_BASE_URL = "https://api.lumalabs.ai/dream-machine/v1"

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """Initializes the LumaApiClient.

        Args:
            api_key: The Luma API key. Defaults to settings.LUMA_API_KEY.
            base_url: The base URL for the Luma API. Defaults to DEFAULT_BASE_URL.
        """
        resolved_api_key = api_key or settings.LUMA_API_KEY
        resolved_base_url = base_url or self.DEFAULT_BASE_URL
        
        # Removed check for placeholder key as we expect a real key in production
        # Note: Luma client implementation might still be partial/placeholder
        if not resolved_api_key:
             logger.error("Luma API Key is not configured.")
             raise ValueError("Luma API Key must be provided either directly or via settings.LUMA_API_KEY")

        super().__init__(base_url=resolved_base_url, api_key=resolved_api_key)

    def start_video_generation(self, prompt: str, image_url: str | None = None, aspect_ratio: str = "16:9", model: str = "ray-2", user_id: str | None = None, callback_url: str | None = None, **kwargs) -> dict:
        """Starts a video generation task (text-to-video or image-to-video).

        Args:
            prompt: The text prompt describing the video.
            image_url: Optional URL of an image to use as input (for image-to-video).
            aspect_ratio: Desired aspect ratio (e.g., "16:9", "1:1"). Defaults to "16:9".
            model: The generation model to use (e.g., "ray-2", "ray-flash-2"). Defaults to "ray-2".
            user_id: Optional user identifier for tracking.
            callback_url: Optional URL to receive webhook notifications.
            **kwargs: Additional parameters accepted by the Luma API endpoint.

        Returns:
            A dictionary containing the initial response, including the generation ID.
            Example (based on docs, may vary):
            {
                "id": "gen_xxx",
                "state": "pending", 
                "created_at": "...",
                "prompt": "...",
                ...
            }

        Raises:
            LumaApiError: If the API request fails.
        """
        endpoint = "/generations"
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "model": model,
            # Add other potential parameters like negative_prompt, seed, etc. via kwargs
            **kwargs 
        }
        if image_url:
            payload["image_url"] = image_url
            # Fixed syntax error in f-string by escaping inner quotes
            logger.info(f"Starting Luma image-to-video generation for prompt: \"{prompt[:50]}...\" with image: {image_url}")
        else:
            # Fixed syntax error in f-string by escaping inner quotes
            logger.info(f"Starting Luma text-to-video generation for prompt: \"{prompt[:50]}...\"")
            
        if user_id:
            payload["user_id"] = user_id
        if callback_url:
            payload["callback_url"] = callback_url

        try:
            response_data = self._post(endpoint, json_data=payload)
            # Luma API returns a list containing the generation object
            if isinstance(response_data, list) and len(response_data) > 0:
                generation_info = response_data[0]
                # Fixed syntax error: Removed extra parenthesis/quotes around generation_info.get("id")
                logger.info(f"Luma video generation task started successfully. ID: {generation_info.get('id')}")
                if "id" not in generation_info:
                     raise LumaApiError(f"Luma API response missing 'id' in generation info: {generation_info}")
                return generation_info
            else:
                logger.error(f"Luma API returned an unexpected response format: {response_data}")
                raise LumaApiError(f"Luma API returned an unexpected response format: {response_data}")

        except ApiClientError as e:
            logger.error(f"Luma API request failed: {e}", exc_info=True)
            raise LumaApiError(f"Failed to start Luma video generation: {e}") from e

    def get_generation_details(self, generation_id: str) -> dict:
        """Gets the details and status of a video generation task.

        Args:
            generation_id: The ID of the generation task to query.

        Returns:
            A dictionary containing the task status and results.
            Example (based on docs, may vary):
            {
                "id": "gen_xxx",
                "state": "completed", # or "processing", "failed", "pending"
                "created_at": "...",
                "prompt": "...",
                "video": {
                    "url": "...",
                    "thumbnail_url": "..."
                },
                ...
            }

        Raises:
            LumaApiError: If the API request fails.
        """
        endpoint = f"/generations/{generation_id}"
        logger.debug(f"Fetching Luma generation details for ID: {generation_id}")
        try:
            response_data = self._get(endpoint)
            logger.debug(f"Luma generation details received: {response_data}")
            # Basic validation
            if "id" not in response_data or "state" not in response_data:
                 raise LumaApiError(f"Luma API returned an unexpected response format when fetching details: {response_data}")
            return response_data
        except ApiClientError as e:
            logger.error(f"Luma API request failed: {e}", exc_info=True)
            raise LumaApiError(f"Failed to get Luma generation details: {e}") from e

# Example Usage (for testing purposes)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Removed check for placeholder key as we expect a real key in production .env
    if not settings.LUMA_API_KEY:
        print("Please ensure the LUMA_API_KEY is set in your .env file or environment variables to run this example.")
    else:
        try:
            client = LumaApiClient()
            
            # --- Test 1: Start Text-to-Video Generation (Non-blocking) ---
            print("\n--- Testing Start Text-to-Video Generation (Non-blocking) ---")
            start_response = client.start_video_generation(
                prompt="A futuristic cityscape at sunset, flying cars zooming by",
                aspect_ratio="16:9"
            )
            print(f"Start Response: {start_response}")
            
            generation_id = start_response.get("id")
            
            if generation_id:
                print(f"\n--- Testing Get Details (Polling for ID: {generation_id}) ---")
                # --- Test 2: Poll for details ---
                attempts = 0
                max_attempts = 15 # Luma might take longer
                wait_time = 20 # seconds
                final_details = None
                while attempts < max_attempts:
                    attempts += 1
                    print(f"Attempt {attempts}/{max_attempts}: Fetching details...")
                    details_response = client.get_generation_details(generation_id)
                    print(f"Details Response: {details_response}")
                    state = details_response.get("state")
                    
                    if state == 'completed':
                        print("Generation complete!")
                        final_details = details_response
                        break
                    elif state == 'failed':
                        print("Generation failed.")
                        final_details = details_response # Still useful to see the failure reason if available
                        break
                    else:
                        print(f"State: {state}. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                
                if not final_details:
                    print("Polling timed out.")
                elif final_details.get("state") == 'completed':
                    video_url = final_details.get("video", {}).get("url")
                    print(f"\nVideo URL: {video_url}")
                else:
                    print("\nGeneration did not complete successfully.")
            else:
                print("Could not extract generation_id from start response.")

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except LumaApiError as e:
            print(f"Luma API Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

