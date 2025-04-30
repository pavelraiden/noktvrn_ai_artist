# Module: Luma API Client

*   **File:** `noktvrn_ai_artist/api_clients/luma_client.py`

## Role

Provides an interface to interact with the Luma Labs API for generating videos based on text prompts or potentially image inputs (though current implementation focuses on text-to-video).

## Inputs

*   **Method `generate_video`:**
    *   `prompt` (str): Text prompt describing the desired video content.
    *   `aspect_ratio` (str, optional): Desired aspect ratio (e.g., "16:9").
    *   `expand_prompt` (bool, optional): Whether Luma should expand the prompt internally.
*   **Method `get_video_status`:**
    *   `video_id` (str): The ID of the video generation task to check.

## Outputs

*   **Method `generate_video`:** A dictionary containing the API response, typically including the ID of the generation task. Returns None on failure.
*   **Method `get_video_status`:** A dictionary containing details about the specified video generation task, including its status (e.g., "pending", "processing", "completed") and potentially the video URL if completed. Returns None on failure.

## Usage

*   Used by the `Content Generation Flow` (conceptual) or relevant service as part of the `Artist Content Generation Pipeline` to create videos from prompts.
*   Requires a Luma API key, which should be configured via environment variables (`LUMA_API_KEY`).
*   Relies on direct HTTP requests using the `requests` library.

## Status

*   **Core:** Essential for the AI-generated video part of the content pipeline.
*   **Implemented:** Basic client using direct API calls is implemented.
