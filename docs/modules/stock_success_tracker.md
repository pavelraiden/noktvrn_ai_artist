# Module: Stock Success Tracker

*   **File:** `noktvrn_ai_artist/analytics/stock_success_tracker.py`

## Role

Tracks the usage and inferred performance of stock video clips used in generated content. It maintains statistics on different sources (e.g., Pexels) and provides rankings to prioritize sources that have historically correlated with better performance (using a time-decay mechanism).

## Inputs

*   **Method `log_clip_usage`:**
    *   `source_name` (str): The name of the stock video source (e.g., "pexels").
    *   `clip_id` (str): A unique identifier for the specific clip used.
    *   `release_id` (int): The ID of the release the clip was used in.
*   **Method `log_release_performance`:**
    *   `release_id` (int): The ID of the release.
    *   `performance_score` (float): A score representing the release's performance (e.g., derived from views, likes).
*   **Method `get_top_sources`:**
    *   `top_n` (int, optional): The number of top sources to return (defaults to 3).

## Outputs

*   **Method `log_clip_usage` / `log_release_performance`:** Updates internal statistics stored in a JSON file (`source_stats.json` by default).
*   **Method `get_top_sources`:** A list of source names (str) ranked by their aggregated performance score, up to `top_n` sources.

## Usage

*   Used by the `Video Selector` (`video_processing/video_selector.py`) to get prioritized source recommendations before searching for stock videos.
*   The `Video Selector` also calls `log_clip_usage` after selecting a clip.
*   The `log_release_performance` method is intended to be called by a process that monitors content performance (e.g., potentially linked to the `Performance DB Service` or `Artist Evolution Service`) to feed performance data back into the tracker.
*   Persists its state to a JSON file.

## Status

*   **Core:** Important for optimizing the stock video selection process based on performance feedback.
*   **Implemented:** Core logic for tracking usage, associating performance (mocked in current tests), calculating scores with time decay, and ranking sources is implemented.
