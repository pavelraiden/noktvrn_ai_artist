#!/usr/bin/env python3
"""
Helper script to toggle the autopilot_enabled flag for a specific artist.
"""

import argparse
import logging
import os
import sys

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Import DB functions ---
try:
    from services.artist_db_service import get_artist, update_artist, initialize_database
except ImportError as e:
    print(f"Error: Failed to import database service: {e}", file=sys.stderr)
    sys.exit(1)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Toggle autopilot mode for an AI artist.")
    parser.add_argument("artist_id", help="The ID of the artist to modify.")
    parser.add_argument("autopilot_status", type=str, choices=["on", "off"], help="Set autopilot mode to 'on' or 'off'.")

    args = parser.parse_args()

    artist_id = args.artist_id
    enable_autopilot = args.autopilot_status == "on"

    # Ensure DB is initialized
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Check if artist exists
    artist = get_artist(artist_id)
    if not artist:
        logger.error(f"Artist with ID 	{artist_id}	 not found in the database.")
        sys.exit(1)

    logger.info(f"Artist 	{artist_id}	 (	{artist.get("name")}	) current autopilot status: {artist.get("autopilot_enabled")}")

    # Update artist status
    update_data = {"autopilot_enabled": enable_autopilot}
    success = update_artist(artist_id, update_data)

    if success:
        logger.info(f"Successfully updated artist 	{artist_id}	 autopilot status to: {enable_autopilot}")
        # Verify update
        updated_artist = get_artist(artist_id)
        if updated_artist:
            logger.info(f"Verified new autopilot status: {updated_artist.get("autopilot_enabled")}")
        else:
            logger.warning("Could not re-fetch artist to verify update.")
    else:
        logger.error(f"Failed to update autopilot status for artist 	{artist_id}	.")
        sys.exit(1)

if __name__ == "__main__":
    main()

