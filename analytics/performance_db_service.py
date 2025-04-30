import logging
import os
from typing import List, Dict, Any, Optional

from ..database.connection_manager import get_db_cursor, init_connection_pool, close_connection_pool

logger = logging.getLogger(__name__)

class PerformanceDbError(Exception):
    """Custom exception for performance database operations."""
    pass

def apply_schema():
    """Applies the content_performance.sql schema to the database."""
    schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema', 'content_performance.sql')
    logger.info(f"Attempting to apply schema from: {schema_file}")
    try:
        with open(schema_file, 'r') as f:
            sql_script = f.read()
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql_script)
        logger.info("Successfully applied content_performance schema.")
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_file}")
        raise PerformanceDbError(f"Schema file not found: {schema_file}")
    except Exception as e:
        logger.error(f"Error applying content_performance schema: {e}", exc_info=True)
        raise PerformanceDbError(f"Failed to apply schema: {e}")

def add_performance_metric(
    release_id: int,
    platform: str,
    metric_type: str,
    metric_value: int,
    source_url: Optional[str] = None,
    notes: Optional[str] = None
) -> int:
    """Adds a new performance metric record to the database.

    Args:
        release_id: The ID of the release this metric belongs to.
        platform: The platform where the metric was observed.
        metric_type: The type of metric (e.g., 'views', 'likes').
        metric_value: The value of the metric.
        source_url: Optional URL of the content on the platform.
        notes: Optional notes about the metric.

    Returns:
        The ID of the newly inserted performance record.

    Raises:
        PerformanceDbError: If the database insertion fails.
    """
    sql = """
        INSERT INTO content_performance 
            (release_id, platform, metric_type, metric_value, source_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (release_id, platform, metric_type, metric_value, source_url, notes))
            record_id = cursor.fetchone()[0]
            logger.info(f"Added performance metric record with ID: {record_id} for release_id: {release_id}")
            return record_id
    except Exception as e:
        logger.error(f"Error adding performance metric for release_id {release_id}: {e}", exc_info=True)
        raise PerformanceDbError(f"Failed to add performance metric: {e}")

def get_performance_metrics_for_release(release_id: int) -> List[Dict[str, Any]]:
    """Retrieves all performance metrics for a specific release.

    Args:
        release_id: The ID of the release.

    Returns:
        A list of dictionaries, each representing a performance metric record.

    Raises:
        PerformanceDbError: If the database query fails.
    """
    sql = """
        SELECT id, release_id, platform, metric_type, metric_value, recorded_at, source_url, notes 
        FROM content_performance 
        WHERE release_id = %s
        ORDER BY recorded_at DESC;
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (release_id,))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            logger.info(f"Retrieved {len(results)} performance metrics for release_id: {release_id}")
            return results
    except Exception as e:
        logger.error(f"Error retrieving performance metrics for release_id {release_id}: {e}", exc_info=True)
        raise PerformanceDbError(f"Failed to retrieve performance metrics: {e}")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Assumes DB connection details are in environment variables or defaults
    # Assumes approved_releases table exists and has an entry with id=1
    TEST_RELEASE_ID = 1 

    try:
        init_connection_pool()
        
        # Apply the schema first (idempotent thanks to IF NOT EXISTS)
        apply_schema()

        # Add some dummy metrics
        print("\n--- Adding Metrics ---")
        metric_id_1 = add_performance_metric(TEST_RELEASE_ID, 'YouTube', 'views', 10500, source_url='http://youtube.com/watch?v=xyz')
        metric_id_2 = add_performance_metric(TEST_RELEASE_ID, 'YouTube', 'likes', 320)
        metric_id_3 = add_performance_metric(TEST_RELEASE_ID, 'Spotify', 'streams', 25000)
        metric_id_4 = add_performance_metric(TEST_RELEASE_ID, 'TikTok', 'views', 150000, notes='Initial surge')

        # Retrieve metrics
        print("\n--- Retrieving Metrics --- ")
        all_metrics = get_performance_metrics_for_release(TEST_RELEASE_ID)
        
        import json
        print(json.dumps(all_metrics, indent=2, default=str)) # Use default=str for datetime objects

    except (PerformanceDbError, ConnectionError) as e:
        print(f"\nDatabase Operation Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        close_connection_pool()

