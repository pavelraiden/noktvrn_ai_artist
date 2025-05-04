# /home/ubuntu/ai_artist_system_clone/services/artist_db_service.py
"""
Service for managing AI Artist and Error Report data persistence using SQLite.
Replaces the simple JSON file storage for better scalability and robustness.
"""

import sqlite3
import json
import logging
import os
import uuid  # Added for generating artist IDs
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- Configuration ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(PROJECT_ROOT, "data", "artists.db")
MAX_HISTORY_LENGTH = 20  # Max number of performance records to keep per artist
MAX_ERROR_REPORTS = 500  # Max number of error reports to keep

logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


# --- Database Initialization ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
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
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            )
            # Corrected f-string
            logger.info(f"Added column '{column_name}' to table '{table_name}'.")
        except sqlite3.OperationalError as e:
            # Corrected f-string
            logger.warning(
                f"Could not add column '{column_name}' to '{table_name}' (might already exist): {e}"
            )
    else:
        # Corrected f-string
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
            cursor.execute(
                f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
            )
            # Corrected f-string
            logger.info(
                f"Renamed column '{old_column_name}' to '{new_column_name}' in table '{table_name}'."
            )
        except sqlite3.OperationalError as e:
            # Corrected f-string
            logger.error(
                f"Failed to rename column '{old_column_name}' to '{new_column_name}' in '{table_name}': {e}. Manual migration might be needed if using older SQLite."
            )
    elif old_column_name in columns and new_column_name in columns:
        # Corrected f-string
        logger.debug(
            f"Both '{old_column_name}' and '{new_column_name}' exist in '{table_name}'. Skipping rename."
        )
    elif old_column_name not in columns:
        # Corrected f-string
        logger.debug(
            f"Column '{old_column_name}' does not exist in '{table_name}'. Skipping rename."
        )


def initialize_database():
    """Creates the artists and error_reports tables if they don't exist, adding/modifying columns as needed."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # Artists Table - Updated Schema
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                genre TEXT,
                style_notes TEXT,
                llm_config TEXT, -- Storing LLM details as JSON
                created_at TEXT NOT NULL,
                last_run_at TEXT,
                status TEXT DEFAULT 'Candidate', -- Candidate, Active, Paused, Retired, Evolving
                performance_history TEXT, -- Storing as JSON string
                consecutive_rejections INTEGER DEFAULT 0,
                autopilot_enabled BOOLEAN DEFAULT 0,
                voice_url TEXT -- Added for storing voice sample/clone URL
            )
        """
        )
        logger.info("Database initialized. 'artists' table checked/created.")

        # --- Schema Migrations/Updates ---
        # Add columns if they don't exist (idempotent)
        _add_column_if_not_exists(
            cursor, "artists", "status", "TEXT DEFAULT 'Candidate'"
        )
        _add_column_if_not_exists(cursor, "artists", "llm_config", "TEXT")
        _add_column_if_not_exists(
            cursor, "artists", "autopilot_enabled", "BOOLEAN DEFAULT 0"
        )
        _add_column_if_not_exists(
            cursor, "artists", "voice_url", "TEXT"
        )  # Add the new voice_url column

        # Error Reports Table (Unchanged)
        cursor.execute(
            """
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
        """
        )
        logger.info("Database initialized. 'error_reports' table checked/created.")

        # Indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_reports (timestamp DESC)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_error_hash ON error_reports (error_hash)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_artist_status ON artists (status)"
        )

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error initializing database tables: {e}")
    finally:
        if conn:
            conn.close()


# --- Artist Data CRUD Operations ---


