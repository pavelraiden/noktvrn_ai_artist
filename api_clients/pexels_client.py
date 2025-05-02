import os
import logging
import time  # Added for potential delays
from pexelsapi.pexels import Pexels
from dotenv import load_dotenv

# Adjust import path based on actual structure
from ..utils.retry_decorator import retry_on_exception

logger = logging.getLogger(__name__)


class PexelsApiError(Exception):
    """Custom exception for Pexels API errors."""

    pass


# Define common exceptions to retry on for Pexels
# Note: The pexelsapi library might not raise specific HTTP errors easily.
# We'll retry on generic connection/timeout errors and potentially PexelsApiError if it wraps transient issues.
# If the library raises standard requests exceptions, add them here (e.g., requests.exceptions.RequestException)
PEXELS_RETRY_EXCEPTIONS = (
    PexelsApiError,
    ConnectionError,
    TimeoutError,
    Exception,
)  # Broad for now, refine if specific errors known


class PexelsClient:
    """Client for interacting with the Pexels API to search for stock videos."""

    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            logger.error("PEXELS_API_KEY not found in environment variables.")
            # Raise config error immediately, no point retrying initialization
            raise ValueError("PEXELS_API_KEY is required but not set.")
        try:
            # Add timeout to the Pexels client if the library supports it (check library docs/source)
            # Assuming it doesn't have a direct timeout param, rely on underlying HTTP library timeouts or decorator
            self.client = Pexels(self.api_key)
            logger.info("Pexels client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Pexels client: {e}", exc_info=True)
            # Wrap initialization error, but don't use PexelsApiError here as it's for API call issues
            raise ConnectionError(f"Failed to initialize Pexels client: {e}")

    @retry_on_exception(
        retries=3, delay=2, backoff=2, exceptions=PEXELS_RETRY_EXCEPTIONS
    )
    def search_videos(
        self,
        query: str,
        orientation: str = "",
        size: str = "",
        locale: str = "",
        page: int = 1,
        per_page: int = 15,
        min_duration: (
            int | None
        ) = None,  # Keep params even if unused by lib for potential future use
        max_duration: int | None = None,
    ) -> dict:
        """Searches for videos on Pexels based on a query and filters. Retries on transient errors.

        Args:
            query: The search query (e.g., 'nature', 'city').
            orientation: Desired video orientation ('landscape', 'portrait', 'square').
            size: Desired video size ('large', 'medium', 'small').
            locale: Locale for the search (e.g., 'en-US').
            page: Page number to retrieve.
            per_page: Number of results per page (max 80).
            min_duration: Minimum duration in seconds (Note: May not be supported by underlying library).
            max_duration: Maximum duration in seconds (Note: May not be supported by underlying library).

        Returns:
            A dictionary containing the search results from the Pexels API.

        Raises:
            PexelsApiError: If the API call fails definitively after retries.
            Exception: Other exceptions if they occur and are not in PEXELS_RETRY_EXCEPTIONS.
        """
        logger.info(
            f"Searching Pexels videos for query: '{query}' with params: orientation={orientation}, size={size}, page={page}, per_page={per_page}"
        )

        # Let the decorator handle retries and exceptions
        search_results = self.client.search_videos(
            query=query,
            orientation=orientation,
            size=size,
            locale=locale,
            page=page,
            per_page=per_page,
        )

        # The library might return a dict-like object, let's ensure it's a standard dict
        # The pexelsapi library seems to return a PexelsResult object, convert it
        try:
            # Access attributes directly based on library's structure
            results_dict = {
                "page": search_results.page,
                "per_page": search_results.per_page,
                "total_results": search_results.total_results,
                "url": search_results.url,
                "videos": [
                    vars(video) for video in search_results.entries
                ],  # Convert Video objects to dicts
            }
        except AttributeError as e:
            logger.error(
                f"Failed to parse Pexels response structure: {e}. Response object: {search_results}"
            )
            raise PexelsApiError(f"Unexpected Pexels API response format: {e}")

        if not results_dict.get("videos"):
            logger.warning(f"No videos found for query: '{query}'")
            # Return the empty result structure
            return results_dict

        logger.info(
            f"Found {results_dict.get('total_results', 0)} videos for query: '{query}'"
        )
        return results_dict


# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Removed dummy .env creation - Expect real .env in production

    try:
        pexels_client = PexelsClient()
        # Removed placeholder check - Expect real key in production .env
        if pexels_client.api_key:
            search_query = "nature sunset"
            try:
                videos = pexels_client.search_videos(query=search_query, per_page=5)
                print(f"\nSearch results for '{search_query}':")
                import json

                print(json.dumps(videos, indent=2))

                if videos.get("videos"):
                    first_video = videos["videos"][0]
                    print(f"\nFirst video ID: {first_video.get('id')}")
                    print(f"First video URL: {first_video.get('url')}")
                    # Find a downloadable link (e.g., highest quality)
                    video_files = first_video.get("video_files", [])
                    if video_files:
                        # Ensure width/height exist and handle potential None values
                        valid_files = [
                            f
                            for f in video_files
                            if f.get("width") is not None
                            and f.get("height") is not None
                        ]
                        if valid_files:
                            hq_link = max(
                                valid_files, key=lambda x: x["width"] * x["height"]
                            )
                            print(
                                f"Highest quality video link ({hq_link.get('quality')}): {hq_link.get('link')}"
                            )
                        else:
                            print("No video files with valid dimensions found.")
                    else:
                        print("No video files found for the first video.")
                else:
                    print(f"No videos found for query '{search_query}' after retries.")
            except Exception as api_call_error:
                print(
                    f"\nError during Pexels API call for '{search_query}': {api_call_error}"
                )
        else:
            # This case should ideally not happen if ValueError is raised correctly in __init__
            logger.warning(
                "Skipping live API call test as PEXELS_API_KEY was not loaded."
            )

    except ValueError as config_e:
        print(f"\nConfiguration Error: {config_e}")
    except ConnectionError as init_e:
        print(f"\nInitialization Error: {init_e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during testing: {e}")
