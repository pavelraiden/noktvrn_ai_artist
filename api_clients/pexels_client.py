import os
import logging
from pexelsapi.pexels import Pexels
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class PexelsApiError(Exception):
    """Custom exception for Pexels API errors."""
    pass

class PexelsClient:
    """Client for interacting with the Pexels API to search for stock videos."""

    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        self.api_key = os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            logger.error("PEXELS_API_KEY not found in environment variables.")
            raise PexelsApiError("PEXELS_API_KEY is required but not set.")
        try:
            self.client = Pexels(self.api_key)
            logger.info("Pexels client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Pexels client: {e}", exc_info=True)
            raise PexelsApiError(f"Failed to initialize Pexels client: {e}")

    def search_videos(
        self,
        query: str,
        orientation: str = ",
        size: str = ",
        locale: str = ",
        page: int = 1,
        per_page: int = 15,
        min_duration: int | None = None,
        max_duration: int | None = None
    ) -> dict:
        """Searches for videos on Pexels based on a query and filters.

        Args:
            query: The search query (e.g., 'nature', 'city').
            orientation: Desired video orientation ('landscape', 'portrait', 'square').
            size: Desired video size ('large', 'medium', 'small').
            locale: Locale for the search (e.g., 'en-US').
            page: Page number to retrieve.
            per_page: Number of results per page (max 80).
            min_duration: Minimum duration in seconds.
            max_duration: Maximum duration in seconds.

        Returns:
            A dictionary containing the search results from the Pexels API.

        Raises:
            PexelsApiError: If the API call fails or returns an error.
        """
        logger.info(f"Searching Pexels videos for query: 	{query}	 with params: orientation={orientation}, size={size}, page={page}, per_page={per_page}")
        try:
            # Note: The pexels-api-py library doesn't explicitly list duration filters
            # for search_videos in its PyPI docs, only for popular_videos.
            # We will call search_videos as documented and handle potential lack of duration filtering later if needed.
            # If duration filtering is crucial, we might need to filter results client-side or use popular_videos if applicable.

            search_results = self.client.search_videos(
                query=query,
                orientation=orientation,
                size=size,
                locale=locale,
                page=page,
                per_page=per_page
            )

            # The library might return a dict-like object, let's ensure it's a standard dict
            results_dict = dict(search_results)

            if not results_dict.get("videos"):
                logger.warning(f"No videos found for query: 	{query}	")
                # Return the empty result structure instead of raising an error
                return results_dict

            logger.info(f"Found {results_dict.get(	page_result	, {}).get(	total_results	, 0)} videos for query: 	{query}	")
            return results_dict

        except Exception as e:
            logger.error(f"Error searching Pexels videos for query 	{query}	: {e}", exc_info=True)
            raise PexelsApiError(f"Failed to search Pexels videos: {e}")

# Example usage (for testing purposes)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a dummy .env file for testing if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            # IMPORTANT: Replace 'YOUR_PEXELS_API_KEY' with a real key for actual testing
            # For automated testing/CI, consider mocking or using a dedicated test key
            f.write("PEXELS_API_KEY=PLACEHOLDER_KEY_FOR_INITIALIZATION\n")
            logger.info("Created dummy .env file with placeholder PEXELS_API_KEY.")
            logger.warning("Replace PLACEHOLDER_KEY_FOR_INITIALIZATION in .env with a real Pexels API key to run live tests.")

    try:
        pexels_client = PexelsClient()
        # Only proceed if the key is not the placeholder
        if pexels_client.api_key != "PLACEHOLDER_KEY_FOR_INITIALIZATION":
            search_query = "nature sunset"
            videos = pexels_client.search_videos(query=search_query, per_page=5)
            print(f"\nSearch results for 	{search_query}	:")
            # Pretty print the results
            import json
            print(json.dumps(videos, indent=2))

            if videos.get("videos"):
                first_video = videos["videos"][0]
                print(f"\nFirst video ID: {first_video.get(	id	)}")
                print(f"First video URL: {first_video.get(	url	)}")
                # Find a downloadable link (e.g., highest quality)
                video_files = first_video.get(	video_files	, [])
                if video_files:
                    hq_link = max(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0))
                    print(f"Highest quality video link ({hq_link.get(	quality	)}): {hq_link.get(	link	)}")
        else:
            logger.warning("Skipping live API call test as PEXELS_API_KEY is a placeholder.")

    except PexelsApiError as e:
        print(f"\nPexels API Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during testing: {e}")

