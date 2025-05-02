# /home/ubuntu/ai_artist_system_clone/services/artist_db_service.py
"""
Service for managing AI Artist data persistence using SQLite.
Replaces the simple JSON file storage for better scalability and robustness.
"""

import sqlite3
import json
import logging
import os
from datetime import datetime

# --- Configuration ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_FILE = os.path.join(PROJECT_ROOT, "data", "artists.db")
MAX_HISTORY_LENGTH = 20 # Max number of performance records to keep per artist

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

def initialize_database():
    """Creates the artists table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
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
                is_active BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()
        logger.info("Database initialized. 'artists' table checked/created.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database table: {e}")
    finally:
        if conn:
            conn.close()

# --- Artist Data CRUD Operations ---

def add_artist(artist_data):
    """Adds a new artist to the database."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO artists (artist_id, name, genre, style_notes, created_at, last_run_at, performance_history, consecutive_rejections, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artist_data["artist_id"],
            artist_data["name"],
            artist_data.get("genre"),
            artist_data.get("style_notes"),
            artist_data["created_at"],
            artist_data.get("last_run_at"),
            json.dumps(artist_data.get("performance_history", [])), # Store as JSON string
            artist_data.get("consecutive_rejections", 0),
            artist_data.get("is_active", True)
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

def get_artist(artist_id):
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
            return artist
        else:
            return None
    except sqlite3.Error as e:
        logger.error(f"Error getting artist {artist_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_artists(only_active=False):
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
            artists.append(artist)
        return artists
    except sqlite3.Error as e:
        logger.error(f"Error getting all artists: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_artist(artist_id, update_data):
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
        elif key == "is_active":
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

def update_artist_performance_db(artist_id, run_id, status, retirement_threshold):
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

# --- Initial Setup ---
initialize_database()

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Running artist_db_service tests...")

    # Test Add
    test_artist_id = f"test_artist_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    added = add_artist({
        "artist_id": test_artist_id,
        "name": "DB Test Artist",
        "genre": "test-genre",
        "style_notes": "Testing DB service.",
        "created_at": datetime.utcnow().isoformat(),
        "performance_history": [],
        "is_active": True
    })
    print(f"Add Artist {test_artist_id}: {'Success' if added else 'Failed'}")

    # Test Get
    retrieved_artist = get_artist(test_artist_id)
    print(f"Get Artist {test_artist_id}: {'Found' if retrieved_artist else 'Not Found'}")
    if retrieved_artist:
        print(f"  Name: {retrieved_artist.get('name')}")
        print(f"  History: {retrieved_artist.get('performance_history')}")

    # Test Update Performance (Approved)
    updated_perf = update_artist_performance_db(test_artist_id, "run_1", "approved", 3)
    print(f"Update Performance (Approved): {'Success' if updated_perf else 'Failed'}")
    retrieved_artist = get_artist(test_artist_id)
    if retrieved_artist:
        print(f"  Consecutive Rejections: {retrieved_artist.get('consecutive_rejections')}")
        print(f"  History Length: {len(retrieved_artist.get('performance_history', []))}")

    # Test Update Performance (Rejected x3 -> Retire)
    updated_perf = update_artist_performance_db(test_artist_id, "run_2", "rejected", 3)
    print(f"Update Performance (Rejected 1): {'Success' if updated_perf else 'Failed'}")
    updated_perf = update_artist_performance_db(test_artist_id, "run_3", "rejected", 3)
    print(f"Update Performance (Rejected 2): {'Success' if updated_perf else 'Failed'}")
    updated_perf = update_artist_performance_db(test_artist_id, "run_4", "rejected", 3)
    print(f"Update Performance (Rejected 3 - Retire): {'Success' if updated_perf else 'Failed'}")

    retrieved_artist = get_artist(test_artist_id)
    if retrieved_artist:
        print(f"  Consecutive Rejections: {retrieved_artist.get('consecutive_rejections')}")
        print(f"  Is Active: {retrieved_artist.get('is_active')}")

    # Test Get All Active
    active_artists = get_all_artists(only_active=True)
    print(f"Get All Active Artists: Found {len(active_artists)}")
    # Check if test artist is NOT in the active list
    is_test_artist_active = any(a["artist_id"] == test_artist_id for a in active_artists)
    print(f"  Is {test_artist_id} in active list: {is_test_artist_active}")

    logger.info("artist_db_service tests finished.")


