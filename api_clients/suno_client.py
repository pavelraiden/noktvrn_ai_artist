import logging
import time
import sys
import os
from dotenv import load_dotenv

# Removed unused asyncio, aiohttp

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path to allow importing base_client
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Removed streamlit_app path insertion as config is no longer imported

from api_clients.base_client import BaseApiClient, ApiClientError  # noqa: E402

# Removed config import

logger = logging.getLogger(__name__)


class SunoApiError(ApiClientError):
    """Custom exception for Suno API errors."""

    pass


class SunoApiClient(BaseApiClient):
    """Client for interacting with the Suno API
    (unofficial, via sunoapi.org wrapper).
    """

    # Based on https://docs.sunoapi.org/
    DEFAULT_BASE_URL = "https://apibox.erweima.ai"

    def __init__(
        self, api_key: str | None = None, base_url: str | None = None
    ):
        """Initializes the SunoApiClient.

        Args:
            api_key: The Suno API key. Defaults to SUNO_API_KEY
                     environment variable.
            base_url: The base URL for the Suno API. Defaults to
                      DEFAULT_BASE_URL or SUNO_BASE_URL environment variable.
        """
        resolved_api_key = api_key or os.getenv("SUNO_API_KEY")
        # Allow overriding base_url via env var as well
        resolved_base_url = base_url or os.getenv(
            "SUNO_BASE_URL", self.DEFAULT_BASE_URL
        )

        if not resolved_api_key:
            logger.error(
                "Suno API Key is not configured in environment "
                "variables (SUNO_API_KEY)."
            )
            raise ValueError(
                "Suno API Key must be provided either directly or via "
                "SUNO_API_KEY environment variable"
            )

        super().__init__(base_url=resolved_base_url, api_key=resolved_api_key)

    # Renamed from start_music_generation to match track_service usage
    def start_audio_generation(
        self,
        prompt: str,
        model: str = "v3.5",
        custom_mode: bool = False,
        title: str | None = None,
        tags: str | None = None,
        make_instrumental: bool = False,
        wait_audio: bool = False,
        callback_url: str | None = None,
    ) -> list:
        """Starts a music generation task.

        Args:
            prompt: The text prompt for the music.
            model: The model version (e.g., "v3.5", "v4"). Defaults to "v3.5".
            custom_mode: Whether to use custom mode (requires lyrics,
                         style prompt etc.). Defaults to False.
            title: Optional title for the track.
            tags: Optional style tags (e.g., "acoustic, pop").
            make_instrumental: Whether to generate instrumental music.
                               Defaults to False.
            wait_audio: Whether the API should wait until audio is ready
                        before returning. Defaults to False.
            callback_url: Optional URL to receive webhook notifications.

        Returns:
            A list containing dictionaries for each generated clip,
            including task IDs.
            Example (based on docs, may vary):
            [
                {
                    "id": "clip_id_1",
                    "status": "queued",
                    ...
                },
                ...
            ]
            Or if wait_audio=True, might return the full details
            including URLs.

        Raises:
            SunoApiError: If the API request fails.
        """
        endpoint = (
            "/generate"  # Corrected endpoint based on unofficial docs/tests
        )
        payload = {
            "prompt": prompt,
            "model": model,
            "custom_mode": custom_mode,
            "make_instrumental": make_instrumental,
            "wait_audio": wait_audio,
        }
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = tags
        if callback_url:
            payload["callback_url"] = callback_url

        logger.info(
            f'Starting Suno music generation with prompt: "{prompt[:50]}..."'
        )
        try:
            # The unofficial API returns a list directly
            response_data = self._post(endpoint, json_data=payload)
            logger.info(
                "Suno music generation task started successfully. "
                f"Response: {response_data}"
            )
            # Basic validation of response structure (expecting a list)
            if not isinstance(response_data, list) or not all(
                "id" in item for item in response_data
            ):
                raise SunoApiError(
                    "Suno API returned an unexpected response format: "
                    f"{response_data}"
                )
            return response_data
        except ApiClientError as e:
            logger.error(f"Suno API request failed: {e}", exc_info=True)
            # TODO [fallback_bas_integration]:
            # This section should support BAS fallback for beat/vocal/lyric
            # generation
            # if the LLM/API path fails entirely.
            # Consider implementing a call to a fallback handler here.
            raise SunoApiError(
                f"Failed to start Suno audio generation: {e}"
            ) from e

    def get_generation_details(self, clip_ids: list[str]) -> list:
        """Gets the details and status of one or more generated clips.

        Args:
            clip_ids: A list of clip IDs to query.

        Returns:
            A list of dictionaries containing the status and
            results for each clip.
            Example (based on docs,
                     may vary):
            [
                {
                    "id": "clip_id_1",
                    "status": "complete", # or "streaming", "failed", etc.
                    "audio_url": "...",
                    "image_url": "...",
                    "title": "...",
                    ...
                },
                ...
            ]

        Raises:
            SunoApiError: If the API request fails.
        """
        endpoint = "/feed"  # Corrected endpoint based on unofficial docs/tests
        if not clip_ids:
            return []

        ids_param = ",".join(clip_ids)
        logger.debug(
            f"Fetching Suno generation details for clip_ids: {ids_param}"
        )
        try:
            response_data = self._get(endpoint, params={"ids": ids_param})
            logger.debug(f"Suno generation details received: {response_data}")
            # Basic validation (expecting a list)
            if not isinstance(response_data, list):
                raise SunoApiError(
                    "Suno API returned an unexpected response format "
                    f"when fetching details: {response_data}"
                )
            return response_data
        except ApiClientError as e:
            logger.error(f"Suno API request failed: {e}", exc_info=True)
            raise SunoApiError(
                f"Failed to get Suno generation details: {e}"
            ) from e


