import logging
import random
from typing import List, Dict, Any, Optional
import json # Added

# Import the tracker
try:
    # Adjusted relative import path assuming video_processing is a sibling to analytics
    from ..analytics.stock_success_tracker import (
        StockSuccessTracker,
        StockTrackerError,
    )
except (ImportError, ValueError): # Catch ValueError for potential relative import issues
    logging.warning(
        "Failed to import StockSuccessTracker. "
        "Performance-based source selection disabled."
    )

    # Define dummy tracker if import fails
    class StockSuccessTracker:
        def get_top_sources(
            self, genre: Optional[str] = None, days: int = 30
        ) -> List[str]:
            return []

        def log_clip_usage(
            self, release_id: Any, source_name: str, clip_id: Any
        ):
            pass

    class StockTrackerError(Exception):
        pass

# Import API clients
try:
    from ..api_clients.pexels_client import PexelsClient, PexelsApiError
except (ImportError, ValueError):
    logging.warning("Failed to import PexelsClient.")
    class PexelsClient:
        def search_videos(self, *args, **kwargs):
            return {}
    class PexelsApiError(Exception):
        pass

# Removed unused AudioAnalysisError import

logger = logging.getLogger(__name__)


class VideoSelectionError(Exception):
    """Custom exception for video selection errors."""
    pass


