# Module: Video Selector

*   **File:** `noktvrn_ai_artist/video_processing/video_selector.py`

## Role

Selects appropriate stock video footage from Pexels based on audio analysis features and artist profile information. It incorporates performance data from the `Stock Success Tracker` to prioritize video sources.

## Inputs

*   `audio_features` (dict): A dictionary containing features extracted from the audio track by the `Audio Analyzer` (e.g., tempo, mood, energy, keywords).
*   `artist_profile` (dict - conceptual): Information about the artist, potentially including visual style keywords or themes.
*   `stock_tracker` (StockSuccessTracker instance): An instance of the tracker to get source preferences.
*   `pexels_client` (PexelsClient instance): An instance of the Pexels API client for searching videos.

## Outputs

*   `selected_video_url` (str or None): The URL of the selected Pexels video that best matches the inputs, or None if no suitable video is found.
*   `selected_source` (str or None): The name of the source (e.g., "pexels") from which the video was selected.

## Usage

*   Called by the `Content Generation Flow` (conceptual) or relevant service as part of the `Artist Content Generation Pipeline` after track generation and audio analysis.
*   Uses the `Pexels API Client` to search for videos.
*   Uses the `Stock Success Tracker` to get prioritized sources.
*   Logs the usage of the selected clip source back to the `Stock Success Tracker`.

## Status

*   **Core:** Essential for the stock video part of the content generation pipeline.
*   **Implemented:** The core logic for searching Pexels based on audio features and prioritizing based on the stock tracker is implemented.