def add_artist(artist_data: Dict[str, Any]) -> Optional[str]:
    """Adds a new artist to the database. Returns artist_id if successful."""
    conn = get_db_connection()
    if not conn:
        return None

    artist_id = artist_data.get("artist_id", str(uuid.uuid4()))
    created_at = artist_data.get("created_at", datetime.utcnow().isoformat())
    initial_status = artist_data.get("status", "Candidate")

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO artists (
                artist_id, name, genre, style_notes, llm_config, created_at,
                last_run_at, status, performance_history, consecutive_rejections,
                autopilot_enabled, voice_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                artist_id,
                artist_data["name"],
                artist_data.get("genre"),
                artist_data.get("style_notes"),
                json.dumps(artist_data.get("llm_config", {})),
                created_at,
                artist_data.get("last_run_at"),
                initial_status,
                json.dumps(artist_data.get("performance_history", [])),
                artist_data.get("consecutive_rejections", 0),
                artist_data.get("autopilot_enabled", False),
                artist_data.get(
                    "voice_url"
                ),  # Include voice_url (can be None initially)
            ),
        )
        conn.commit()
        # Corrected f-string
        logger.info(
            f"Added new artist '{artist_data['name']}' with ID {artist_id} and status '{initial_status}'."
        )
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
    llm_config_str = None  # Initialize for error logging
    perf_history_str = None  # Initialize for error logging
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM artists WHERE artist_id = ?", (artist_id,))
        row = cursor.fetchone()
        if row:
            artist = dict(row)
            # Deserialize JSON fields safely
            perf_history_str = artist.get("performance_history")
            artist["performance_history"] = (
                json.loads(perf_history_str) if perf_history_str is not None else []
            )
            llm_config_str = artist.get("llm_config")
            artist["llm_config"] = (
                json.loads(llm_config_str) if llm_config_str is not None else {}
            )
            # Convert autopilot_enabled from 0/1 to boolean
            artist["autopilot_enabled"] = bool(artist.get("autopilot_enabled", 0))
            # voice_url is already TEXT, no conversion needed
            return artist
        else:
            return None
    except json.JSONDecodeError as e:
        # Corrected f-string
        logger.error(
            f"Error decoding JSON for artist {artist_id}: {e}. Data: llm_config='{llm_config_str}', history='{perf_history_str}'"
        )
        return None  # Or handle partially loaded data if needed
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
            llm_config_str = None  # Initialize for error logging
            perf_history_str = None  # Initialize for error logging
            try:
                # Deserialize JSON fields safely
                perf_history_str = artist.get("performance_history")
                artist["performance_history"] = (
                    json.loads(perf_history_str) if perf_history_str is not None else []
                )
                llm_config_str = artist.get("llm_config")
                artist["llm_config"] = (
                    json.loads(llm_config_str) if llm_config_str is not None else {}
                )
                # Convert autopilot_enabled from 0/1 to boolean
                artist["autopilot_enabled"] = bool(artist.get("autopilot_enabled", 0))
                # voice_url is already TEXT, no conversion needed
                artists.append(artist)
            except json.JSONDecodeError as e:
                artist_id = artist.get("artist_id", "UNKNOWN")
                # Corrected f-string
                logger.error(
                    f"Error decoding JSON for artist {artist_id} in get_all_artists: {e}. Skipping this artist. Data: llm_config='{llm_config_str}', history='{perf_history_str}'"
                )
                continue  # Skip this artist if JSON is invalid
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
            values.append(json.dumps(value))
        elif key == "autopilot_enabled":
            fields.append(f"{key} = ?")
            values.append(1 if value else 0)
        elif key != "artist_id":  # Avoid updating the primary key
            # Includes 'status', 'name', 'genre', 'style_notes', 'last_run_at', 'consecutive_rejections', 'voice_url'
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


def update_artist_performance_db(
    artist_id: str, run_id: str, status: str, retirement_threshold: int
) -> bool:
    """Updates performance history, rejection count, and potentially status based on run outcome.

    Args:
        artist_id: The ID of the artist.
        run_id: The ID of the completed run.
        status: The outcome of the run ('approved', 'rejected', 'error', etc.).
        retirement_threshold: Number of consecutive rejections to trigger retirement.

    Returns:
        True if the update was successful, False otherwise.
    """
    artist = get_artist(artist_id)
    if not artist:
        logger.warning(
            f"Attempted to update performance for non-existent artist ID: {artist_id}"
        )
        return False

    now_iso = datetime.utcnow().isoformat()
    new_history_entry = {"run_id": run_id, "status": status, "timestamp": now_iso}
    performance_history = artist.get("performance_history", [])
    performance_history.append(new_history_entry)
    # Keep history manageable
    performance_history = performance_history[-MAX_HISTORY_LENGTH:]

    update_payload = {
        "last_run_at": now_iso,
        "performance_history": performance_history,
    }

    consecutive_rejections = artist.get("consecutive_rejections", 0)
    current_status = artist.get("status", "Unknown")

    if status == "rejected":
        consecutive_rejections += 1
        update_payload["consecutive_rejections"] = consecutive_rejections
        # Check for retirement trigger
        if consecutive_rejections >= retirement_threshold and current_status not in [
            "Retired",
            "Paused",
        ]:
            update_payload["status"] = "Retired"
            # Corrected f-string
            logger.warning(
                f"Artist {artist_id} ('{artist.get('name', 'N/A')}') automatically retired due to {consecutive_rejections} consecutive rejections."
            )
    elif status == "approved":
        if consecutive_rejections > 0:
            update_payload["consecutive_rejections"] = 0  # Reset on approval
        # If artist was 'Candidate', first approval makes them 'Active'
        if current_status == "Candidate":
            update_payload["status"] = "Active"
            # Corrected f-string
            logger.info(
                f"Promoting candidate artist {artist_id} ('{artist.get('name', 'N/A')}') to Active after first approval."
            )
    else:  # Handle 'error', 'generation_failed_track', etc. - Treat as neutral for rejection count
        # No change to consecutive_rejections needed
        pass

    # Perform the update
    success = update_artist(artist_id, update_payload)
    if success:
        # Corrected f-string
        logger.info(
            f"Updated performance for artist {artist_id}. Run: {run_id}, Status: {status}. New rejection count: {update_payload.get('consecutive_rejections', consecutive_rejections)}"
        )
    else:
        logger.error(
            f"Failed to update performance for artist {artist_id} after run {run_id}."
        )
    return success


