# Module: Performance DB Service

*   **File:** `noktvrn_ai_artist/analytics/performance_db_service.py`

## Role

Provides an interface for interacting with the `content_performance` table in the PostgreSQL database. It handles inserting new performance records and retrieving performance data for analysis.

## Inputs

*   **Method `insert_performance_record`:**
    *   `release_id` (int): The ID of the approved release.
    *   `platform` (str): The platform where performance is measured (e.g., "YouTube", "Spotify").
    *   `metric_name` (str): The name of the performance metric (e.g., "views", "likes", "listen_time").
    *   `metric_value` (float or int): The value of the metric.
    *   `recorded_at` (datetime, optional): Timestamp when the metric was recorded (defaults to now).
*   **Method `get_performance_data`:**
    *   `artist_id` (int, optional): Filter data by artist ID.
    *   `release_id` (int, optional): Filter data by release ID.
    *   `platform` (str, optional): Filter data by platform.
    *   `start_date` (datetime, optional): Filter data recorded after this date.
    *   `end_date` (datetime, optional): Filter data recorded before this date.

## Outputs

*   **Method `insert_performance_record`:** None (or Boolean indicating success/failure).
*   **Method `get_performance_data`:** A list of dictionaries, where each dictionary represents a performance record matching the query criteria.

## Usage

*   Used by the `Artist Evolution Service` to retrieve performance data for analysis.
*   Used by the Streamlit `Analytics Dashboard` (`streamlit_app/analytics/dashboard.py`) to display performance metrics.
*   Used by the Streamlit `Data Entry` component (`streamlit_app/analytics/data_entry.py`) to insert new performance data (potentially from external sources or manual input).
*   Relies on the `Database Connection Manager` (`database/connection_manager.py`) to manage database connections.

## Status

*   **Core:** Essential for the self-learning loop and performance tracking.
*   **Implemented:** Core functionality for inserting and retrieving data is implemented.
