# API Clients Module

This module contains clients for interacting with external APIs used by the AI Artist Platform.

## Existing Clients

*   `base_client.py`: Provides a base class for API clients, handling common functionalities like request retries and error handling.
*   `suno_client.py`: Client for interacting with the Suno API (for track generation).

## New Clients (Production Phase)

*   `pexels_client.py`: Client for interacting with the Pexels API (for stock video search and retrieval).
    *   **Initialization**: Requires a Pexels API key (obtained from Pexels).
    *   **Key Methods**:
        *   `search_videos(query, orientation=	landscape	, size=	medium	, per_page=15)`: Searches for videos based on a query string and optional parameters. Returns a list of video dictionaries containing URLs and metadata.
        *   Handles pagination (though currently fetches only the first page by default).
        *   Includes error handling for API requests.

## Usage

1.  Obtain necessary API keys for each service (Suno, Pexels).
2.  Set the API keys as environment variables (e.g., `PEXELS_API_KEY`).
3.  Import the desired client (e.g., `from noktvrn_ai_artist.api_clients.pexels_client import PexelsClient`).
4.  Instantiate the client: `pexels = PexelsClient()`.
5.  Call the client methods (e.g., `videos = pexels.search_videos(query="nature sunset")`).

## Dependencies

*   `requests` (via `base_client`)
*   `pexels-api-py` (specifically for `pexels_client`)
*   `python-dotenv` (for loading API keys from `.env`)

## Configuration

API keys should be stored securely, preferably using environment variables or a secret management system. The `.env` file is used for local development convenience.