def delete_artist(artist_id: str) -> bool:
    """Deletes an artist from the database."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM artists WHERE artist_id = ?", (artist_id,))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Attempted to delete non-existent artist ID: {artist_id}")
            return False
        logger.info(f"Deleted artist {artist_id}.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error deleting artist {artist_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()


# --- Error Report CRUD Operations ---


def add_error_report(report_data: Dict[str, Any]) -> Optional[int]:
    """Adds a new error report to the database. Returns report_id if successful."""
    conn = get_db_connection()
    if not conn:
        return None

    timestamp = report_data.get("timestamp", datetime.utcnow().isoformat())
    status = report_data.get("status", "new")

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO error_reports (
                timestamp, error_hash, error_log, analysis, fix_suggestion, status, service_name
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                timestamp,
                report_data.get("error_hash"),
                report_data.get("error_log"),
                report_data.get("analysis"),
                report_data.get("fix_suggestion"),
                status,
                report_data.get("service_name"),
            ),
        )
        report_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Added new error report with ID {report_id}.")

        # Prune old reports if limit exceeded
        _prune_error_reports(cursor)
        conn.commit()

        return report_id
    except sqlite3.Error as e:
        logger.error(f"Error adding error report: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_error_report(report_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single error report by ID."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM error_reports WHERE report_id = ?", (report_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Error getting error report {report_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_error_reports(
    limit: int = 50, status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves recent error reports, optionally filtering by status."""
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
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(
            f"Error getting error reports (filter: {status_filter}, limit: {limit}): {e}"
        )
        return []
    finally:
        if conn:
            conn.close()


def update_error_report(report_id: int, update_data: Dict[str, Any]) -> bool:
    """Updates specific fields for an existing error report."""
    conn = get_db_connection()
    if not conn:
        return False

    fields = []
    values = []
    for key, value in update_data.items():
        if key != "report_id":  # Avoid updating the primary key
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        logger.warning("No valid fields provided for error report update.")
        return False

    set_clause = ", ".join(fields)
    query = f"UPDATE error_reports SET {set_clause} WHERE report_id = ?"
    values.append(report_id)

    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning(
                f"Attempted to update non-existent error report ID: {report_id}"
            )
            return False
        logger.debug(f"Updated error report {report_id} with data: {update_data}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating error report {report_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()


def _prune_error_reports(cursor):
    """Internal function to delete the oldest error reports if the count exceeds MAX_ERROR_REPORTS."""
    try:
        cursor.execute("SELECT COUNT(*) FROM error_reports")
        count = cursor.fetchone()[0]
        if count > MAX_ERROR_REPORTS:
            num_to_delete = count - MAX_ERROR_REPORTS
            # Find the IDs of the oldest reports to delete
            cursor.execute(
                "SELECT report_id FROM error_reports ORDER BY timestamp ASC LIMIT ?",
                (num_to_delete,),
            )
            ids_to_delete = [row[0] for row in cursor.fetchall()]
            if ids_to_delete:
                # Use placeholders for security
                placeholders = ",".join("?" * len(ids_to_delete))
                cursor.execute(
                    f"DELETE FROM error_reports WHERE report_id IN ({placeholders})",
                    tuple(ids_to_delete),
                )
                logger.info(
                    f"Pruned {len(ids_to_delete)} oldest error reports to maintain limit of {MAX_ERROR_REPORTS}."
                )
    except sqlite3.Error as e:
        logger.error(f"Error pruning error reports: {e}")


# --- Autopilot Status --- #
def set_autopilot_status(artist_id: str, enabled: bool) -> bool:
    """Sets the autopilot status for a specific artist."""
    return update_artist(artist_id, {"autopilot_enabled": enabled})


def get_autopilot_status(artist_id: str) -> Optional[bool]:
    """Gets the autopilot status for a specific artist."""
    artist = get_artist(artist_id)
    if artist:
        return artist.get(
            "autopilot_enabled", False
        )  # Default to False if somehow missing
    else:
        logger.warning(
            f"Attempted to get autopilot status for non-existent artist ID: {artist_id}"
        )
        return None
