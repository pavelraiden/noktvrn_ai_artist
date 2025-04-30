import logging
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Define the path for the persistent stats file relative to the production_phase directory
STATS_FILE_PATH = "/home/ubuntu/production_phase/data/source_stats.json"

class StockSuccessTracker:
    """Tracks the usage and performance of stock video clips to rank sources."""

    def __init__(self, stats_file: str = STATS_FILE_PATH):
        """Initializes the tracker, loading existing stats if available."""
        self.stats_file = stats_file
        self.source_data = self._load_stats()
        # source_data structure: 
        # {
        #   "source_name": { # e.g., "pexels"
        #     "clips": {
        #       "clip_id_or_url": {
        #         "usage_count": 1,
        #         "releases": [release_id1, release_id2],
        #         "metrics": [
        #           {"release_id": release_id, "likes": 100, "watch_time_avg_sec": 30, "retention_pct": 50, "timestamp": "isoformat"},
        #           ...
        #         ]
        #       },
        #       ...
        #     },
        #     "aggregated_score": 0.0 # Calculated score based on metrics
        #   },
        #   ...
        # }

    def _load_stats(self) -> Dict[str, Any]:
        """Loads stats from the JSON file."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    logger.info(f"Loading stock success stats from {self.stats_file}")
                    return json.load(f)
            else:
                logger.info(f"Stats file {self.stats_file} not found. Starting fresh.")
                return defaultdict(lambda: {"clips": defaultdict(lambda: {"usage_count": 0, "releases": [], "metrics": []}), "aggregated_score": 0.0})
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading stats file {self.stats_file}: {e}. Starting fresh.", exc_info=True)
            return defaultdict(lambda: {"clips": defaultdict(lambda: {"usage_count": 0, "releases": [], "metrics": []}), "aggregated_score": 0.0})

    def _save_stats(self):
        """Saves the current stats to the JSON file."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.source_data, f, indent=2)
            logger.info(f"Successfully saved stock success stats to {self.stats_file}")
        except IOError as e:
            logger.error(f"Error saving stats file {self.stats_file}: {e}", exc_info=True)

    def log_clip_usage(self, release_id: Any, source_name: str, clip_id_or_url: str):
        """Logs that a specific clip from a source was used in a release."""
        logger.debug(f"Logging usage for clip 	{clip_id_or_url}	 from source 	{source_name}	 in release {release_id}")
        clip_data = self.source_data[source_name]["clips"][clip_id_or_url]
        clip_data["usage_count"] += 1
        if release_id not in clip_data["releases"]:
            clip_data["releases"].append(release_id)
        # Saving frequently might be inefficient, consider batching or saving on exit
        # For now, save after each significant update
        # self._save_stats() # Moved saving to metric logging and ranking update

    def log_clip_performance(self, release_id: Any, source_name: str, clip_id_or_url: str, likes: int, watch_time_avg_sec: float, retention_pct: float):
        """Logs mock performance metrics for a specific clip within a release."""
        logger.debug(f"Logging performance for clip 	{clip_id_or_url}	 from source 	{source_name}	 in release {release_id}")
        if source_name not in self.source_data or clip_id_or_url not in self.source_data[source_name]["clips"]:
            logger.warning(f"Attempted to log performance for clip 	{clip_id_or_url}	 from source 	{source_name}	 which has no usage logged. Logging usage first.")
            self.log_clip_usage(release_id, source_name, clip_id_or_url)
        
        metric_record = {
            "release_id": release_id,
            "likes": likes,
            "watch_time_avg_sec": watch_time_avg_sec,
            "retention_pct": retention_pct,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.source_data[source_name]["clips"][clip_id_or_url]["metrics"].append(metric_record)
        
        # Update ranking after adding new metrics
        self._update_ranking()
        self._save_stats()

    def _calculate_clip_score(self, metrics: List[Dict[str, Any]], days: Optional[int] = None) -> float:
        """Calculates a simple score based on recent metrics for a single clip."""
        score = 0
        count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=days) if days is not None else None

        for metric in metrics:
            metric_time = datetime.fromisoformat(metric["timestamp"]) 
            if cutoff_date and metric_time < cutoff_date:
                continue
            
            # Simple scoring: likes + retention + watch_time (adjust weights as needed)
            # Normalize or scale these values in a real scenario
            clip_score = metric.get("likes", 0) * 0.2 + metric.get("retention_pct", 0) * 0.5 + metric.get("watch_time_avg_sec", 0) * 0.3
            score += clip_score
            count += 1
            
        return score / count if count > 0 else 0

    def _update_ranking(self, days: Optional[int] = None):
        """Recalculates the aggregated score for each source based on recent clip performance."""
        logger.info(f"Updating source ranking, considering metrics from the last {days} days" if days else "Updating source ranking using all metrics")
        for source_name, source_info in self.source_data.items():
            total_score = 0
            scored_clips_count = 0
            for clip_id, clip_data in source_info["clips"].items():
                clip_score = self._calculate_clip_score(clip_data["metrics"], days)
                if clip_score > 0: # Only count clips with scores
                    total_score += clip_score
                    scored_clips_count += 1
            
            # Average score across all scored clips for the source
            source_info["aggregated_score"] = total_score / scored_clips_count if scored_clips_count > 0 else 0
            score = source_info["aggregated_score"]
            logger.debug(f"Source: {source_name}, Aggregated Score: {score:.2f}")

    def get_top_sources(self, genre: Optional[str] = None, days: int = 30) -> List[str]:
        """Returns a ranked list of source names based on recent performance.
        
        Args:
            genre: Optional genre filter (Not implemented in current scoring).
            days: How many recent days of metrics to consider for ranking.
            
        Returns:
            A list of source names, highest score first.
        """
        # Ensure rankings are up-to-date with the specified time window
        self._update_ranking(days=days)
        
        # Genre filtering is not implemented in this version
        if genre:
            logger.warning(f"Genre filtering (	{genre}	) is not implemented in get_top_sources.")

        # Sort sources by aggregated_score descending
        sorted_sources = sorted(self.source_data.items(), key=lambda item: item[1]["aggregated_score"], reverse=True)
        
        top_sources = [source_name for source_name, data in sorted_sources if data["aggregated_score"] > 0]
        logger.info(f"Top sources based on last {days} days: {top_sources}")
        return top_sources