# Modify function signature to accept tracker
def select_stock_videos(
    audio_features: Dict[str, Any],
    query_keywords: Optional[List[str]] = None, # Made keywords optional
    num_videos: int = 1,
    tracker: Optional[StockSuccessTracker] = None,  # Added tracker parameter
    release_id: Optional[Any] = None,  # Added release_id for logging usage later
) -> List[Dict[str, Any]]:
    """Selects stock videos based on audio features, keywords, and tracker data.

    Args:
        audio_features: Dict containing audio analysis results (tempo, energy,
            duration).
        query_keywords:
            Optional list of additional keywords to guide the search.
        num_videos: The desired number of videos to select.
        tracker: (Optional) An instance of StockSuccessTracker.
        release_id: (Optional) The ID of the release for logging clip usage.

    Returns:
        A list of dictionaries, each representing a selected video.

    Raises:
        VideoSelectionError: If video selection fails.
    """
    if query_keywords is None:
        query_keywords = [] # Ensure query_keywords is a list

    logger.info(
        f"Starting video selection for release {release_id} based on "
        f"audio features: {audio_features} and keywords: {query_keywords}"
    )

    # Initialize tracker if not provided
    if tracker is None:
        logger.warning(
            "No StockSuccessTracker provided. "
            "Performance-based source selection disabled."
        )
        tracker = StockSuccessTracker()  # Use dummy tracker

    # --- Determine Preferred Sources ---
    preferred_sources = []
    try:
        preferred_sources = tracker.get_top_sources(days=30)
        if preferred_sources:
            logger.info(
                f"Tracker suggests preferred sources: {preferred_sources}"
            )
        else:
            logger.info(
                "Tracker has no preferred sources based on recent performance."
            )
    except StockTrackerError as e:
        logger.warning(
            f"Error getting top sources from tracker: {e}. Proceeding without preference."
        )
    except Exception as e:
        logger.error(
            f"Unexpected error interacting with tracker: {e}", exc_info=True
        )

    # --- Initialize API Clients ---
    clients = {}
    try:
        clients["pexels"] = PexelsClient()
        logger.debug("Initialized Pexels client.")
    except PexelsApiError as e:
        logger.error(f"Failed to initialize Pexels client: {e}")
        # No need to check if clients is empty here, handled later
    except NameError:
         logger.error("PexelsClient class not available.")

    if not clients:
        raise VideoSelectionError(
            "Failed to initialize any video source clients."
        )

    # --- Generate Search Query ---
    base_query_parts = []
    if query_keywords:
        base_query_parts.extend(query_keywords)

    tempo = audio_features.get("tempo", 120)
    energy = audio_features.get("energy", 0.5)

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

    # Remove duplicates while preserving order (Python 3.7+)
    final_query_parts = list(dict.fromkeys(base_query_parts))
    final_query = " ".join(final_query_parts)

    if not final_query:
        logger.warning(
            "Could not generate query from features/keywords. Using default 'abstract'."
        )
        final_query = "abstract"

    logger.info(f"Generated search query: \"{final_query}\"")

    # --- Search Sources ---
    searched_sources_order = []
    if preferred_sources:
        valid_preferred = [src for src in preferred_sources if src in clients]
        searched_sources_order.extend(valid_preferred)

    remaining_clients = [
        src for src in clients if src not in searched_sources_order
    ]
    random.shuffle(remaining_clients)
    searched_sources_order.extend(remaining_clients)

    logger.info(f"Search order: {searched_sources_order}")

    videos_from_sources = {}
    for source_name in searched_sources_order:
        client = clients[source_name]
        logger.info(f"Searching {source_name} with query: \"{final_query}\"")
        try:
            if source_name == "pexels":
                search_results = client.search_videos(
                    query=final_query,
                    per_page=max(num_videos * 3, 15),
                    orientation="landscape",
                )
                source_videos = search_results.get("videos", [])
                logger.info(
                    f"Found {len(source_videos)} videos from {source_name}."
                )
                if source_videos:
                    videos_from_sources[source_name] = source_videos
            # Add elif for other clients if needed
        except (PexelsApiError, Exception) as e:
            logger.warning(f"Error searching {source_name}: {e}. Skipping.")
            continue

    # --- Fallback Query Logic ---
    if not videos_from_sources:
        logger.warning(
            f"No videos found for query: \"{final_query}\". Trying fallbacks."
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
            logger.info(f"Attempting fallback query: \"{fallback_query}\"")
            for source_name in searched_sources_order:
                client = clients[source_name]
                logger.info(
                    f"Searching {source_name} with fallback: \"{fallback_query}\""
                )
                try:
                    if source_name == "pexels":
                        search_results = client.search_videos(
                            query=fallback_query,
                            per_page=max(num_videos * 3, 15),
                            orientation="landscape",
                        )
                        source_videos = search_results.get("videos", [])
                        logger.info(
                            f"Found {len(source_videos)} videos from "
                            f"{source_name} (fallback)."
                        )
                        if source_videos:
                            videos_from_sources[source_name] = source_videos
                            break  # Found videos, break inner loop
                    # Add elif for other clients
                except (PexelsApiError, Exception) as e:
                    logger.warning(
                        f"Error searching {source_name} with fallback: {e}. Skipping."
                    )
                    continue
            if videos_from_sources:
                break  # Found videos, break outer loop

    if not videos_from_sources:
        logger.error(
            f"No videos found even with fallbacks for features: {audio_features}"
        )
        raise VideoSelectionError(
            f"Could not find videos for query \"{final_query}\" or fallbacks."
        )

    # --- Select Videos ---
    all_potential_videos = []
    for source_name, source_videos in videos_from_sources.items():
        for video in source_videos:
            # Ensure video is a dictionary before adding source
            if isinstance(video, dict):
                video["source"] = source_name
                all_potential_videos.append(video)
            else:
                logger.warning(f"Skipping non-dict item from {source_name}: {type(video)}")


    logger.info(
        f"Total potential videos gathered: {len(all_potential_videos)}"
    )

    # Filter pools based on source
    preferred_pool = [
        v for v in all_potential_videos if v.get("source") in preferred_sources
    ]
    fallback_pool = [
        v for v in all_potential_videos if v.get("source") not in preferred_sources
    ]

    random.shuffle(preferred_pool)
    random.shuffle(fallback_pool)

    combined_pool = preferred_pool + fallback_pool

    if not combined_pool:
         raise VideoSelectionError("No valid videos found after filtering.")

    if len(combined_pool) < num_videos:
        logger.warning(
            f"Requested {num_videos} videos, but only {len(combined_pool)} found. "
            "Returning all found."
        )
        num_to_select = len(combined_pool)
    else:
        num_to_select = num_videos

    selected_videos_raw = combined_pool[:num_to_select]

    # --- Format Selection & Log Usage ---
    final_selection = []
    for video in selected_videos_raw:
        source_name = video.get("source", "unknown")
        video_id = video.get("id")

        video_files = video.get("video_files", [])
        hq_link_info = None
        if video_files and isinstance(video_files, list):
            # Find the video file with the highest resolution (width * height)
            valid_files = [f for f in video_files if isinstance(f, dict)]
            if valid_files:
                hq_link_info = max(
                    valid_files,
                    key=lambda x: x.get("width", 0) * x.get("height", 0),
                    default=None, # Should not happen if valid_files is not empty
                )
            else:
                 logger.warning(f"No valid dictionary items found in video_files for video {video_id}")
        elif not isinstance(video_files, list):
             logger.warning(f"video_files is not a list for video {video_id}: {type(video_files)}")

        formatted_video = {
            "source": source_name,
            "id": video_id,
            "url": video.get("url"),
            "width": video.get("width"),
            "height": video.get("height"),
            "duration": video.get("duration"),
            "photographer": video.get("user", {}).get("name"),
            "download_link": (
                hq_link_info.get("link") if hq_link_info else None
            ),
            "quality": hq_link_info.get("quality") if hq_link_info else None,
        }
        final_selection.append(formatted_video)

        # Log usage with the tracker
        if tracker and release_id and video_id:
            try:
                tracker.log_clip_usage(
                    release_id=release_id,
                    source_name=source_name,
                    clip_id=video_id,
                )
                logger.debug(
                    f"Logged usage for clip {video_id} from {source_name} "
                    f"for release {release_id}"
                )
            except StockTrackerError as e:
                logger.warning(
                    f"Failed to log clip usage for {video_id} from {source_name}: {e}"
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error logging clip usage: {e}", exc_info=True
                )
        elif not tracker:
            logger.debug("Skipping usage logging: tracker not available.")
        elif not release_id:
            logger.warning(
                f"Skipping usage logging for clip {video_id}: no release_id."
            )
        elif not video_id:
            logger.warning(
                f"Skipping usage logging from {source_name}: no video ID."
            )

    logger.info(
        f"Final selected videos ({len(final_selection)}): {[v.get('id') for v in final_selection]}"
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
            logger.info(
                f"[MockTracker] Initialized. Top sources: {self._top_sources}"
            )

        def get_top_sources(
            self, genre: Optional[str] = None, days: int = 30
        ) -> List[str]:
            logger.info(
                f"[MockTracker] get_top_sources called (genre={genre}, days={days}). "
                f"Returning: {self._top_sources}"
            )
            return self._top_sources

        def log_clip_usage(
            self, release_id: Any, source_name: str, clip_id: Any
        ):
            log_entry = {
                "release_id": release_id,
                "source_name": source_name,
                "clip_id": clip_id,
            }
            self.usage_log.append(log_entry)
            logger.info(f"[MockTracker] log_clip_usage called: {log_entry}")

    # --- Test Scenarios ---
    test_features_energetic = {
        "tempo": 150.0,
        "energy": 0.8,
        "duration": 180.0,
    }
    test_keywords = ["electronic", "synthwave"]
    test_release_id = "test_release_001"

    print("\n--- Testing Energetic Track with Tracker (Pexels Preferred) --- ")
    # Scenario 1: Tracker prefers "pexels"
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
        print(json.dumps(selected, indent=2))
        print("\nMock Tracker Usage Log:")
        print(json.dumps(mock_tracker_pexels_pref.usage_log, indent=2))
        # Verify source preference if possible (depends on Pexels results)
        if selected:
            print(
                f"Selected video sources: {[v.get('source') for v in selected]}"
            )

    except VideoSelectionError as e:
        print(f"Video selection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error("Unexpected error during test", exc_info=True)

    print("\n--- Testing Calm Track without Tracker --- ")
    # Scenario 2: No tracker, calm features
    test_features_calm = {"tempo": 80.0, "energy": 0.2, "duration": 240.0}
    try:
        selected = select_stock_videos(
            test_features_calm,
            query_keywords=["ambient", "nature"],
            num_videos=1,
            # No tracker passed
            release_id="test_release_002"
        )
        print("Selected Videos:")
        print(json.dumps(selected, indent=2))
        if selected:
            print(
                f"Selected video sources: {[v.get('source') for v in selected]}"
            )
    except VideoSelectionError as e:
        print(f"Video selection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error("Unexpected error during test", exc_info=True)

    print("\n--- Testing with No Results Scenario (using unlikely query) --- ")
    # Scenario 3: Query likely to yield no results, triggering fallback
    try:
        selected = select_stock_videos(
            test_features_calm, # Use calm features
            query_keywords=["nonexistentkeywordxyz", "anotheroneabc"],
            num_videos=1,
            release_id="test_release_003"
        )
        print("Selected Videos (should be from fallback):")
        print(json.dumps(selected, indent=2))
        if selected:
            print(
                f"Selected video sources: {[v.get('source') for v in selected]}"
            )
    except VideoSelectionError as e:
        print(f"Video selection failed as expected (or fallback failed): {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error("Unexpected error during test", exc_info=True)

