# Module: Suno API Client

*   **File:** `noktvrn_ai_artist/api_clients/suno_client.py`

## Role

Provides an interface to interact with the Suno API for generating music tracks based on provided prompts and parameters.

## Inputs

*   **Method `generate_track`:**
    *   `prompt` (str): Text prompt describing the desired music (e.g., genre, mood, lyrics).
    *   `style_of_music` (str, optional): Specific style guidance.
    *   `make_instrumental` (bool, optional): Whether to generate an instrumental track.
    *   `wait_audio` (bool, optional): Whether to wait for the audio generation to complete.
*   **Method `get_track`:**
    *   `track_id` (str): The ID of the track to retrieve information for.

## Outputs

*   **Method `generate_track`:** A dictionary containing the API response, typically including track IDs and metadata. Returns None on failure.
*   **Method `get_track`:** A dictionary containing details about the specified track, including its status and potentially the audio URL if completed. Returns None on failure.

## Usage

*   Used by the `Content Generation Flow` (conceptual) or relevant service as part of the `Artist Content Generation Pipeline` to create new music tracks.
*   Requires a Suno API key/cookie, which should be configured via environment variables (`SUNO_COOKIE`).
*   Relies on an underlying unofficial Suno API library (`suno-api`).

## Status

*   **Core:** Essential for the music generation part of the content pipeline.
*   **Implemented:** Basic client wrapping an unofficial Suno API library is implemented.
