# /home/ubuntu/ai_artist_system_clone/tests/services/test_artist_db_service.py
"""Unit tests for the Artist DB Service."""

import pytest
import os
import sys
import json
import sqlite3
from datetime import datetime

# Add project root to sys.path to allow importing services
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.append(PROJECT_ROOT)

# Import the service module AFTER potentially patching
# We will patch the DB_FILE constant before importing functions

# --- Test Setup and Fixtures ---


@pytest.fixture
def db_service(monkeypatch, tmp_path):
    """Fixture to initialize a temporary DB for each test."""
    # Create a unique temporary database file path for each test
    temp_db_path = tmp_path / "test_artists.db"

    # Patch DB_FILE to use the temporary file path *before* importing the service
    monkeypatch.setattr(
        "services.artist_db_service.DB_FILE", str(temp_db_path)
    )
    # Ensure the data directory mock doesn't interfere if os.makedirs is called
    monkeypatch.setattr("os.makedirs", lambda *args, **kwargs: None)

    # Import the service module *after* patching DB_FILE
    import services.artist_db_service as service

    # Initialize the database for the test using the patched path
    try:
        service.initialize_database()
    except Exception as e:
        pytest.fail(
            f"Database initialization failed in test fixture: {e} using path {temp_db_path}"
        )

    yield service

    # Cleanup: tmp_path fixture handles file deletion automatically


# --- Test Cases ---


def test_initialize_database(db_service):
    """Test if the database and table are created."""
    conn = db_service.get_db_connection()
    assert conn is not None, "Failed to get DB connection in test"
    try:
        cursor = conn.cursor()
        # Check if the artists table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='artists';"
        )
        table_exists = cursor.fetchone()
        assert (
            table_exists is not None
        ), "'artists' table not found after initialization"
        assert table_exists["name"] == "artists"

        # Check if the error_reports table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='error_reports';"
        )
        table_exists = cursor.fetchone()
        assert (
            table_exists is not None
        ), "'error_reports' table not found after initialization"
        assert table_exists["name"] == "error_reports"
    finally:
        if conn:
            conn.close()


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
        "status": "Active",  # Use status field
        "autopilot_enabled": True,
        "llm_config": {"provider": "test"},
        "voice_url": "http://example.com/voice.wav",
    }
    added_id = db_service.add_artist(artist_data)
    assert added_id == artist_id  # Check if correct ID is returned

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
    assert retrieved["status"] == "Active"  # Check status
    assert retrieved["autopilot_enabled"] is True  # Check boolean
    assert retrieved["llm_config"] == {"provider": "test"}
    assert retrieved["voice_url"] == "http://example.com/voice.wav"


def test_add_artist_duplicate(db_service):
    """Test that adding an artist with a duplicate ID fails gracefully."""
    artist_id = "artist_dup_test"
    now_iso = datetime.utcnow().isoformat()
    artist_data = {
        "artist_id": artist_id,
        "name": "Dup Test",
        "created_at": now_iso,
        "status": "Candidate",
    }

    added_id1 = db_service.add_artist(artist_data)
    assert added_id1 == artist_id  # First add should succeed
    added_id2 = db_service.add_artist(artist_data)  # Try adding again
    assert added_id2 is None  # Second add should fail (return None)


def test_get_nonexistent_artist(db_service):
    """Test retrieving an artist that does not exist."""
    retrieved = db_service.get_artist("nonexistent_id")
    assert retrieved is None


def test_get_all_artists(db_service):
    """Test retrieving all artists, including status filtering."""
    now_iso = datetime.utcnow().isoformat()
    artist1 = {
        "artist_id": "all1",
        "name": "Artist One",
        "created_at": now_iso,
        "status": "Active",
    }
    artist2 = {
        "artist_id": "all2",
        "name": "Artist Two",
        "created_at": now_iso,
        "status": "Paused",
    }
    artist3 = {
        "artist_id": "all3",
        "name": "Artist Three",
        "created_at": now_iso,
        "status": "Active",
    }

    db_service.add_artist(artist1)
    db_service.add_artist(artist2)
    db_service.add_artist(artist3)

    all_artists = db_service.get_all_artists()
    assert len(all_artists) == 3
    assert {a["artist_id"] for a in all_artists} == {"all1", "all2", "all3"}

    active_artists = db_service.get_all_artists(
        status_filter="Active"
    )  # Use status_filter
    assert len(active_artists) == 2
    assert {a["artist_id"] for a in active_artists} == {"all1", "all3"}

    paused_artists = db_service.get_all_artists(status_filter="Paused")
    assert len(paused_artists) == 1
    assert paused_artists[0]["artist_id"] == "all2"


