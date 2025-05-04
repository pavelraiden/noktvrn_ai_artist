"""
Data Pipeline for fetching Spotify chart data and loading it into the database.

This pipeline:
1. Uses the SpotifyApiClient to fetch top playlists (charts) for specified
    countries.
2. Fetches tracks from these playlists.
3. Fetches audio features for the tracks.
4. Transforms the data to fit the database schema.
5. Inserts/updates data into country_profiles, tracks,     and potentially performance_metrics tables.
"""

import logging
import os
import json
from datetime import datetime, timezone

# Assuming the project root is added to PYTHONPATH or running from root
# Adjust imports based on actual project structure if needed
from ai_artist_system.noktvrn_ai_artist.api_clients.spotify_client import (    SpotifyApiClient,)
from ai_artist_system.noktvrn_ai_artist.database.connection_manager import (    init_connection_pool,     close_connection_pool,     get_db_cursor,)

logger = logging.getLogger(__name__)

# Configuration
COUNTRIES = ["US", "GB", "DE", "JP", "BR"]  # Example countries
CHART_CATEGORY_ID = "toplists"
PLAYLIST_LIMIT = 5  # Fetch top 5 chart playlists per country
TRACK_LIMIT_PER_PLAYLIST = 50  # Fetch top 50 tracks per playlist


