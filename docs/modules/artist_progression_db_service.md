# Module: Artist Progression DB Service

*   **File:** `noktvrn_ai_artist/artist_evolution/artist_progression_db_service.py`

## Role

Provides an interface for interacting with the `artist_progression_log` table in the PostgreSQL database. It handles applying the relevant schema and inserting new log entries that track the evolution of an artist over time.

## Inputs

*   **Method `apply_progression_schema`:** None (reads schema from `../database/schema/artist_progression_log.sql`).
*   **Method `add_progression_log_entry`:**
    *   `artist_id` (int): The ID of the artist being logged.
    *   `event_description` (str): A textual description of the evolution event (e.g., rule applied, parameter changed).
    *   `performance_summary` (str, optional): A summary of the performance data that triggered or influenced the event.
    *   `profile_snapshot` (dict, optional): A JSON snapshot of the artist's profile *after* the change occurred.

## Outputs

*   **Method `apply_progression_schema`:** None (applies schema to DB).
*   **Method `add_progression_log_entry`:** The integer ID of the newly inserted log entry in the `artist_progression_log` table.

## Connections / Usage

*   Used by the `Artist Evolution Service` (`artist_evolution/artist_evolution_service.py`) to record changes made to an artist's profile during the evolution process.
*   Relies on the `Database Connection Manager` (`database/connection_manager.py`) to obtain database cursors.
*   Reads the SQL schema definition from `database/schema/artist_progression_log.sql`.

## Status

*   **Core:** Essential for tracking and auditing the self-learning and adaptation process of artists.
*   **Implemented:** Core functionality for applying schema and inserting log entries is implemented.
