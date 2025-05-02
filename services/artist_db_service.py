# /home/ubuntu/ai_artist_system_clone/services/artist_db_service.py
"""
Service for managing AI Artist and Error Report data persistence using SQLite.
Replaces the simple JSON file storage for better scalability and robustness.
"""

import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- Configuration ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(PROJECT_ROOT, "data", "artists.db")
MAX_HISTORY_LENGTH = 20 # Max number of performance records to keep per artist
MAX_ERROR_REPORTS = 500 # Max number of error reports to keep

logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# --- Database Initialization ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
        logger.debug(f"Connected to database: {DB_FILE}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database {DB_FILE}: {e}")
        raise

def _add_column_if_not_exists(cursor, table_name, column_name, column_type):
    """Helper function to add a column if it doesn't exist."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info["name"] for info in cursor.fetchall()]
    if column_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            logger.info(f"Added column 	{column_name}	 to table 	{table_name}	.")
        except sqlite3.OperationalError as e:
            # Handle cases where adding column might fail concurrently (less likely with ALTER TABLE)
            logger.warning(f"Could not add column 	{column_name}	 to 	{table_name}	 (might already exist): {e}")
    else:
        logger.debug(f"Column 	{column_name}	 already exists in table 	{table_name}	.")

def initialize_database():
    """Creates the artists and error_reports tables if they don't exist, adding new columns if needed."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # Artists Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                genre TEXT,
                style_notes TEXT,
                created_at TEXT NOT NULL,
                last_run_at TEXT,
                performance_history TEXT, -- Storing as JSON string
                consecutive_rejections INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                autopilot_enabled BOOLEAN DEFAULT 0 -- Added for Autopilot mode
            )
        """)
        logger.info("Database initialized. 'artists' table checked/created.")

        # Add autopilot_enabled column to existing tables if necessary (for backward compatibility)
        _add_column_if_not_exists(cursor, "artists", "autopilot_enabled", "BOOLEAN DEFAULT 0")

        # Error Reports Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                error_hash TEXT,
                error_log TEXT,
                analysis TEXT,
                fix_suggestion TEXT,
                status TEXT DEFAULT 'new', -- e.g., new, analyzed, fix_suggested, fix_attempted, fix_failed, fix_applied, ignored
                service_name TEXT -- e.g., batch_runner, error_analysis_service
            )
        """)
        logger.info("Database initialized. 'error_reports' table checked/created.")

        # Index for faster querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_reports (timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_hash ON error_reports (error_hash)")

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error initializing database tables: {e}")
    finally:
        if conn:
            conn.close()

# --- Artist Data CRUD Operations ---