def test_update_artist(db_service):
    """Test updating fields of an existing artist."""
    artist_id = "update_test"
    now_iso = datetime.utcnow().isoformat()
    initial_data = {
        "artist_id": artist_id,
        "name": "Initial Name",
        "genre": "initial",
        "created_at": now_iso,
        "status": "Candidate",
        "autopilot_enabled": False,
    }
    added_id = db_service.add_artist(initial_data)
    assert added_id == artist_id

    update_payload = {
        "name": "Updated Name",
        "style_notes": "Now with style!",
        "status": "Active",  # Update status
        "autopilot_enabled": True,  # Update boolean
        "llm_config": {"provider": "updated"},
        "voice_url": "http://new.voice/url",
    }
    updated = db_service.update_artist(artist_id, update_payload)
    assert updated is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["name"] == "Updated Name"
    assert retrieved["genre"] == "initial"  # Unchanged field
    assert retrieved["style_notes"] == "Now with style!"
    assert retrieved["status"] == "Active"  # Check updated status
    assert retrieved["autopilot_enabled"] is True  # Check updated boolean
    assert retrieved["llm_config"] == {"provider": "updated"}
    assert retrieved["voice_url"] == "http://new.voice/url"


def test_update_nonexistent_artist(db_service):
    """Test that updating a non-existent artist fails."""
    updated = db_service.update_artist(
        "nonexistent_update", {"name": "Wont Work"}
    )
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
        "status": "Active",
    }
    added_id = db_service.add_artist(initial_data)
    assert added_id == artist_id

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
    assert (
        retrieved["status"] == "Active"
    )  # Status shouldn't change on approval


def test_update_artist_performance_rejected(db_service):
    """Test updating performance after a rejected run."""
    artist_id = "perf_reject_test"
    now_iso = datetime.utcnow().isoformat()
    initial_data = {
        "artist_id": artist_id,
        "name": "Perf Reject",
        "created_at": now_iso,
        "consecutive_rejections": 1,
        "status": "Active",
    }
    added_id = db_service.add_artist(initial_data)
    assert added_id == artist_id

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
    assert retrieved["status"] == "Active"  # Status shouldn't change yet


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
        "status": "Active",
    }
    added_id = db_service.add_artist(initial_data)
    assert added_id == artist_id

    # Last rejection to trigger retirement
    updated = db_service.update_artist_performance_db(
        artist_id, "run_retire", "rejected", retirement_threshold
    )
    assert updated is True

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert retrieved["last_run_at"] is not None
    assert retrieved["consecutive_rejections"] == retirement_threshold
    assert retrieved["status"] == "Retired"  # Should be retired

    # Test that another rejection doesn't change status if already retired
    updated_again = db_service.update_artist_performance_db(
        artist_id, "run_after_retire", "rejected", retirement_threshold
    )
    assert updated_again is True
    retrieved_again = db_service.get_artist(artist_id)
    assert retrieved_again["status"] == "Retired"
    assert (
        retrieved_again["consecutive_rejections"] == retirement_threshold + 1
    )  # Count still increments


def test_update_artist_performance_history_limit(db_service, monkeypatch):
    """Test that performance history is capped at MAX_HISTORY_LENGTH."""
    artist_id = "perf_history_test"
    now_iso = datetime.utcnow().isoformat()
    test_max_history = 3
    # Temporarily reduce max history for test using monkeypatch
    monkeypatch.setattr(
        "services.artist_db_service.MAX_HISTORY_LENGTH", test_max_history
    )

    initial_data = {
        "artist_id": artist_id,
        "name": "Perf History",
        "created_at": now_iso,
        "status": "Active",
    }
    added_id = db_service.add_artist(initial_data)
    assert added_id == artist_id

    # Add more history entries than the limit
    num_entries_to_add = test_max_history + 2
    for i in range(num_entries_to_add):
        updated = db_service.update_artist_performance_db(
            artist_id, f"run_{i}", "approved", 5
        )
        assert updated is True, f"Update failed for run_{i}"

    retrieved = db_service.get_artist(artist_id)
    assert retrieved is not None
    assert (
        len(retrieved["performance_history"]) == test_max_history
    ), f"Expected history length {test_max_history}, got {len(retrieved['performance_history'])}"

    # Check if the oldest entries were removed (indices are 0-based)
    # The first entry should be the one added at index `num_entries_to_add - test_max_history`
    expected_first_run_id = f"run_{num_entries_to_add - test_max_history}"
    # The last entry should be the last one added
    expected_last_run_id = f"run_{num_entries_to_add - 1}"

    assert (
        retrieved["performance_history"][0]["run_id"] == expected_first_run_id
    ), f"Expected first run_id {expected_first_run_id}, got {retrieved['performance_history'][0]['run_id']}"
    assert (
        retrieved["performance_history"][-1]["run_id"] == expected_last_run_id
    ), f"Expected last run_id {expected_last_run_id}, got {retrieved['performance_history'][-1]['run_id']}"


# Note: No need to restore MAX_HISTORY_LENGTH, monkeypatch handles it.

# --- Error Report Tests (Placeholder - Add if needed) ---
# def test_add_error_report(db_service):
#     ...
# def test_get_error_report(db_service):
#     ...
# def test_update_error_report_status(db_service):
#     ...
# def test_get_error_reports_by_status(db_service):
#     ...
# def test_prune_error_reports(db_service):
#     ...
