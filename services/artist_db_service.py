# /home/ubuntu/ai_artist_system_clone/services/artist_db_service.py
"""
Service for managing AI Artist and Error Report data persistence using SQLite.
Replaces the simple JSON file storage for better scalability and robustness.
"""

import sqlite3
import json
import logging
import os
import uuid # Added for generating artist IDs
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
            logger.info(f"Added column '{column_name}' to table '{table_name}'.")
        except sqlite3.OperationalError as e:
            # Handle cases where adding column might fail concurrently (less likely with ALTER TABLE)
            logger.warning(f"Could not add column '{column_name}' to '{table_name}' (might already exist): {e}")
    else:
        logger.debug(f"Column '{column_name}' already exists in table '{table_name}'.")

def _rename_column_if_exists(cursor, table_name, old_column_name, new_column_name):
    """Helper function to rename a column if it exists and the new name doesn't."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {info["name"]: info for info in cursor.fetchall()}
    if old_column_name in columns and new_column_name not in columns:
        try:
            # SQLite < 3.25.0 doesn't support RENAME COLUMN directly in ALTER TABLE
            # For broader compatibility, we might need a more complex migration (create new table, copy data, drop old, rename new)
            # However, modern SQLite versions support it. Assuming modern version for simplicity here.
            cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}")
            logger.info(f"Renamed column '{old_column_name}' to '{new_column_name}' in table '{table_name}'.")
        except sqlite3.OperationalError as e:
            logger.error(f"Failed to rename column '{old_column_name}' to '{new_column_name}' in '{table_name}': {e}. Manual migration might be needed if using older SQLite.")
    elif old_column_name in columns and new_column_name in columns:
         logger.debug(f"Both '{old_column_name}' and '{new_column_name}' exist in '{table_name}'. Skipping rename.")
    elif old_column_name not in columns:
         logger.debug(f"Column '{old_column_name}' does not exist in '{table_name}'. Skipping rename.")

def initialize_database():
    """Creates the artists and error_reports tables if they don't exist, adding/modifying columns as needed for lifecycle management."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # Artists Table - Updated Schema for Lifecycle Management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                genre TEXT,
                style_notes TEXT,
                llm_config TEXT, -- Added for storing LLM details
                created_at TEXT NOT NULL,
                last_run_at TEXT,
                status TEXT DEFAULT 'Candidate', -- Replaces is_active (Candidate, Active, Paused, Retired, Evolving)
                performance_history TEXT, -- Storing as JSON string
                consecutive_rejections INTEGER DEFAULT 0,
                autopilot_enabled BOOLEAN DEFAULT 0
            )
        """)
        logger.info("Database initialized. 'artists' table checked/created.")

        # --- Schema Migrations/Updates ---
        # 1. Add 'status' column if it doesn't exist
        _add_column_if_not_exists(cursor, "artists", "status", "TEXT DEFAULT 'Candidate'")

        # 2. Add 'llm_config' column if it doesn't exist
        _add_column_if_not_exists(cursor, "artists", "llm_config", "TEXT")

        # 3. Rename 'is_active' to 'status' if 'is_active' exists and 'status' doesn't (Handle legacy)
        # Note: This is a simplification. A proper migration would map 1 to 'Active', 0 to 'Paused' or 'Retired'.
        # For now, we prioritize the new 'status' column. If 'is_active' exists, it might become redundant.
        # We will primarily use the 'status' column going forward.
        # _rename_column_if_exists(cursor, "artists", "is_active", "status") # Commented out rename due to complexity of data migration

        # 4. Add 'autopilot_enabled' if missing (already handled in previous version, kept for safety)
        _add_column_if_not_exists(cursor, "artists", "autopilot_enabled", "BOOLEAN DEFAULT 0")

        # Error Reports Table (Unchanged from previous version)
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

        # Index for faster querying (Unchanged)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_reports (timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_hash ON error_reports (error_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artist_status ON artists (status)") # Add index for status

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error initializing database tables: {e}")
    finally:
        if conn:
            conn.close()

# --- Artist Data CRUD Operations ---

def add_artist(artist_data: Dict[str, Any]) -> Optional[str]:
    """Adds a new artist to the database with 'Candidate' status. Returns artist_id if successful."""
    conn = get_db_connection()
    if not conn:
        return None

    artist_id = artist_data.get("artist_id", str(uuid.uuid4())) # Generate ID if not provided
    created_at = artist_data.get("created_at", datetime.utcnow().isoformat())
    initial_status = artist_data.get("status", "Candidate") # Default to Candidate

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO artists (
                artist_id, name, genre, style_notes, llm_config, created_at,
                last_run_at, status, performance_history, consecutive_rejections,
                autopilot_enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artist_id,
            artist_data["name"],
            artist_data.get("genre"),
            artist_data.get("style_notes"),
            json.dumps(artist_data.get("llm_config", {})), # Store LLM config as JSON
            created_at,
            artist_data.get("last_run_at"), # Likely None initially
            initial_status,
            json.dumps(artist_data.get("performance_history", [])), # Store as JSON string
            artist_data.get("consecutive_rejections", 0),
            artist_data.get("autopilot_enabled", False) # Default autopilot to False
        ))
        conn.commit()
        logger.info(f"Added new artist '{artist_data['name']}' with ID {artist_id} and status '{initial_status}'.")
        return artist_id
    except sqlite3.IntegrityError:
        logger.warning(f"Artist ID {artist_id} already exists in the database.")
        return None
    except sqlite3.Error as e:
        logger.error(f"Error adding artist {artist_id}: {e}")
        return None
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
            # Deserialize JSON fields safely
            perf_history_str = artist.get("performance_history")
            artist["performance_history"] = json.loads(perf_history_str) if perf_history_str is not None else []
            llm_config_str = artist.get("llm_config")
            artist["llm_config"] = json.loads(llm_config_str) if llm_config_str is not None else {}
            # Convert autopilot_enabled from 0/1 to boolean
            artist["autopilot_enabled"] = bool(artist.get("autopilot_enabled", 0))
            return artist
        else:
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON for artist {artist_id}: {e}. Data: llm_config='{llm_config_str}', history='{perf_history_str}'")
        return None # Or handle partially loaded data if needed
    except sqlite3.Error as e:
        logger.error(f"Error getting artist {artist_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_artists(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all artists, optionally filtering by status."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM artists"
        params = []
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        artists = []
        for row in rows:
            artist = dict(row)
            try:
                # Deserialize JSON fields safely
                perf_history_str = artist.get("performance_history")
                artist["performance_history"] = json.loads(perf_history_str) if perf_history_str is not None else []
                llm_config_str = artist.get("llm_config")
                artist["llm_config"] = json.loads(llm_config_str) if llm_config_str is not None else {}
                # Convert autopilot_enabled from 0/1 to boolean
                artist["autopilot_enabled"] = bool(artist.get("autopilot_enabled", 0))
                artists.append(artist)
            except json.JSONDecodeError as e:
                artist_id = artist.get("artist_id", "UNKNOWN")
                logger.error(f"Error decoding JSON for artist {artist_id} in get_all_artists: {e}. Skipping this artist. Data: llm_config='{llm_config_str}', history='{perf_history_str}'")
                continue # Skip this artist if JSON is invalid
        return artists
    except sqlite3.Error as e:
        logger.error(f"Error getting artists (filter: {status_filter}): {e}")
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
        if key == "performance_history" or key == "llm_config":
            fields.append(f"{key} = ?")
            values.append(json.dumps(value)) # Serialize to JSON
        elif key == "autopilot_enabled": # Handle boolean field
             fields.append(f"{key} = ?")
             values.append(1 if value else 0) # Convert boolean to integer for SQLite
        elif key != "artist_id": # Avoid updating the primary key
            # Includes 'status', 'name', 'genre', 'style_notes', 'last_run_at', 'consecutive_rejections'
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

def update_artist_status(artist_id: str, new_status: str) -> bool:
    """Convenience function to update only the artist's status."""
    return update_artist(artist_id, {"status": new_status})