# Example Usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Use a temporary file for testing
    TEST_STATS_FILE = "/tmp/test_source_stats.json"
    if os.path.exists(TEST_STATS_FILE):
        os.remove(TEST_STATS_FILE)
        
    tracker = StockSuccessTracker(stats_file=TEST_STATS_FILE)

    # Log some usage
    tracker.log_clip_usage(release_id="release_001", source_name="pexels", clip_id_or_url="pexels_vid_123")
    tracker.log_clip_usage(release_id="release_001", source_name="pexels", clip_id_or_url="pexels_vid_456")
    tracker.log_clip_usage(release_id="release_002", source_name="pixabay", clip_id_or_url="pixabay_vid_abc")
    tracker.log_clip_usage(release_id="release_002", source_name="pexels", clip_id_or_url="pexels_vid_123") # Used again

    # Log some performance (will trigger ranking update and save)
    tracker.log_clip_performance("release_001", "pexels", "pexels_vid_123", likes=150, watch_time_avg_sec=45, retention_pct=60)
    tracker.log_clip_performance("release_001", "pexels", "pexels_vid_456", likes=80, watch_time_avg_sec=25, retention_pct=40)
    tracker.log_clip_performance("release_002", "pixabay", "pixabay_vid_abc", likes=200, watch_time_avg_sec=55, retention_pct=70)
    tracker.log_clip_performance("release_002", "pexels", "pexels_vid_123", likes=180, watch_time_avg_sec=50, retention_pct=65) # Performance for second usage

    print("\n--- Current Stats ---")
    print(json.dumps(tracker.source_data, indent=2))

    print("\n--- Getting Top Sources (Last 30 days) ---")
    top = tracker.get_top_sources(days=30)
    print(f"Top sources: {top}")

    print("\n--- Getting Top Sources (All time) ---")
    top_all = tracker.get_top_sources(days=None) # Use None for all time
    print(f"Top sources (all time): {top_all}")

    # Verify file saved
    if os.path.exists(TEST_STATS_FILE):
        print(f"\nStats saved to {TEST_STATS_FILE}")
        # os.remove(TEST_STATS_FILE) # Clean up test file
    else:
        print(f"\nError: Stats file {TEST_STATS_FILE} not found.")

