# Database Module

This module handles all interactions with the PostgreSQL database for the AI Artist System.

## Components

- **`connection_manager.py`**: Manages the PostgreSQL database connection pool using `psycopg2`.
- **`schema/`**: Contains SQL files defining the database table schemas:
    - `artist_profiles.sql`
    - `tracks.sql`
    - `country_profiles.sql`
    - `trend_analysis.sql`
    - `competitor_analysis.sql`
    - `performance_metrics.sql`
    - `evolution_plans.sql`
- **`utils/`**: Contains utility functions related to database operations (currently empty).

## Setup

1. Ensure PostgreSQL server is installed and running.
2. Create the database and user (see `phase1_db_setup_user_db_retry` shell command for example).
3. Set environment variables for database connection:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
4. Install required library: `pip install psycopg2-binary`

## Usage

Import the context managers from `connection_manager`:

```python
from ai_artist_system.noktvrn_ai_artist.database.connection_manager import init_connection_pool, close_connection_pool, get_db_cursor

# Initialize the pool at application startup
init_connection_pool()

# Use a cursor within a context manager
try:
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("INSERT INTO tracks (id, artist_id, title) VALUES (%s, %s, %s)", ("track123", "artist456", "New Song"))
except Exception as e:
    print(f"Database error: {e}")
finally:
    # Close the pool at application shutdown
    close_connection_pool()
```

