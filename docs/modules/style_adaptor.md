# Module: Style Adaptor

*   **File:** `noktvrn_ai_artist/artist_evolution/style_adaptor.py`

## Role

Translates high-level artist profile characteristics and evolution directives into concrete, actionable parameters suitable for use by content generation APIs (Suno, Luma) and stock footage selection logic (Pexels).

## Inputs

*   `artist_profile` (dict - conceptual): The current state of the artist, including genre, themes, visual style, target audience, historical parameters, etc.
*   `evolution_directives` (dict, optional): Specific changes or directions proposed by the `Artist Evolution Service` (e.g., "increase tempo", "explore adjacent genre X", "focus on visual theme Y").

## Outputs

*   `generation_params` (dict): A dictionary containing specific parameters ready for use by downstream services:
    *   `suno_params` (dict): Parameters for the Suno API client (e.g., prompt, style_of_music, tempo).
    *   `luma_params` (dict): Parameters for the Luma API client (e.g., user_prompt, aspect_ratio).
    *   `pexels_params` (dict): Keywords or search parameters for the Pexels API client.

## Usage

*   Called by the `Artist Evolution Service` after the artist profile has been updated.
*   Takes the potentially abstract profile information and evolution goals.
*   Applies logic (potentially including simple rules or even LLM calls in the future) to convert these into specific prompts, keywords, and settings for the generation APIs.
*   The output parameters are then passed to the `Content Generation Pipeline`.

## Status

*   **Core:** Essential bridge between the abstract artist profile/evolution logic and the concrete requirements of generation tools.
*   **Implemented:** Basic implementation exists, likely using rule-based logic to adapt parameters based on profile fields.
