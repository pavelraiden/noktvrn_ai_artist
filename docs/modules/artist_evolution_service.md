# Module: Artist Evolution Service

*   **File:** `noktvrn_ai_artist/artist_evolution/artist_evolution_service.py`

## Role

Orchestrates the evolution process for an AI artist. It analyzes content performance, applies evolution rules (reinforcement/diversification), updates the artist's profile, and logs the progression.

## Inputs

*   `artist_id` (int): The ID of the artist to evolve.
*   `performance_data` (list): Performance metrics for the artist's recent content, typically retrieved via `Performance DB Service`.
*   `artist_profile` (dict - conceptual): The current state of the artist (genre, themes, parameters, prompt history, etc.).

## Outputs

*   `updated_artist_profile` (dict - conceptual): The modified artist profile after applying evolution rules.
*   Logs changes to the `artist_progression_log` table via `Artist Progression DB Service`.
*   Potentially triggers the content generation pipeline with updated parameters (via `Style Adaptor`).

## Usage

*   Intended to be run periodically (e.g., scheduled task) or triggered based on certain conditions (e.g., performance thresholds met, manual trigger).
*   Retrieves data using `Performance DB Service`.
*   Calculates release effectiveness scores (`score_release_effectiveness`).
*   Applies evolution rules (`apply_evolution_rules`) based on scores.
*   Updates the conceptual artist profile.
*   Logs changes using `Artist Progression DB Service`.
*   Interacts with `Style Adaptor` to translate profile changes into generation parameters.

## Status

*   **Core:** Central to the platform's self-learning and adaptation capabilities.
*   **Implemented:** Core logic for scoring, applying rules (reinforcement/diversification based on scores and prompt history), and interacting with DB services is implemented.
