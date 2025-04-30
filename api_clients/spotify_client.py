"""
Spotify API Client

This module provides a client to interact with the Spotify Web API using the Spotipy library.
It focuses on fetching public data like charts and potentially artist/track information
for trend and competitor analysis.
"""

import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger(__name__)

# Spotify API credentials (from environment variables)
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

class SpotifyApiClient:
    def __init__(self):
        """Initializes the Spotify API client using Client Credentials Flow."""
        self.client = None
        if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
            logger.warning("Spotify API credentials (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET) not found in environment variables. Client will not be initialized.")
            return

        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET
            )
            self.client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            logger.info("Spotify API client initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Spotify API client: {e}", exc_info=True)
            self.client = None

    def is_available(self):
        """Check if the client was initialized successfully."""
        return self.client is not None

    def get_category_playlists(self, category_id=\"toplists\", country=\"US\", limit=50):
        """Fetches playlists for a given category, often used for charts.

        Args:
            category_id (str): The Spotify category ID (e.g., \"toplists\", \"pop\").
            country (str): ISO 3166-1 alpha-2 country code.
            limit (int): The maximum number of playlists to return.

        Returns:
            dict: API response containing playlists, or None if an error occurs.
        """
        if not self.is_available():
            logger.error("Spotify client not available.")
            return None
        try:
            logger.info(f"Fetching category playlists for category 
{category_id} in country {country}")
            results = self.client.category_playlists(category_id=category_id, country=country, limit=limit)
            return results
        except Exception as e:
            logger.error(f"Error fetching category playlists: {e}", exc_info=True)
            return None

    def get_playlist_tracks(self, playlist_id, limit=100, offset=0):
        """Fetches tracks from a specific playlist.

        Args:
            playlist_id (str): The Spotify ID of the playlist.
            limit (int): The maximum number of tracks to return.
            offset (int): The index of the first track to return.

        Returns:
            dict: API response containing playlist tracks, or None if an error occurs.
        """
        if not self.is_available():
            logger.error("Spotify client not available.")
            return None
        try:
            logger.info(f"Fetching tracks for playlist {playlist_id}")
            # Note: Spotipy might automatically handle pagination for playlist_items
            # Check documentation if full list is needed beyond limit.
            results = self.client.playlist_items(playlist_id, limit=limit, offset=offset, fields=\"items(track(id, name, artists(id, name), album(id, name, release_date), popularity, external_urls))\")
            return results
        except Exception as e:
            logger.error(f"Error fetching playlist tracks: {e}", exc_info=True)
            return None

    def search_artists(self, query, limit=10):
        """Searches for artists on Spotify.

        Args:
            query (str): The search query.
            limit (int): The maximum number of artists to return.

        Returns:
            dict: API response containing artist search results, or None if an error occurs.
        """
        if not self.is_available():
            logger.error("Spotify client not available.")
            return None
        try:
            logger.info(f"Searching for artists with query: 
{query}")
            results = self.client.search(q=query, type=\"artist\", limit=limit)
            return results.get(\"artists\") # Return the artists part of the response
        except Exception as e:
            logger.error(f"Error searching artists: {e}", exc_info=True)
            return None

    def get_artist_top_tracks(self, artist_id, country=\"US\"):
        """Fetches the top tracks for a specific artist in a given country.

        Args:
            artist_id (str): The Spotify ID of the artist.
            country (str): ISO 3166-1 alpha-2 country code.

        Returns:
            dict: API response containing artist top tracks, or None if an error occurs.
        """
        if not self.is_available():
            logger.error("Spotify client not available.")
            return None
        try:
            logger.info(f"Fetching top tracks for artist {artist_id} in country {country}")
            results = self.client.artist_top_tracks(artist_id, country=country)
            return results
        except Exception as e:
            logger.error(f"Error fetching artist top tracks: {e}", exc_info=True)
            return None

    def get_audio_features(self, track_ids):
        """Fetches audio features for one or more tracks.

        Args:
            track_ids (list or str): A list of Spotify track IDs or a single track ID string.

        Returns:
            list: A list of audio features objects, or None if an error occurs.
        """
        if not self.is_available():
            logger.error("Spotify client not available.")
            return None
        if not track_ids:
            return []
        try:
            logger.info(f"Fetching audio features for {len(track_ids) if isinstance(track_ids, list) else 1} track(s)")
            results = self.client.audio_features(tracks=track_ids)
            # Filter out None results if any track ID was invalid
            return [features for features in results if features is not None]
        except Exception as e:
            logger.error(f"Error fetching audio features: {e}", exc_info=True)
            return None

# Example Usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Make sure to set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
    if not os.environ.get("SPOTIPY_CLIENT_ID") or not os.environ.get("SPOTIPY_CLIENT_SECRET"):
        print("\nPlease set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables to run example.\n")
    else:
        spotify_client = SpotifyApiClient()

        if spotify_client.is_available():
            # Example 1: Get Top 50 playlists for US
            toplists = spotify_client.get_category_playlists(category_id=\"toplists\", country=\"US\", limit=5)
            if toplists and toplists.get(\"playlists\", {}).get(\"items\"):
                print("\n--- Top Playlists (US) ---")
                for playlist in toplists[\"playlists\"][\"items\"]:
                    print(f"- {playlist[\"name\"]} (ID: {playlist[\"id\"]})")
                
                # Example 2: Get tracks from the first playlist
                first_playlist_id = toplists[\"playlists\"][\"items\"][0][\"id\"]
                tracks = spotify_client.get_playlist_tracks(first_playlist_id, limit=5)
                if tracks and tracks.get(\"items\"):
                    print(f"\n--- Tracks from 
{toplists[\"playlists\"][\"items\"][0][\"name\"]} ---")
                    track_ids_for_features = []
                    for item in tracks[\"items\"]:
                        track = item.get(\"track\")
                        if track and track.get(\"id\"):
                            print(f"- {track[\"name\"]} by {', '.join([a['name'] for a in track['artists']])}")
                            track_ids_for_features.append(track[\"id\"])
                    
                    # Example 3: Get audio features for these tracks
                    if track_ids_for_features:
                        features = spotify_client.get_audio_features(track_ids_for_features)
                        if features:
                            print("\n--- Audio Features ---")
                            for feature in features:
                                print(f"- Track ID: {feature['id']}, Tempo: {feature['tempo']:.2f}, Energy: {feature['energy']:.2f}, Danceability: {feature['danceability']:.2f}")
            else:
                print("Could not fetch top playlists.")

            # Example 4: Search for an artist
            artist_search = spotify_client.search_artists(\"Synthwave Rider\", limit=1) # Hypothetical search
            if artist_search and artist_search.get(\"items\"):
                print("\n--- Artist Search Result ---")
                found_artist = artist_search[\"items\"][0]
                print(f"- Found: {found_artist[\"name\"]} (ID: {found_artist[\"id\"]})")
            else:
                print("\nArtist search did not return results.")
        else:
            print("Spotify client could not be initialized. Check credentials.")

