import logging
import random
from typing import List, Dict, Any, Optional  # Added Optional

# Import the tracker
try:
    from ..analytics.stock_success_tracker import StockSuccessTracker, StockTrackerError
except ImportError:
    logging.warning(
        "Failed to import StockSuccessTracker. Performance-based source selection disabled."
    )

    # Define dummy tracker if import fails
    class StockSuccessTracker:
        def get_top_sources(
            self, genre: Optional[str] = None, days: int = 30
        ) -> List[str]:
            return []

        def log_clip_usage(self, release_id: Any, source_name: str, clip_id: Any):
            pass

    class StockTrackerError(Exception):
        pass


from ..api_clients.pexels_client import PexelsClient, PexelsApiError

# Assuming audio_analyzer is in the same directory (or adjust path)
try:
    from .audio_analyzer import AudioAnalysisError
except ImportError:

    class AudioAnalysisError(Exception):
        pass  # Dummy if needed


logger = logging.getLogger(__name__)


class VideoSelectionError(Exception):
    """Custom exception for video selection errors."""

    pass


# Modify function signature to accept tracker
def select_stock_videos(
    audio_features: Dict[str, Any],
    query_keywords: List[str] = None,
    num_videos: int = 1,
    tracker: Optional[StockSuccessTracker] = None,  # Added tracker parameter
    release_id: Optional[Any] = None,  # Added release_id for logging usage later
) -> List[Dict[str, Any]]:
    """Selects stock videos from Pexels based on audio features, keywords, and tracker data.

    Args:
        audio_features: Dictionary containing audio analysis results (tempo, energy, duration).
        query_keywords: Optional list of additional keywords to guide the search (e.g., genre, mood).
        num_videos: The desired number of videos to select.
        tracker: (Optional) An instance of StockSuccessTracker to guide source selection and log usage.
        release_id: (Optional) The ID of the release this selection is for, used for logging clip usage.

    Returns:
        A list of dictionaries, each representing a selected Pexels video including download links.

    Raises:
        VideoSelectionError: If video selection fails due to API issues or lack of results.
    """
    logger.info(
        f"Starting video selection for release {release_id} based on audio features: {audio_features} and keywords: {query_keywords}"
    )

    # Initialize tracker if not provided (or handle error if required)
    if tracker is None:
        logger.warning(
            "No StockSuccessTracker provided. Performance-based source selection disabled."
        )
        # Create a dummy tracker to avoid errors later if methods are called
        tracker = StockSuccessTracker()

    # --- Determine Preferred Sources (Step 005) ---
    preferred_sources = []
    try:
        # Example: Get top sources from last 30 days
        preferred_sources = tracker.get_top_sources(days=30)
        if preferred_sources:
            logger.info(f"Tracker suggests preferred sources: {preferred_sources}")
        else:
            logger.info("Tracker has no preferred sources based on recent performance.")
    except StockTrackerError as e:
        logger.warning(
            f"Error getting top sources from tracker: {e}. Proceeding without preference."
        )
    except Exception as e:  # Catch unexpected tracker errors
        logger.error(f"Unexpected error interacting with tracker: {e}", exc_info=True)

    # --- Initialize API Clients (Modify to handle multiple sources later) ---
    # For now, we still only have Pexels
    clients = {}
    try:
        clients["pexels"] = PexelsClient()
        logger.debug("Initialized Pexels client.")
    except PexelsApiError as e:
        logger.error(f"Failed to initialize Pexels client: {e}")
        # If no clients can be initialized, raise error
        if not clients:
            raise VideoSelectionError(f"Failed to initialize any video source clients.")

    # --- Generate Search Query (Same as before) ---
    base_query_parts = []
    if query_keywords:
        base_query_parts.extend(query_keywords)

    # Map tempo/energy to descriptive keywords (simple example)
    tempo = audio_features.get("tempo", 120)  # Default to moderate tempo
    energy = audio_features.get("energy", 0.5)  # Default to moderate energy

    if tempo > 140:
        base_query_parts.append(
            random.choice(["fast", "energetic", "dynamic", "action"])
        )
    elif tempo < 90:
        base_query_parts.append(
            random.choice(["slow", "calm", "relaxing", "ambient", "serene"])
        )
    else:
        base_query_parts.append(
            random.choice(["moderate tempo", "steady rhythm", "flowing"])
        )

    if energy > 0.7:
        base_query_parts.append(
            random.choice(["intense", "powerful", "vibrant", "bright"])
        )
    elif energy < 0.3:
        base_query_parts.append(
            random.choice(["gentle", "soft", "subtle", "dark", "muted"])
        )

    # Remove duplicates and join
    final_query = " ".join(list(dict.fromkeys(base_query_parts)))
    if not final_query:
        logger.warning(
            "Could not generate a meaningful query from features/keywords. Using default 	abstract	."
        )
        final_query = "abstract"

    logger.info(f"Generated search query: 	{final_query}	")

    # --- Search Sources (Refactor for prioritization - Step 005/006) ---
    found_videos = []
    searched_sources_order = []

    # Prioritize sources from tracker
    if preferred_sources:
        # Ensure we only try sources we have clients for
        valid_preferred = [src for src in preferred_sources if src in clients]
        searched_sources_order.extend(valid_preferred)

    # Add remaining available clients (not in preferred list)
    remaining_clients = [src for src in clients if src not in searched_sources_order]
    random.shuffle(remaining_clients)  # Randomize fallback order
    searched_sources_order.extend(remaining_clients)

    logger.info(
        f"Search order based on tracker and availability: {searched_sources_order}"
    )

    videos_from_sources = {}  # Store results per source

    for source_name in searched_sources_order:
        client = clients[source_name]
        logger.info(f"Searching source: {source_name} with query: 	{final_query}	")
        try:
            # Assuming clients have a compatible search_videos method
            # TODO: Adapt this if client methods differ significantly
            if source_name == "pexels":
                search_results = client.search_videos(
                    query=final_query,
                    per_page=max(num_videos * 3, 15),
                    orientation=landscape,
                )
                source_videos = search_results.get("videos", [])
                logger.info(f"Found {len(source_videos)} videos from {source_name}.")
                if source_videos:
                    videos_from_sources[source_name] = source_videos
                    # If we found enough videos from a preferred source, maybe stop early?
                    # For now, let	 s search all available sources to get a wider pool.

            # Add elif blocks here for other clients (e.g., pixabay) if implemented

        except (
            PexelsApiError,
            Exception,
        ) as e:  # Catch specific client errors + general errors
            logger.warning(f"Error searching {source_name}: {e}. Skipping source.")
            continue  # Try next source

    # --- Fallback Query Logic (If initial search yields nothing) ---
    if not videos_from_sources:
        logger.warning(
            f"No videos found across sources for query: 	{final_query}	. Trying fallback queries."
        )
        fallback_queries = [
            "abstract background",
            "nature landscape",
            "city lights",
            "technology",
            "music visualization",
        ]
        random.shuffle(fallback_queries)

        for fallback_query in fallback_queries:
            logger.info(f"Attempting fallback query: 	{fallback_query}	")
            for (
                source_name
            ) in searched_sources_order:  # Try sources in the same preferred order
                client = clients[source_name]
                logger.info(
                    f"Searching source: {source_name} with fallback query: 	{fallback_query}	"
                )
                try:
                    if source_name == "pexels":
                        search_results = client.search_videos(
                            query=fallback_query,
                            per_page=max(num_videos * 3, 15),
                            orientation=landscape,
                        )
                        source_videos = search_results.get("videos", [])
                        logger.info(
                            f"Found {len(source_videos)} videos from {source_name} using fallback."
                        )
                        if source_videos:
                            videos_from_sources[source_name] = source_videos
                            # Found videos with fallback, break inner loop and outer loop
                            break
                    # Add elif for other clients
                except (PexelsApiError, Exception) as e:
                    logger.warning(
                        f"Error searching {source_name} with fallback query: {e}. Skipping source."
                    )
                    continue
            if (
                videos_from_sources
            ):  # If videos found with this fallback, stop trying other fallbacks
                break

    if not videos_from_sources:
        logger.error(
            f"No videos found even with fallback queries for audio features: {audio_features}"
        )
        raise VideoSelectionError(
            f"Could not find any suitable videos for query 	{final_query}	 or fallbacks across available sources."
        )

    # --- Select Videos (Refactor to prioritize sources - Step 005) ---
    # Combine videos from all sources, keeping track of the source
    all_potential_videos = []
    for source_name, source_videos in videos_from_sources.items():
        for video in source_videos:
            video[source] = source_name  # Add source information
            all_potential_videos.append(video)

    logger.info(f"Total potential videos gathered: {len(all_potential_videos)}")

    # Selection strategy: Prioritize videos from preferred sources first
    selected_videos_data = []
    preferred_pool = [v for v in all_potential_videos if v[source] in preferred_sources]
    fallback_pool = [
        v for v in all_potential_videos if v[source] not in preferred_sources
    ]

    # Shuffle within pools to maintain randomness
    random.shuffle(preferred_pool)
    random.shuffle(fallback_pool)

    # Fill selection from preferred pool first, then fallback pool
    combined_pool = preferred_pool + fallback_pool

    if len(combined_pool) < num_videos:
        logger.warning(
            f"Requested {num_videos} videos, but only {len(combined_pool)} were found/suitable. Returning all found."
        )
        num_videos = len(combined_pool)

    selected_videos_raw = combined_pool[:num_videos]

    # --- Format Selection & Log Usage (Step 007/008) ---
    final_selection = []
    for video in selected_videos_raw:
        source_name = video.get("source", "unknown")  # Get source name added earlier
        video_id = video.get("id")

        # Format the output dictionary (similar to before, but add source)
        video_files = video.get("video_files", [])
        hq_link_info = None
        if video_files:
            hq_link_info = max(
                video_files,
                key=lambda x: x.get(width, 0) * x.get(height, 0),
                default=None,
            )

        formatted_video = {
            "source": source_name,  # Ensure source is included
            "id": video_id,
            "url": video.get("url"),
            "width": video.get("width"),
            "height": video.get("height"),
            "duration": video.get("duration"),
            "photographer": video.get("user", {}).get("name"),
            "download_link": hq_link_info.get("link") if hq_link_info else None,
            "quality": hq_link_info.get("quality") if hq_link_info else None,
        }
        final_selection.append(formatted_video)

        # Log usage with the tracker (Step 007)
        if tracker and release_id and video_id:
            try:
                tracker.log_clip_usage(
                    release_id=release_id, source_name=source_name, clip_id=video_id
                )
                logger.debug(
                    f"Logged usage for clip {video_id} from {source_name} for release {release_id}"
                )
            except StockTrackerError as e:
                logger.warning(
                    f"Failed to log clip usage for {video_id} from {source_name}: {e}"
                )
            except Exception as e:
                logger.error(f"Unexpected error logging clip usage: {e}", exc_info=True)
        elif not tracker:
            logger.debug("Skipping usage logging as tracker is not available.")
        elif not release_id:
            logger.warning(
                f"Skipping usage logging for clip {video_id}: release_id not provided."
            )
        elif not video_id:
            logger.warning(
                f"Skipping usage logging for video from {source_name}: video ID not found."
            )

    logger.info(
        f"Final selected videos ({len(final_selection)}): {[v[	 id	] for v in final_selection]}"
    )
    return final_selection