def update_artist_performance_db(artist_id: str, run_id: str, status: str, retirement_threshold: int) -> bool:
    """Updates performance history, rejection count, and potentially status based on run outcome.

    Args:
        artist_id: The ID of the artist.
        run_id: The ID of the completed run.
        status: The outcome of the run ('approved', 'rejected', etc.).
        retirement_threshold: Number of consecutive rejections to trigger retirement.

    Returns:
        True if the update was successful, False otherwise.
    """
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
    current_status = artist.get("status", "Unknown")

    if status == "rejected":
        consecutive_rejections += 1
        update_payload["consecutive_rejections"] = consecutive_rejections
        # Check for retirement trigger
        if consecutive_rejections >= retirement_threshold and current_status not in ["Retired", "Paused"]:
            update_payload["status"] = "Retired"
            logger.warning(f"Artist {artist_id} ('{artist.get('name', 'N/A')}') automatically retired due to {consecutive_rejections} consecutive rejections.")
    elif status == "approved":
        if consecutive_rejections > 0:
            update_payload["consecutive_rejections"] = 0 # Reset on approval
        # If artist was 'Candidate', first approval makes them 'Active'
        if current_status == "Candidate":
             update_payload["status"] = "Active"
             logger.info(f"Artist {artist_id} ('{artist.get('name', 'N/A')}') status changed from Candidate to Active after first approval.")

    # Ensure we don't try to update if payload is empty (e.g., non-approved/rejected status with 0 rejections)
    if len(update_payload) <= 1 and "last_run_at" in update_payload:
         logger.debug(f"No significant performance update needed for artist {artist_id} based on run status '{status}'. Only updating last_run_at.")
         return update_artist(artist_id, {"last_run_at": now_iso})

    return update_artist(artist_id, update_payload)

