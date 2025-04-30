# Artist Evolution Module

This module is responsible for adapting the AI artist's profile and generation parameters based on the performance of previously released content. It aims to guide the artist towards styles that resonate better with audiences over time.

## Components

*   `artist_evolution_service.py`: The core service orchestrating the evolution process.
    *   `analyze_performance_trends()`: Takes performance data (from `analytics.performance_db_service`) and identifies basic trends (e.g., highest performing metric).
    *   `apply_evolution_rules()`: Modifies the artist's profile (e.g., adds/removes keywords) based on the identified trends. Contains example rules.
    *   `evolve_artist()`: Main function that fetches the artist profile, retrieves performance data for their releases, analyzes trends, applies rules, updates the profile (via placeholder `artist_profile_manager`), and logs the change using `artist_progression_db_service`.
*   `style_adaptor.py`: Translates the evolved artist profile into concrete parameters for content generation.
    *   `adapt_generation_parameters()`: Takes the artist profile and generates specific modifiers for Suno prompts, Luma style references, and stock video search keywords.
*   `artist_progression_db_service.py`: Manages the logging of evolution events to the database.
    *   `apply_progression_schema()`: Applies the `artist_progression_log.sql` schema.
    *   `add_progression_log_entry()`: Inserts a record detailing the evolution event, the trigger (performance summary), and a snapshot of the profile after the change.
*   `../database/schema/artist_progression_log.sql`: Defines the PostgreSQL schema for the `artist_progression_log` table.
*   `artist_profile_manager.py` (Placeholder): This module is assumed to exist for managing artist profiles (CRUD operations), likely interacting with an `artists` table in the database. It's a crucial dependency for the evolution service.

## Usage

1.  Ensure database schemas (`approved_releases`, `content_performance`, `artist_progression_log`, and the assumed `artists` schema) are applied.
2.  Ensure performance data is being collected for releases.
3.  Periodically call `artist_evolution_service.evolve_artist(artist_id)` for each active artist.
4.  The `evolve_artist` function will update the artist's profile and log the change.
5.  When generating new content for an artist, fetch their latest profile and use `style_adaptor.adapt_generation_parameters(profile)` to get tailored parameters for the generation services (Suno, Luma, Pexels via `video_selector`).

## Dependencies

*   `../analytics/performance_db_service.py`
*   `../database/connection_manager.py`
*   `artist_profile_manager.py` (Placeholder/Assumed)
*   `datetime`
*   `random`

## Future Enhancements

*   Implement the `artist_profile_manager`.
*   Develop more sophisticated trend analysis in `analyze_performance_trends` (e.g., time-series analysis, genre correlation).
*   Create more nuanced evolution rules in `apply_evolution_rules`.
*   Refine parameter adaptation in `style_adaptor` based on feedback from generation services.
*   Add UI elements to visualize artist progression logs.

