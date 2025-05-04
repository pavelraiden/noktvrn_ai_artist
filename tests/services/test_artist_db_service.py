# /home/ubuntu/ai_artist_system_clone/tests/services/test_artist_db_service.py
"""Unit tests for the Artist DB Service."""

import pytest
import sqlite3
import json
import os
from datetime import datetime
import sys

# Add project root to sys.path to allow importing services
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

# Import the service module AFTER potentially patching
# We will patch the DB_FILE constant before importing functions

# --- Test Setup and Fixtures ---


@pytest.fixture(autouse=True)
def patch_db_file(monkeypatch):
    """Patches the DB_FILE constant to use an in-memory database for tests."""
    # Patch the constant *before* importing functions that use it
    monkeypatch.setattr("services.artist_db_service.DB_FILE", ":memory:")
    # Ensure the data directory mock doesn't interfere if os.makedirs is called
    monkeypatch.setattr("os.makedirs", lambda *args, **kwargs: None)


@pytest.fixture
def db_service_module(monkeypatch):
    """Fixture to initialize the in-memory DB for each test."""
    # Patch DB_FILE to use in-memory *before* importing the service
    monkeypatch.setattr("services.artist_db_service.DB_FILE", ":memory:")
    monkeypatch.setattr("os.makedirs", lambda *args, **kwargs: None)

    # Import the service module *after* patching
    import services.artist_db_service as service

    # Initialize the database once for the module
    try:
        service.initialize_database()  # This uses the patched :memory: path
    except Exception as e:
        pytest.fail(f"Database initialization failed in module fixture: {e}")

    # No need to yield connection, functions will connect to :memory:
    yield service


@pytest.fixture(autouse=True)
def db_service(db_service_module):
    """Fixture to provide the initialized service module to each test."""
    # This fixture simply passes through the module-scoped fixture
    # and ensures the DB is clean for each test (by re-initializing, though :memory: is usually clean)
    # Re-initializing might be redundant for :memory: but ensures table exists if tests somehow drop it.
    try:
        db_service_module.initialize_database()
    except Exception as e:
        pytest.fail(f"Database re-initialization failed in test fixture: {e}")
    return db_service_module


# --- Test Cases ---


def test_initialize_database(db_service):
    """Test if the database and table are created."""
    conn = db_service.get_db_connection()
    cursor = conn.cursor()
    # Check if the artists table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='artists';"
    )
    table_exists = cursor.fetchone()
    conn.close()
    assert table_exists is not None
    assert table_exists["name"] == "artists"


def test_add_and_get_artist(db_service):
    """Test adding a new artist and retrieving it."""
    artist_id = "artist_add_test"
    now_iso = datetime.utcnow().isoformat()
    artist_data = {
        "artist_id": artist_id,
        "name": "Add Test Artist",
        "genre": "test-pop",
        "style_notes": "Catchy hooks.",
        "created_at": now_iso,
        "performance_history": [
            {"run_id": "run0", "status": "init", "timestamp": now_iso}
        ],
        "is_active": True,
    }
    added = db_service.add_artist(artist_data)
    assert added is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["artist_id"] == artist_id
    assert retrieved["name"] == "Add Test Artist"
    assert retrieved["genre"] == "test-pop"
    assert retrieved["style_notes"] == "Catchy hooks."
    assert retrieved["created_at"] == now_iso
    assert retrieved["last_run_at"] is None  # Not set during add
    assert isinstance(retrieved["performance_history"], list)
    assert len(retrieved["performance_history"]) == 1
    assert retrieved["performance_history"][0]["run_id"] == "run0"
    assert retrieved["consecutive_rejections"] == 0
    assert retrieved["is_active"] == 1  # SQLite stores boolean as 0 or 1


def test_add_artist_duplicate(db_service):
    """Test that adding an artist with a duplicate ID fails gracefully."""
    artist_id = "artist_dup_test"
    now_iso = datetime.utcnow().isoformat()
    artist_data = {"artist_id": artist_id, "name": "Dup Test", "created_at": now_iso}

    added1 = db_service.add_artist(artist_data)
    assert added1 is True
    added2 = db_service.add_artist(artist_data)  # Try adding again
    assert added2 is False


def test_get_nonexistent_artist(db_service):
    """Test retrieving an artist that does not exist."""
    retrieved = db_service.get_artist("nonexistent_id")
    assert retrieved is None


def test_get_all_artists(db_service):
    """Test retrieving all artists, including active/inactive filtering."""
    now_iso = datetime.utcnow().isoformat()
    artist1 = {
        "artist_id": "all1",
        "name": "Artist One",
        "created_at": now_iso,
        "is_active": True,
    }
    artist2 = {
        "artist_id": "all2",
        "name": "Artist Two",
        "created_at": now_iso,
        "is_active": False,
    }
    artist3 = {
        "artist_id": "all3",
        "name": "Artist Three",
        "created_at": now_iso,
        "is_active": True,
    }

    db_service.add_artist(artist1)
    db_service.add_artist(artist2)
    db_service.add_artist(artist3)

    all_artists = db_service.get_all_artists()
    assert len(all_artists) == 3
    assert {a["artist_id"] for a in all_artists} == {"all1", "all2", "all3"}

    active_artists = db_service.get_all_artists(only_active=True)
    assert len(active_artists) == 2
    assert {a["artist_id"] for a in active_artists} == {"all1", "all3"}