def transform_playlist_to_country_profile(playlist_data, country_code):
    """Transforms Spotify playlist data (representing a chart) into a
        country_profile update."""
    # This is a simplified transformation. A real implementation would likely
    # aggregate
    # data from multiple playlists/sources for a more comprehensive country
    # profile.
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    profile_id = f"{country_code}_{timestamp}"
    country_name = country_code  # In a real scenario, map code to name

    genre_trends = {        "chart_playlist_name": playlist_data.get("name"),         "chart_playlist_id": playlist_data.get("id"),         "chart_playlist_url": playlist_data.get("external_urls", {}).get(            "spotify"        ),         "description": playlist_data.get("description"),         "snapshot_id": playlist_data.get(            "snapshot_id"        ),  # Useful for tracking changes         "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    # Market data and demographics would likely come from other sources or
    # require more complex analysis
    market_data = {"language": "-", "timezone": "-"}  # Placeholder
    audience_demographics = {}  # Placeholder

    return {        "id": profile_id,         "country_code": country_code,         "country_name": country_name,         "market_data": json.dumps(market_data),         "genre_trends": json.dumps(genre_trends),         "audience_demographics": json.dumps(audience_demographics),    }


def transform_track_data(track_item, artist_id="unknown_external_artist"):
    """Transforms Spotify track item data into the tracks table format."""
    track_info = track_item.get("track")
    if not track_info or not track_info.get("id"):
        return None

    # Basic track info
    track_id = track_info["id"]
    title = track_info.get("name", "Unknown Title")

    # Placeholder for audio features - fetch separately
    audio_features = {
        "popularity": track_info.get("popularity"),
        # TODO: Add BPM, key, energy etc. after fetching audio_features API
    }
    # Generation details are not applicable for external tracks
    generation_prompt_id = None
    generation_metadata = None

    # Performance summary - this would be populated by a separate metrics
    # pipeline
    performance_summary = {}
    return {
        "id": track_id,
        "artist_id": artist_id,  # Need a way to link/create external artists
        "title": title,
        "audio_features": json.dumps(audio_features),
        "generation_prompt_id": generation_prompt_id,
        "generation_metadata": json.dumps(generation_metadata),
        "performance_summary": json.dumps(performance_summary),
        # created_at/updated_at are handled by DB defaults/triggers
    }


def run_spotify_charts_pipeline():
    """Executes the Spotify charts data pipeline."""
    logger.info("Starting Spotify charts pipeline...")
    spotify_client = SpotifyApiClient()

    if not spotify_client.is_available():
        logger.error(            "Spotify client not available. Check credentials. Aborting pipeline."        )
        return
    all_tracks_to_insert = {}
    all_country_profiles_to_insert = []

    for country in COUNTRIES:
        logger.info(f"Processing country: {country}")
        toplists = spotify_client.get_category_playlists(            category_id=CHART_CATEGORY_ID,             country=country,             limit=PLAYLIST_LIMIT,        )

        if not toplists or not toplists.get("playlists", {}).get("items"):
            logger.warning(f"No toplists found for country: {country}")
            continue

        for playlist in toplists["playlists"]["items"]:
            playlist_id = playlist.get("id")
            if not playlist_id:
                continue

            playlist_name = playlist.get("name", "Unknown Playlist")
            logger.info(                f"Processing playlist: {playlist_name} (ID: {playlist_id})"            )

            # Transform and store country profile based on playlist info
            # (simplified)
            country_profile_data = transform_playlist_to_country_profile(                playlist, country            )
            all_country_profiles_to_insert.append(country_profile_data)

            # Fetch tracks from the playlist
            tracks_response = spotify_client.get_playlist_tracks(                playlist_id, limit=TRACK_LIMIT_PER_PLAYLIST            )
            if not tracks_response or not tracks_response.get("items"):
                logger.warning(f"No tracks found for playlist: {playlist_id}")
                continue

            track_ids_in_playlist = []
            for item in tracks_response["items"]:
                track_data = transform_track_data(item)
                if track_data:
                    # Store unique tracks using ID as key to avoid duplicates
                    # across playlists/countries
                    if track_data["id"] not in all_tracks_to_insert:
                        all_tracks_to_insert[track_data["id"]] = track_data
                    track_ids_in_playlist.append(track_data["id"])

            # Fetch audio features for tracks in this playlist (batching is             # good)
            if track_ids_in_playlist:
                logger.info(f"Fetching audio features for {len(track_ids_in_playlist)} tracks...")
                audio_features_list = spotify_client.get_audio_features(                    track_ids_in_playlist                )
                if audio_features_list:
                    for features in audio_features_list:
                        track_id = features.get("id")
                        if track_id in all_tracks_to_insert:
                            # Update the track data with audio features
                            existing_features = json.loads(
                                all_tracks_to_insert[track_id]["audio_features"]
                            )
                            existing_features.update(
                                {
                                    "bpm": features.get("tempo"),
                                    "key": features.get(
                                        "key"
                                    ),  # Numerical key, might need mapping
                                    "mode": features.get(
                                        "mode"
                                    ),  # Major/Minor
                                    "energy": features.get("energy"),
                                    "danceability": features.get(
                                        "danceability"
                                    ),
                                    "valence": features.get("valence"),
                                    "duration_ms": features.get("duration_ms"),
                                    "time_signature": features.get(
                                        "time_signature"
                                    ),
                                    "acousticness": features.get(
                                        "acousticness"
                                    ),
                                    "instrumentalness": features.get(
                                        "instrumentalness"
                                    ),
                                    "liveness": features.get("liveness"),
                                    "loudness": features.get("loudness"),
                                    "speechiness": features.get("speechiness"),
                                }
                            )
                            all_tracks_to_insert[track_id][
                                "audio_features"
                            ] = json.dumps(existing_features)

    # --- Database Insertion ---
    logger.info(f"Attempting to insert {len(all_country_profiles_to_insert)} country profile entries and {len(all_tracks_to_insert)} unique tracks.")
    try:
        with get_db_cursor(commit=True) as cursor:
            # Insert Country Profiles
            if all_country_profiles_to_insert:
                logger.info("Inserting country profiles...")
                insert_query_cp = """
                    INSERT INTO country_profiles (id, country_code,                         country_name, market_data, genre_trends,                         audience_demographics)
                    VALUES (%(id)s, %(country_code)s, %(country_name)s,                         %(market_data)s::jsonb, %(genre_trends)s::jsonb,                         %(audience_demographics)s::jsonb)
                    ON CONFLICT (id) DO NOTHING; -- Simple conflict handling
                """
                # Consider using execute_batch for efficiency if psycopg2
                # version supports it well
                for profile_data in all_country_profiles_to_insert:
                    try:
                        cursor.execute(insert_query_cp, profile_data)
                    except Exception as insert_error:
                        profile_id = profile_data.get("id")
                        error_msg = f"Error inserting country profile {profile_id}: {insert_error}"
                        logger.error(error_msg)
                        # Optionally rollback or continue

            # Insert Tracks (handle potential conflicts)
            if all_tracks_to_insert:
                logger.info("Inserting tracks...")
                insert_query_track = """
                    INSERT INTO tracks (id, artist_id, title, audio_features,                         generation_prompt_id, generation_metadata,                         performance_summary)
                    VALUES (%(id)s, %(artist_id)s, %(title)s,                         %(audio_features)s::jsonb, %(generation_prompt_id)s,                         %(generation_metadata)s::jsonb, %(performance_summary)s::jsonb)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,                         audio_features = EXCLUDED.audio_features,
                        updated_at = NOW(); -- Update timestamp on conflict
                """
                for track_id, track_data in all_tracks_to_insert.items():
                    try:
                        cursor.execute(insert_query_track, track_data)
                    except Exception as insert_error:
                        error_msg = (                            f"Error inserting track {track_id}: {insert_error}"                        )
                        logger.error(error_msg)
                        # Optionally rollback or continue

        logger.info("Database insertion complete.")

    except Exception as db_error:
        logger.error(            f"Database error during pipeline execution: {db_error}",             exc_info=True        )

    logger.info("Spotify charts pipeline finished.")


if __name__ == "__main__":
    logging.basicConfig(        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"    )

    # Make sure to set DB and Spotify credentials as environment variables
    if not all(        os.environ.get(var)         for var in [            "DB_HOST",             "DB_PORT",             "DB_NAME",             "DB_USER",             "DB_PASSWORD",             "SPOTIPY_CLIENT_ID",             "SPOTIPY_CLIENT_SECRET",        ]    ):
        print(            "\nPlease set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,                 SPOTIPY_CLIENT_ID,                 and SPOTIPY_CLIENT_SECRET environment variables to run example.\n"        )
    else:
        try:
            init_connection_pool()
            run_spotify_charts_pipeline()
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
        finally:
            close_connection_pool()