# Example Usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Check if the key is available in the environment
    suno_api_key = os.getenv("SUNO_API_KEY")
    if not suno_api_key:
        print(
            "Please ensure the SUNO_API_KEY is set in your .env file "
            "or environment variables to run this example."
        )
    else:
        try:
            # Initialize client (will use key from environment)
            client = SunoApiClient()

            print("\n--- Testing Start Generation (Non-blocking) ---")
            start_response = client.start_audio_generation(
                prompt="A cheerful upbeat acoustic pop song about sunny days",
                # model="chirp-v3-0", # Use default from client
                tags="pop, acoustic, upbeat",
                title="Sunny Day Dream",
                wait_audio=False,
            )
            print(f"Start Response: {start_response}")

            clip_ids = [
                item.get("id") for item in start_response if item.get("id")
            ]

            if clip_ids:
                print(
                    "\n--- Testing Get Details "
                    f"(Polling for IDs: {clip_ids}) ---"
                )
                attempts = 0
                max_attempts = 10
                wait_time = 15  # seconds
                final_details = None
                while attempts < max_attempts:
                    attempts += 1
                    print(
                        f"Attempt {attempts}/{max_attempts}: "
                        "Fetching details..."
                    )
                    details_response = client.get_generation_details(clip_ids)
                    print(f"Details Response: {details_response}")

                    all_complete = True
                    any_failed = False
                    current_statuses = []
                    for item in details_response:
                        status = item.get("status")
                        current_statuses.append(status)
                        if status != "complete":
                            all_complete = False
                        if status == "failed":
                            any_failed = True

                    if all_complete:
                        print("All clips complete!")
                        final_details = details_response
                        break
                    elif any_failed:
                        print("At least one clip failed.")
                        final_details = details_response
                        break
                    else:
                        print(
                            f"Statuses: {current_statuses}. "
                            f"Waiting {wait_time} seconds..."
                        )
                        time.sleep(wait_time)

                if not final_details:
                    print("Polling timed out.")
                elif all_complete:
                    for item in final_details:
                        print(
                            f"Clip {item.get('id')} Audio URL: "
                            f"{item.get('audio_url')}"
                        )
                else:
                    print(
                        "Generation did not complete successfully "
                        "for all clips."
                    )
            else:
                print("Could not extract clip_ids from start response.")

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except SunoApiError as e:
            print(f"Suno API Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _handle_fallback_generation(self, payload: dict):
        """Placeholder for handling generation via BAS fallback.

        Args:
            payload: The original payload intended for the API.
        """
        # TODO [fallback_bas_integration]:
        # Implement the actual BAS fallback logic here.
        # This should involve:
        # 1. Triggering the BAS script with necessary parameters from payload.
        # 2. Monitoring the BAS script execution.
        # 3. Retrieving results (file paths, status) from BAS.
        # 4. Formatting results similar to the API response.
        # 5. Handling errors during BAS execution.
        logger.warning(
            "Suno API failed. BAS fallback is not yet implemented. "
            f"Original payload: {payload}"
        )
        # For now, return None or raise NotImplementedError
        # Depending on how the caller should handle this placeholder
        # Returning None might imply fallback didn't produce results yet
        return None