# --- Error Report CRUD Operations (Unchanged) ---

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
        logger.info(f"Added new error report with ID: {report_id}")

        # --- Prune old error reports ---
        cursor.execute("SELECT COUNT(*) FROM error_reports")
        count = cursor.fetchone()[0]
        if count > MAX_ERROR_REPORTS:
            num_to_delete = count - MAX_ERROR_REPORTS
            cursor.execute("DELETE FROM error_reports WHERE report_id IN (SELECT report_id FROM error_reports ORDER BY timestamp ASC LIMIT ?)", (num_to_delete,))
            conn.commit()
            logger.info(f"Pruned {num_to_delete} oldest error reports.")

        return report_id
    except sqlite3.Error as e:
        logger.error(f"Error adding error report: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_error_reports(limit: int = 50, offset: int = 0, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves error reports, ordered by timestamp descending, with optional status filter."""
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
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Error getting error reports: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_error_report_status(report_id: int, new_status: str) -> bool:
    """Updates the status of a specific error report."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE error_reports SET status = ? WHERE report_id = ?", (new_status, report_id))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Attempted to update status for non-existent error report ID: {report_id}")
            return False
        logger.info(f"Updated status for error report {report_id} to '{new_status}'.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating status for error report {report_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Seed Data (Optional) ---
# You might want a function to load initial artists from a JSON file if the DB is empty.
# Example:
# def seed_artists_from_json(filepath="data/artists/seed_artists.json"):
#     if not os.path.exists(filepath):
#         logger.warning(f"Seed artist file not found: {filepath}")
#         return
#     if get_all_artists(): # Only seed if DB is empty
#         logger.info("Artist database already contains data. Skipping seed.")
#         return
#     try:
#         with open(filepath, "r") as f:
#             seed_data = json.load(f)
#         logger.info(f"Seeding artists from {filepath}...")
#         count = 0
#         for artist_data in seed_data:
#             if add_artist(artist_data):
#                 count += 1
#         logger.info(f"Successfully seeded {count} artists.")
#     except (json.JSONDecodeError, IOError) as e:
#         logger.error(f"Error reading or decoding seed artist file {filepath}: {e}")
#     except Exception as e:
#         logger.error(f"Unexpected error during artist seeding: {e}")

# --- Initialization Call ---
# initialize_database() # Usually called by the main application/runner
# seed_artists_from_json() # Optional: Call if you want to seed on module load