def test_update_artist(db_service):
    """Test updating fields of an existing artist."""
    artist_id = "update_test"
    now_iso = datetime.utcnow().isoformat()
    initial_data = {
        "artist_id": artist_id,
        "name": "Initial Name",
        "genre": "initial",
        "created_at": now_iso,
    }
    db_service.add_artist(initial_data)

    update_payload = {
        "name": "Updated Name",
        "style_notes": "Now with style!",
        "is_active": False,
    }
    updated = db_service.update_artist(artist_id, update_payload)
    assert updated is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["name"] == "Updated Name"
    assert retrieved["genre"] == "initial"  # Unchanged field
    assert retrieved["style_notes"] == "Now with style!"
    assert retrieved["is_active"] == 0  # Updated boolean


def test_update_nonexistent_artist(db_service):
    """Test that updating a non-existent artist fails."""
    updated = db_service.update_artist("nonexistent_update", {"name": "Wont Work"})
    assert updated is False


def test_update_artist_performance_approved(db_service):
    """Test updating performance after an approved run."""
    artist_id = "perf_approve_test"
    now_iso = datetime.utcnow().isoformat()
    initial_data = {
        "artist_id": artist_id,
        "name": "Perf Approve",
        "created_at": now_iso,
        "consecutive_rejections": 2,
    }
    db_service.add_artist(initial_data)

    updated = db_service.update_artist_performance_db(
        artist_id, "run_approve", "approved", 3
    )
    assert updated is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["last_run_at"] is not None
    assert len(retrieved["performance_history"]) == 1
    assert retrieved["performance_history"][0]["status"] == "approved"
    assert retrieved["consecutive_rejections"] == 0  # Should reset
    assert retrieved["is_active"] == 1


def test_update_artist_performance_rejected(db_service):
    """Test updating performance after a rejected run."""
    artist_id = "perf_reject_test"
    now_iso = datetime.utcnow().isoformat()
    initial_data = {
        "artist_id": artist_id,
        "name": "Perf Reject",
        "created_at": now_iso,
        "consecutive_rejections": 1,
    }
    db_service.add_artist(initial_data)

    updated = db_service.update_artist_performance_db(
        artist_id, "run_reject", "rejected", 3
    )
    assert updated is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["last_run_at"] is not None
    assert len(retrieved["performance_history"]) == 1
    assert retrieved["performance_history"][0]["status"] == "rejected"
    assert retrieved["consecutive_rejections"] == 2  # Should increment
    assert retrieved["is_active"] == 1


def test_update_artist_performance_retirement(db_service):
    """Test artist retirement after reaching rejection threshold."""
    artist_id = "perf_retire_test"
    now_iso = datetime.utcnow().isoformat()
    retirement_threshold = 3
    initial_data = {
        "artist_id": artist_id,
        "name": "Perf Retire",
        "created_at": now_iso,
        "consecutive_rejections": retirement_threshold - 1,
    }
    db_service.add_artist(initial_data)

    # Last rejection to trigger retirement
    updated = db_service.update_artist_performance_db(
        artist_id, "run_retire", "rejected", retirement_threshold
    )
    assert updated is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["last_run_at"] is not None
    assert retrieved["consecutive_rejections"] == retirement_threshold
    assert retrieved["is_active"] == 0  # Should be inactive

    # Test that another rejection doesn't change state if already inactive
    updated_again = db_service.update_artist_performance_db(
        artist_id, "run_after_retire", "rejected", retirement_threshold
    )
    assert updated_again is True
    retrieved_again = db_service.get_artist(artist_id)
    assert retrieved_again["is_active"] == 0
    assert (
        retrieved_again["consecutive_rejections"] == retirement_threshold + 1
    )  # Count still increments


def test_update_artist_performance_history_limit(db_service):
    """Test that performance history is capped at MAX_HISTORY_LENGTH."""
    artist_id = "perf_history_test"
    now_iso = datetime.utcnow().isoformat()
    # Temporarily reduce max history for test
    db_service.MAX_HISTORY_LENGTH = 3
    initial_data = {
        "artist_id": artist_id,
        "name": "Perf History",
        "created_at": now_iso,
    }
    db_service.add_artist(initial_data)

    # Add more history entries than the limit
    for i in range(db_service.MAX_HISTORY_LENGTH + 2):
        db_service.update_artist_performance_db(artist_id, f"run_{i}", "approved", 5)

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert len(retrieved["performance_history"]) == db_service.MAX_HISTORY_LENGTH
    # Check if the oldest entries were removed
    assert retrieved["performance_history"][0]["run_id"] == "run_2"
    assert (
        retrieved["performance_history"][-1]["run_id"]
        == f"run_{db_service.MAX_HISTORY_LENGTH + 1}"
    )

    # Restore original value (important if MAX_HISTORY_LENGTH is used elsewhere)
    # In a real scenario, might need a better way to manage this constant for testing
    import services.artist_db_service

    services.artist_db_service.MAX_HISTORY_LENGTH = 20  # Restore default
