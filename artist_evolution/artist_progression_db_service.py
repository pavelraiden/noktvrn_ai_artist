import logging
import os
import json
from typing import Dict, Any, Optional

# Adjust import path based on actual structure
try:
    from ..database.connection_manager import get_db_cursor, init_connection_pool, close_connection_pool
except ImportError:
    logging.warning("Progression DB Service: Failed to import DB connection manager.")
    # Define dummy context manager if import fails
    from contextlib import contextmanager
    @contextmanager
    def get_db_cursor(commit=False):
        yield None # Or raise an error
    def init_connection_pool(): pass
    def close_connection_pool(): pass

logger = logging.getLogger(__name__)

class ProgressionDbError(Exception):
    """Custom exception for artist progression database operations."""
    pass

def apply_progression_schema():
    """Applies the artist_progression_log.sql schema to the database."""
    # Construct path relative to this file's location
    schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema', 'artist_progression_log.sql')
    logger.info(f"Attempting to apply schema from: {schema_file}")
    try:
        with open(schema_file, 'r') as f:
            sql_script = f.read()
        
        with get_db_cursor(commit=True) as cursor:
            if cursor is None: raise ProgressionDbError("DB Cursor not available")
            cursor.execute(sql_script)
        logger.info("Successfully applied artist_progression_log schema.")
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_file}")
        raise ProgressionDbError(f"Schema file not found: {schema_file}")
    except Exception as e:
        logger.error(f"Error applying artist_progression_log schema: {e}", exc_info=True)
        raise ProgressionDbError(f"Failed to apply schema: {e}")

def add_progression_log_entry(
    artist_id: int,
    event_description: str,
    performance_summary: Optional[str] = None,
    profile_snapshot: Optional[Dict[str, Any]] = None
) -> int:
    """Adds a new entry to the artist progression log.

    Args:
        artist_id: The ID of the artist.
        event_description: Description of the evolution event.
        performance_summary: Optional summary of performance data triggering the change.
        profile_snapshot: Optional snapshot of the profile after the change.

    Returns:
        The ID of the newly inserted log entry.

    Raises:
        ProgressionDbError: If the database insertion fails.
    """
    sql = """
        INSERT INTO artist_progression_log
            (artist_id, event_description, performance_summary, profile_snapshot)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    try:
        # Convert snapshot dict to JSON string for DB storage
        snapshot_json = json.dumps(profile_snapshot) if profile_snapshot else None
        
        with get_db_cursor(commit=True) as cursor:
            if cursor is None: raise ProgressionDbError("DB Cursor not available")
            cursor.execute(sql, (artist_id, event_description, performance_summary, snapshot_json))
            log_id = cursor.fetchone()[0]
            logger.info(f"Added artist progression log entry with ID: {log_id} for artist_id: {artist_id}")
            return log_id
    except Exception as e:
        logger.error(f"Error adding progression log for artist_id {artist_id}: {e}", exc_info=True)
        raise ProgressionDbError(f"Failed to add progression log: {e}")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Assumes DB connection details are in environment variables or defaults
    # Assumes an artist with ID=1 exists (or adjust TEST_ARTIST_ID)
    TEST_ARTIST_ID = 1 
    TEST_SNAPSHOT = {"genres": ["synthwave", "pop"], "keywords": ["retro", "upbeat", "catchy"]}

    try:
        init_connection_pool()
        
        # Apply the schema first (idempotent thanks to IF NOT EXISTS)
        apply_progression_schema()

        # Add a log entry
        print("\n--- Adding Log Entry ---")
        log_id = add_progression_log_entry(
            artist_id=TEST_ARTIST_ID,
            event_description="Added keyword 'catchy' due to high saves.",
            performance_summary="Highest metric: 400 saves on Spotify (Release ID: 102)",
            profile_snapshot=TEST_SNAPSHOT
        )
        print(f"Added log entry with ID: {log_id}")

    except (ProgressionDbError, ConnectionError) as e:
        print(f"\nDatabase Operation Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        close_connection_pool()