def add_artist(artist_data: Dict[str, Any]) -> bool:
    """Adds a new artist to the database."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        # Include autopilot_enabled in the INSERT statement
        cursor.execute("""
            INSERT INTO artists (artist_id, name, genre, style_notes, created_at, last_run_at, performance_history, consecutive_rejections, is_active, autopilot_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artist_data["artist_id"],
            artist_data["name"],
            artist_data.get("genre"),
            artist_data.get("style_notes"),
            artist_data["created_at"],
            artist_data.get("last_run_at"),
            json.dumps(artist_data.get("performance_history", [])), # Store as JSON string
            artist_data.get("consecutive_rejections", 0),
            artist_data.get("is_active", True),
            artist_data.get("autopilot_enabled", False) # Default to False if not provided
        ))
        conn.commit()
        logger.info(f"Added new artist {artist_data['artist_id']} to database.")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Artist ID {artist_data['artist_id']} already exists in the database.")
        return False
    except sqlite3.Error as e:
        logger.error(f"Error adding artist {artist_data['artist_id']}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_artist(artist_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single artist by ID."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM artists WHERE artist_id = ?", (artist_id,))
        row = cursor.fetchone()
        if row:
            artist = dict(row)
            # Deserialize performance_history
            artist["performance_history"] = json.loads(artist.get("performance_history", "[]"))
            # Convert autopilot_enabled from 0/1 to boolean
            artist["autopilot_enabled"] = bool(artist.get("autopilot_enabled", 0))
            return artist
        else:
            return None
    except sqlite3.Error as e:
        logger.error(f"Error getting artist {artist_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_artists(only_active: bool = False) -> List[Dict[str, Any]]:
    """Retrieves all artists, optionally filtering for active ones."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM artists"
        if only_active:
            query += " WHERE is_active = 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        artists = []
        for row in rows:
            artist = dict(row)
            artist["performance_history"] = json.loads(artist.get("performance_history", "[]"))
            # Convert autopilot_enabled from 0/1 to boolean
            artist["autopilot_enabled"] = bool(artist.get("autopilot_enabled", 0))
            artists.append(artist)
        return artists
    except sqlite3.Error as e:
        logger.error(f"Error getting all artists: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_artist(artist_id: str, update_data: Dict[str, Any]) -> bool:
    """Updates specific fields for an existing artist."""
    conn = get_db_connection()
    if not conn:
        return False

    fields = []
    values = []
    for key, value in update_data.items():
        # Handle specific fields that need transformation
        if key == "performance_history":
            fields.append(f"{key} = ?")
            values.append(json.dumps(value)) # Serialize to JSON
        elif key == "is_active" or key == "autopilot_enabled": # Handle boolean fields
             fields.append(f"{key} = ?")
             values.append(1 if value else 0) # Convert boolean to integer for SQLite
        elif key != "artist_id": # Avoid updating the primary key
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        logger.warning("No valid fields provided for update.")
        return False

    set_clause = ", ".join(fields)
    query = f"UPDATE artists SET {set_clause} WHERE artist_id = ?"
    values.append(artist_id)

    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Attempted to update non-existent artist ID: {artist_id}")
            return False
        logger.debug(f"Updated artist {artist_id} with data: {update_data}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating artist {artist_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_artist_performance_db(artist_id: str, run_id: str, status: str, retirement_threshold: int) -> bool:
    """Updates performance history, rejection count, and checks for retirement."""
    artist = get_artist(artist_id)
    if not artist:
        logger.warning(f"Attempted to update performance for non-existent artist ID: {artist_id}")
        return False

    now_iso = datetime.utcnow().isoformat()
    new_history_entry = {"run_id": run_id, "status": status, "timestamp": now_iso}
    performance_history = artist.get("performance_history", [])
    performance_history.append(new_history_entry)
    # Keep history manageable
    performance_history = performance_history[-MAX_HISTORY_LENGTH:]

    update_payload = {
        "last_run_at": now_iso,
        "performance_history": performance_history
    }

    consecutive_rejections = artist.get("consecutive_rejections", 0)
    if status == "rejected":
        consecutive_rejections += 1
        update_payload["consecutive_rejections"] = consecutive_rejections
    elif status == "approved":
        consecutive_rejections = 0 # Reset on approval
        update_payload["consecutive_rejections"] = 0
    # No change to consecutive_rejections for other statuses

    # Check for retirement
    if consecutive_rejections >= retirement_threshold:
        if artist.get("is_active", True): # Only log/update if currently active
            update_payload["is_active"] = False
            logger.info(f"Artist {artist_id} (", {artist.get('name', 'N/A')}, ") marked as inactive due to {consecutive_rejections} consecutive rejections.")

    return update_artist(artist_id, update_payload)

# --- Error Report CRUD Operations ---

def add_error_report(report_data: Dict[str, Any]) -> Optional[int]:
    """Adds a new error report to the database and returns the report ID."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO error_reports (timestamp, error_hash, error_log, analysis, fix_suggestion, status, service_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_data.get("timestamp", datetime.utcnow().isoformat()),
            report_data.get("error_hash"),
            report_data.get("error_log"),
            report_data.get("analysis"),
            report_data.get("fix_suggestion"),
            report_data.get("status", "new"),
            report_data.get("service_name")
        ))
        conn.commit()
        report_id = cursor.lastrowid
        logger.info(f"Added new error report with ID {report_id}.")

        # Prune old reports if necessary
        cursor.execute(f"SELECT COUNT(*) FROM error_reports")
        count = cursor.fetchone()[0]
        if count > MAX_ERROR_REPORTS:
            limit = count - MAX_ERROR_REPORTS
            cursor.execute(f"DELETE FROM error_reports WHERE report_id IN (SELECT report_id FROM error_reports ORDER BY timestamp ASC LIMIT {limit})")
            conn.commit()
            logger.info(f"Pruned {limit} oldest error reports.")

        return report_id
    except sqlite3.Error as e:
        logger.error(f"Error adding error report: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_error_reports(limit: int = 50, offset: int = 0, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves error reports, ordered by timestamp descending, with optional filtering."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM error_reports"
        params = []
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        reports = [dict(row) for row in rows]
        return reports
    except sqlite3.Error as e:
        logger.error(f"Error getting error reports: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_error_report_status(report_id: int, new_status: str, update_data: Optional[Dict[str, Any]] = None) -> bool:
    """Updates the status and optionally other fields of a specific error report."""
    conn = get_db_connection()
    if not conn:
        return False

    fields = ["status = ?"]
    values = [new_status]

    if update_data:
        for key, value in update_data.items():
            if key != "report_id": # Avoid updating the primary key
                fields.append(f"{key} = ?")
                values.append(value)

    set_clause = ", ".join(fields)
    query = f"UPDATE error_reports SET {set_clause} WHERE report_id = ?"
    values.append(report_id)

    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Attempted to update status for non-existent error report ID: {report_id}")
            return False
        logger.info(f"Updated error report {report_id}: Status={new_status}, Data={update_data}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating status for error report {report_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Initial Setup ---
initialize_database()

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Running artist_db_service tests...")

    # --- Artist Tests ---
    test_artist_id = f"test_artist_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    added = add_artist({
        "artist_id": test_artist_id,
        "name": "DB Test Artist",
        "genre": "test-genre",
        "style_notes": "Testing DB service.",
        "created_at": datetime.utcnow().isoformat(),
        "performance_history": [],
        "is_active": True,
        "autopilot_enabled": False # Test adding with autopilot off
    })
    print(f"Add Artist {test_artist_id}: {'Success' if added else 'Failed'}")
    retrieved_artist = get_artist(test_artist_id)
    print(f"Get Artist {test_artist_id}: {'Found' if retrieved_artist else 'Not Found'}")
    if retrieved_artist:
        print(f"  Autopilot Enabled: {retrieved_artist.get('autopilot_enabled')}")

    # Test Update Autopilot
    updated_autopilot = update_artist(test_artist_id, {"autopilot_enabled": True})
    print(f"Update Autopilot to True: {'Success' if updated_autopilot else 'Failed'}")
    retrieved_artist = get_artist(test_artist_id)
    if retrieved_artist:
        print(f"  Autopilot Enabled (after update): {retrieved_artist.get('autopilot_enabled')}")

    # ... (rest of artist tests) ...

    # --- Error Report Tests ---
    logger.info("Running error_report tests...")
    test_report_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_hash": "testhash123",
        "error_log": "Traceback:\nValueError: Test error",
        "analysis": "This is a test error.",
        "fix_suggestion": "No fix needed.",
        "status": "new",
        "service_name": "test_service"
    }
    report_id = add_error_report(test_report_data)
    print(f"Add Error Report: {'Success, ID=' + str(report_id) if report_id else 'Failed'}")

    if report_id:
        # Test Get Reports
        reports = get_error_reports(limit=5)
        print(f"Get Error Reports (limit 5): Found {len(reports)}")
        if reports:
            print(f"  Latest report ID: {reports[0]['report_id']}, Status: {reports[0]['status']}")

        # Test Update Status with data
        updated_status = update_error_report_status(report_id, "analyzed", {"analysis": "Updated analysis"})
        print(f"Update Error Report Status & Data (ID: {report_id}): {'Success' if updated_status else 'Failed'}")
        reports_after_update = get_error_reports(limit=1)
        if reports_after_update and reports_after_update[0]['report_id'] == report_id:
            print(f"  New Status: {reports_after_update[0]['status']}")
            print(f"  Updated Analysis: {reports_after_update[0]['analysis']}")

    logger.info("artist_db_service tests finished.")

