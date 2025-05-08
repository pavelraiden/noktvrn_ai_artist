# Module: Database Connection Manager

*   **File:** `noktvrn_ai_artist/database/connection_manager.py`

## Role

Manages the connection pool to the PostgreSQL database. It provides a centralized way for other services to obtain database connections and cursors, ensuring efficient connection handling.

## Inputs

*   Configuration details (implicitly via environment variables like `DATABASE_URL` used by `psycopg2` or the pooling mechanism).
*   Method `get_connection()`: No direct inputs.
*   Method `release_connection(conn)`: The connection object to return to the pool.
*   Method `execute_query(query, params=None, fetch=False)`: SQL query string, optional parameters, and a flag indicating if results should be fetched.
*   Method `execute_script(script_path)`: Path to an SQL script file.

## Outputs

*   Method `get_connection()`: A database connection object from the pool.
*   Method `execute_query()`: Query results if `fetch=True`, otherwise None.
*   Method `execute_script()`: None (logs success or errors).

## Usage

*   Used by various database service modules (`Performance DB Service`, `Artist Progression DB Service`, Streamlit `Database Service`) to interact with the database.
*   Initializes a connection pool on startup.
*   Provides methods for executing individual queries or entire SQL scripts.

## Status

*   **Core:** Fundamental component for all database interactions.
*   **Implemented:** Core functionality using `psycopg2` connection pooling is implemented.
