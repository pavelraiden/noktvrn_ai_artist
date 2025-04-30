# Analytics Module

This module handles the tracking, storage, and visualization of content performance data for the AI Artist Platform.

## Components

### Backend (`noktvrn_ai_artist/analytics`)

*   `performance_db_service.py`: Provides functions to interact with the `content_performance` database table.
    *   `apply_schema()`: Applies the `content_performance.sql` schema.
    *   `add_performance_metric()`: Inserts a new performance metric record (e.g., views, likes for a specific release on a platform).
    *   `get_performance_metrics_for_release()`: Retrieves all performance metrics for a given release ID.
    *   Includes `PerformanceDbError` for exception handling.
*   `../database/schema/content_performance.sql`: Defines the PostgreSQL schema for the `content_performance` table, which stores metrics like `release_id`, `platform`, `metric_type`, `metric_value`, and `recorded_at`.

### Frontend (`streamlit_app/analytics`)

*   `dashboard.py`: Implements `show_analytics_dashboard()`, a Streamlit component that displays performance metrics.
    *   Allows users to select an approved release.
    *   Fetches data using `performance_db_service`.
    *   Visualizes data using Pandas and Plotly Express (e.g., time-series charts, bar charts).
*   `data_entry.py`: Implements `show_performance_data_entry_form()`, a Streamlit component for manually entering performance data.
    *   Provides a form to input platform, metric type, value, etc., for a selected release.
    *   Saves the data using `performance_db_service.add_performance_metric()`.

## Usage

1.  Ensure the database is set up and the connection pool is initialized (`connection_manager.py`).
2.  Apply the schema using `performance_db_service.apply_schema()`.
3.  Use `add_performance_metric()` to record data (either manually via the data entry form or potentially via automated scripts in the future).
4.  Integrate `show_analytics_dashboard()` and `show_performance_data_entry_form()` into the main Streamlit application (`app.py`) to provide UI access.

## Dependencies

*   `psycopg2-binary` (via `connection_manager`)
*   `streamlit`
*   `pandas`
*   `plotly-express`
*   `../database/connection_manager.py`

## Future Enhancements

*   Automated data collection from platforms (YouTube API, Spotify API, etc.).
*   More sophisticated analytics and visualizations in the dashboard.
*   Integration with the `approved_releases` table/service for release selection (currently uses placeholders).

