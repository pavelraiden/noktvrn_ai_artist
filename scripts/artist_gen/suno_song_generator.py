"""
Suno AI Song Generation Script

This script handles the generation of songs using the Suno AI API.
It creates song requests based on artist profiles and handles the API
    interaction.
"""

import os
import json
import requests
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(    level=logging.INFO,     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",     handlers=[        logging.FileHandler("logs/suno_api.log"),         logging.StreamHandler(),    ],)
logger = logging.getLogger("suno_api")

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Load API key from environment
SUNO_API_KEY = os.getenv("SUNO_API_KEY")
if not SUNO_API_KEY:
    logger.error("SUNO_API_KEY not found in environment variables")
    raise ValueError("SUNO_API_KEY environment variable is required")

# API endpoints
SUNO_API_BASE = "https://api.suno.ai/v1"
SUNO_GENERATE_ENDPOINT = f"{SUNO_API_BASE}/generate"
SUNO_STATUS_ENDPOINT = f"{SUNO_API_BASE}/generations"

# Default paths - using string for formatting
DEFAULT_OUTPUT_DIR_TEMPLATE = "artists/{artist_slug}/songs"


class SunoSongGenerator:
    """Class to handle Suno AI song generation."""

    def __init__(self, api_key=None):
        """Initialize the Suno song generator.

        Args:
            api_key (str, optional):
                Suno API key. Defaults to environment variable.
        """
        self.api_key = api_key or SUNO_API_KEY
        self.headers = {            "Authorization": f"Bearer {self.api_key}",             "Content-Type": "application/json",        }

    def generate_song(        self,         title,         prompt,         artist_slug,         genre=None,         reference_song=None,         bpm=None,         duration=None,         output_dir=None,         wait_for_completion=False,         check_interval=10,         max_wait_time=300,    ):
        """Generate a song using Suno AI.

        Args:
            title (str): Title of the song
            prompt (str): Detailed prompt describing the song
            artist_slug (str): Artist identifier
            genre (str, optional): Music genre. Defaults to None.
            reference_song (str, optional):
                Reference song URL. Defaults to None.
            bpm (int, optional): Beats per minute. Defaults to None.
            duration (int, optional): Duration in seconds. Defaults to None.
            output_dir (Path, optional):
                Output directory. Defaults to artist songs directory.
            wait_for_completion (bool, optional):
                Whether to wait for generation to complete. Defaults to False.
            check_interval (int, optional):
                Interval in seconds to check generation status. Defaults to 10.
            max_wait_time (int, optional):
                Maximum wait time in seconds. Defaults to 300.

        Returns:
            dict: Response from Suno API with generation details
        """
        # Prepare output directory
        if output_dir is None:
            # Fix: Use string formatting and then convert to Path
            output_dir = DEFAULT_OUTPUT_DIR_TEMPLATE.format(                artist_slug=artist_slug            )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Prepare request payload
        payload = {            "title": title,             "description": prompt,        }

        # Add optional parameters if provided
        if genre:
            payload["genre"] = genre
        if reference_song:
            payload["reference_song"] = reference_song
        if bpm:
            payload["bpm"] = bpm
        if duration:
            payload["duration"] = duration

        logger.info(f"Generating song '{title}' for artist '{artist_slug}'")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            # Make API request
            response = requests.post(                SUNO_GENERATE_ENDPOINT, headers=self.headers, json=payload            )
            response.raise_for_status()
            generation_data = response.json()

            # Save generation request data
            request_file = (                output_path / f"{self._sanitize_filename(title)}_request.json"            )
            with open(request_file, "w") as f:
                json.dump(                    {"request": payload, "initial_response": generation_data},                     f,                     indent=2,                )

            generation_id = generation_data.get("id")
            logger.info(f"Song generation initiated with ID: {generation_id}")

            # Wait for completion if requested
            if wait_for_completion and generation_id:
                return self._wait_for_completion(                    generation_id,                     output_path,                     title,                     check_interval,                     max_wait_time,                )

            return generation_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating song: {str(e)}")
            if hasattr(e, "response") and e.response:
                logger.error(f"Response: {e.response.text}")
            return {"error": str(e)}

    def check_generation_status(self, generation_id):
        """Check the status of a song generation.

        Args:
            generation_id (str): Generation ID from Suno

        Returns:
            dict: Status response from Suno API
        """
        try:
            response = requests.get(                f"{SUNO_STATUS_ENDPOINT}/{generation_id}", headers=self.headers            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking generation status: {str(e)}")
            if hasattr(e, "response") and e.response:
                logger.error(f"Response: {e.response.text}")
            return {"error": str(e)}

    def _wait_for_completion(        self, generation_id, output_path, title, check_interval, max_wait_time    ):
        """Wait for song generation to complete.

        Args:
            generation_id (str): Generation ID from Suno
            output_path (Path): Path to save the result
            title (str): Song title
            check_interval (int): Interval in seconds to check status
            max_wait_time (int): Maximum wait time in seconds

        Returns:
            dict: Final generation data
        """
        logger.info(f"Waiting for generation {generation_id} to complete...")

        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            status_data = self.check_generation_status(generation_id)

            if "error" in status_data:
                logger.error(                    "Error while waiting for completion: "                     f"{status_data['error']}"                )
                return status_data

            status = status_data.get("status", "").lower()
            logger.info(f"Generation status: {status}")

            # Save the current status
            status_file = (                output_path / f"{self._sanitize_filename(title)}_status.json"            )
            with open(status_file, "w") as f:
                json.dump(status_data, f, indent=2)

            if status == "completed":
                logger.info("Generation completed successfully!")

                # Download the generated song if available
                if "audio_url" in status_data:
                    self._download_song(                        status_data["audio_url"],                         output_path / f"{self._sanitize_filename(title)}.mp3",                    )

                return status_data
            elif status in ["failed", "error"]:
                logger.error(                    f"Generation failed: {status_data.get('error', 'Unknown                         error')}"                )
                return status_data

            # Wait before checking again
            time.sleep(check_interval)

        logger.warning(            f"Reached maximum wait time ({max_wait_time}s) for generation                 {generation_id}"        )
        return {            "error": "Timeout waiting for generation to complete",             "generation_id": generation_id,        }

    def _download_song(self, url, output_path):
        """Download the generated song.

        Args:
            url (str): URL to download from
            output_path (Path): Path to save the song

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading song to {output_path}")
            response = requests.get(url)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Song downloaded successfully to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading song: {str(e)}")
            return False

    @staticmethod
    def _sanitize_filename(filename):
        """Sanitize a filename to be safe for all operating systems.

        Args:
            filename (str): Original filename

        Returns:
            str: Sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Replace spaces with underscores and convert to lowercase
        return filename.replace(" ", "_").lower()


def generate_song_from_artist_profile(    artist_slug, song_title, song_prompt, genre=None, wait_for_completion=False):
    """Generate a song based on an artist profile.

    Args:
        artist_slug (str): Artist identifier
        song_title (str): Title of the song
        song_prompt (str): Detailed prompt for the song
        genre (str, optional): Music genre. Defaults to None.
        wait_for_completion (bool, optional):
            Whether to wait for generation. Defaults to False.

    Returns:
        dict: Response from Suno API
    """
    generator = SunoSongGenerator()

    # Load artist profile to get genre if not provided
    if not genre:
        try:
            profile_path = Path(f"artists/{artist_slug}/profile.json")
            if profile_path.exists():
                with open(profile_path, "r") as f:
                    profile = json.load(f)

                # Extract genre based on profile structure
                if isinstance(profile.get("genre"), dict):
                    genre = profile["genre"].get("main")
                else:
                    genre = profile.get("genre")

                logger.info(f"Using genre '{genre}' from artist profile")
        except Exception as e:
            logger.warning(                f"Could not load genre from artist profile: {str(e)}"            )

    # Generate the song
    return generator.generate_song(        title=song_title,         prompt=song_prompt,         artist_slug=artist_slug,         genre=genre,         wait_for_completion=wait_for_completion,    )


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(        description="Generate songs using Suno AI"    )
    parser.add_argument(        "--artist", required=True, help="Artist slug/identifier"    )
    parser.add_argument("--title", required=True, help="Song title")
    parser.add_argument(        "--prompt", required=True, help="Song prompt/description"    )
    parser.add_argument("--genre", help="Music genre")
    parser.add_argument(        "--wait", action="store_true", help="Wait for generation to complete"    )

    args = parser.parse_args()

    result = generate_song_from_artist_profile(        artist_slug=args.artist,         song_title=args.title,         song_prompt=args.prompt,         genre=args.genre,         wait_for_completion=args.wait,    )

    print(json.dumps(result, indent=2))