# --- Update Example Usage ---
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # --- Mock StockSuccessTracker for testing ---
    class MockStockSuccessTracker(StockSuccessTracker):
        def __init__(self, top_sources=None):
            self._top_sources = top_sources if top_sources else []
            self.usage_log = []
            logger.info(f"[MockTracker] Initialized. Top sources: {self._top_sources}")

        def get_top_sources(
            self, genre: Optional[str] = None, days: int = 30
        ) -> List[str]:
            logger.info(
                f"[MockTracker] get_top_sources called (genre={genre}, days={days}). Returning: {self._top_sources}"
            )
            return self._top_sources

        def log_clip_usage(self, release_id: Any, source_name: str, clip_id: Any):
            log_entry = {
                "release_id": release_id,
                "source_name": source_name,
                "clip_id": clip_id,
            }
            self.usage_log.append(log_entry)
            logger.info(f"[MockTracker] log_clip_usage called: {log_entry}")

    # --- Test Scenarios ---
    test_features_energetic = {tempo: 150.0, energy: 0.8, duration: 180.0}
    test_keywords = ["electronic", "synthwave"]
    test_release_id = "test_release_001"

    print("\n--- Testing Energetic Track with Tracker (Pexels Preferred) --- ")
    # Scenario 1: Tracker prefers 	 pexels
    mock_tracker_pexels_pref = MockStockSuccessTracker(top_sources=["pexels"])
    try:
        selected = select_stock_videos(
            test_features_energetic,
            query_keywords=test_keywords,
            num_videos=2,
            tracker=mock_tracker_pexels_pref,
            release_id=test_release_id,
        )
        print("Selected Videos:")
        import json

        print(json.dumps(selected, indent=2))
        print("\nMock Tracker Usage Log:")
        print(json.dumps(mock_tracker_pexels_pref.usage_log, indent=2))
        # Verify source is likely pexels (though API might return nothing)
        if selected:
            print(f"Selected video sources: {[v.get(	 source	) for v in selected]}")

    except (VideoSelectionError, PexelsApiError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}", exc_info=True)

    print("\n--- Testing Energetic Track with Tracker (No Preference) --- ")
    # Scenario 2: Tracker has no preference or fails
    mock_tracker_no_pref = MockStockSuccessTracker(top_sources=[])
    try:
        selected = select_stock_videos(
            test_features_energetic,
            query_keywords=test_keywords,
            num_videos=1,
            tracker=mock_tracker_no_pref,
            release_id="test_release_002",
        )
        print("Selected Videos:")
        import json

        print(json.dumps(selected, indent=2))
        print("\nMock Tracker Usage Log:")
        print(json.dumps(mock_tracker_no_pref.usage_log, indent=2))
        if selected:
            print(f"Selected video sources: {[v.get(	 source	) for v in selected]}")

    except (VideoSelectionError, PexelsApiError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}", exc_info=True)

    # Note: Still requires PEXELS_API_KEY
