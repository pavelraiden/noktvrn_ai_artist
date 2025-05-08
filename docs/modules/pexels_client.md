# Module: Pexels API Client

*   **File:** `noktvrn_ai_artist/api_clients/pexels_client.py`

## Role

Provides an interface to interact with the Pexels API, specifically for searching and retrieving information about stock videos.

## Inputs

*   **Method `search_videos`:**
    *   `query` (str): The search term(s) for videos.
    *   `per_page` (int, optional): Number of results per page.
    *   `page` (int, optional): Page number to retrieve.
    *   `orientation` (str, optional): Desired video orientation ("landscape", "portrait", "square").
    *   `size` (str, optional): Minimum video size ("large", "medium", "small").

## Outputs

*   **Method `search_videos`:** A dictionary containing the API response, typically including a list of video objects with details like URLs, duration, user, etc. Returns None if the API key is missing or an error occurs.

## Usage

*   Used by the `Video Selector` (`video_processing/video_selector.py`) to find stock videos based on keywords derived from audio analysis or artist profile.
*   Requires a Pexels API key, which should be configured via environment variables (`PEXELS_API_KEY`).

## Status

*   **Core:** Essential for the stock video selection part of the content generation pipeline.
*   **Implemented:** Basic client using the `pexels-api-py` library is implemented.
