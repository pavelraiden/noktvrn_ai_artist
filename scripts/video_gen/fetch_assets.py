"""
Enhanced Fetch Assets Script

This script fetches video assets from Pixabay and Pexels APIs based on
    keywords.
It includes improved error handling, logging, and API key validation.
"""

import os
import json
import requests
import logging
from pathlib import Path
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/video_assets.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("video_assets")

# Load API keys from environment
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Validate API keys
if not PIXABAY_API_KEY:
    logger.error("PIXABAY_KEY not found in environment variables")
    raise ValueError("PIXABAY_KEY environment variable is required")

if not PEXELS_API_KEY:
    logger.error("PEXELS_KEY not found in environment variables")
    raise ValueError("PEXELS_KEY environment variable is required")

ASSETS_DIR = Path("assets/raw_sources/")


def fetch_pixabay(keyword, limit=1):
    """Fetch video from Pixabay API.

    Args:
        keyword (str): Search keyword
        limit (int, optional): Number of results to fetch. Defaults to 1.

    Returns:
        str: URL of the video or None if not found
    """
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={keyword}&per_page={limit}"
    logger.info(f"Fetching from Pixabay: {keyword}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        hits = data.get("hits", [])
        if hits:
            video_url = hits[0]["videos"]["medium"]["url"]
            logger.info(f"Pixabay video found for '{keyword}'")
            return video_url
        else:
            logger.warning(f"No videos found on Pixabay for '{keyword}'")
    except requests.exceptions.RequestException as e:
        logger.error(f"Pixabay API error for '{keyword}': {str(e)}")
        if hasattr(e, "response") and e.response:
            logger.error(f"Response: {e.response.text}")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching from Pixabay for '{keyword}': {str(e)}"
        )

    return None


def fetch_pexels(keyword, limit=1):
    """Fetch video from Pexels API.

    Args:
        keyword (str): Search keyword
        limit (int, optional): Number of results to fetch. Defaults to 1.

    Returns:
        str: URL of the video or None if not found
    """
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page={limit}"
    headers = {"Authorization": PEXELS_API_KEY}
    logger.info(f"Fetching from Pexels: {keyword}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        videos = data.get("videos", [])
        if videos and videos[0].get("video_files"):
            video_url = videos[0]["video_files"][0]["link"]
            logger.info(f"Pexels video found for '{keyword}'")
            return video_url
        else:
            logger.warning(f"No videos found on Pexels for '{keyword}'")
    except requests.exceptions.RequestException as e:
        logger.error(f"Pexels API error for '{keyword}': {str(e)}")
        if hasattr(e, "response") and e.response:
            logger.error(f"Response: {e.response.text}")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching from Pexels for '{keyword}': {str(e)}"
        )

    return None


def fallback_mixkit(keyword):
    """Provide fallback video from MixKit if API requests fail.

    Args:
        keyword (str): Search keyword

    Returns:
        str: URL of the fallback video or None if not found
    """
    # Static fallback links from MixKit
    fallback_videos = {
        "drift cars": "https:             //assets.mixkit.co/videos/preview/mixkit-drifting-sports-car-4317-large.mp4",
        "neon city": "https:             //assets.mixkit.co/videos/preview/mixkit-city-billboards-at-night-2432-large.mp4",
        "models": "https:             //assets.mixkit.co/videos/preview/mixkit-fashion-model-posing-on-the-street-4225-large.mp4",
        "concert": "https:             //assets.mixkit.co/videos/preview/mixkit-hands-of-people-at-a-concert-1029-large.mp4",
        "dj": "https:             //assets.mixkit.co/videos/preview/mixkit-dj-playing-music-at-a-nightclub-1235-large.mp4",
        "urban": "https:             //assets.mixkit.co/videos/preview/mixkit-urban-life-in-a-city-at-night-time-lapse-10304-large.mp4",
    }

    if keyword.lower() in fallback_videos:
        logger.info(f"Using MixKit fallback for '{keyword}'")
        return fallback_videos.get(keyword.lower())

    # Try partial matches
    for key, url in fallback_videos.items():
        if key in keyword.lower() or keyword.lower() in key:
            logger.info(
                f"Using MixKit partial match fallback: '{key}' for '{keyword}'"
            )
            return url

    logger.warning(f"No fallback video found for '{keyword}'")
    return None


def download_video(url, output_path):
    """Download video from URL to specified path.

    Args:
        url (str): URL of the video
        output_path (Path): Path to save the video

    Raises:
        Exception: If download fails
    """
    logger.info(f"Downloading video to {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192

        with open(output_path, "wb") as f:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=output_path.name,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        logger.info(f"Successfully downloaded video to {output_path}")
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise


def load_video_plan(plan_path):
    """Load video plan from JSON file.

    Args:
        plan_path (Path): Path to the video plan JSON file

    Returns:
        dict: Video plan data
    """
    logger.info(f"Loading video plan from {plan_path}")
    try:
        with open(plan_path) as f:
            plan = json.load(f)
        logger.info(
            f"Successfully loaded video plan with {len(plan.get('segments',                 []))} segments"
        )
        return plan
    except Exception as e:
        logger.error(f"Error loading video plan: {str(e)}")
        raise


def main(artist="noktvrn", output_log_path=None):
    """Main function to fetch video assets based on a video plan.

    Args:
        artist (str, optional): Artist slug/identifier. Defaults to "noktvrn".
        output_log_path (str, optional):
            Path to save the fetch log. Defaults to "fetch_log.json".
    """
    logger.info(f"Starting video asset fetching for artist: {artist}")

    try:
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)

        # Set default output log path if not provided
        if output_log_path is None:
            output_log_path = f"logs/fetch_log_{artist}.json"

        # Load video plan
        plan_path = Path(f"artists/{artist}/video/video_plan_{artist}.json")
        plan = load_video_plan(plan_path)
        fetched = {}

        # Process each visual in the plan
        total_visuals = sum(
            len(segment.get("visuals", []))
            for segment in plan.get("segments", [])
        )
        logger.info(f"Processing {total_visuals} visuals from the video plan")

        for segment in tqdm(plan.get("segments", []), desc="Fetching assets"):
            for visual in segment.get("visuals", []):
                keyword = visual.replace("_", " ")
                folder = ASSETS_DIR / keyword.replace(" ", "_").lower()

                # Skip if already exists
                if any(folder.glob("*.mp4")):
                    logger.info(
                        f"Asset for '{keyword}' already exists, skipping"
                    )
                    existing_files = list(folder.glob("*.mp4"))
                    fetched[visual] = str(existing_files[0])
                    continue

                logger.info(f"Fetching asset for visual: {visual}")

                # Try APIs in sequence
                url = (
                    fetch_pixabay(keyword)
                    or fetch_pexels(keyword)
                    or fallback_mixkit(keyword)
                )

                if url:
                    filename = keyword.replace(" ", "_").lower() + ".mp4"
                    output_path = folder / filename
                    try:
                        download_video(url, output_path)
                        fetched[visual] = str(output_path)
                    except Exception as e:
                        error_msg = f"Download error: {str(e)}"
                        logger.error(error_msg)
                        fetched[visual] = error_msg
                else:
                    error_msg = "No asset found from any source"
                    logger.error(f"{error_msg} for '{keyword}'")
                    fetched[visual] = error_msg

        # Save fetch log
        with open(output_log_path, "w") as f:
            json.dump(fetched, f, indent=2)

        logger.info(f"✅ Fetch complete. Log saved to {output_log_path}")

        # Summary statistics
        success_count = sum(
            1
            for v in fetched.values()
            if not v.startswith("Download error")
            and not v.startswith("No asset")
        )
        logger.info(
            f"Successfully fetched {success_count} out of {len(fetched)}                 visuals"
        )

        return {
            "status": "success",
            "total_visuals": len(fetched),
            "successful_fetches": success_count,
            "log_path": output_log_path,
        }

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch video assets from Pixabay and Pexels"
    )
    parser.add_argument(
        "--artist", default="noktvrn", help="Artist slug/identifier"
    )
    parser.add_argument("--output", help="Path to save the fetch log")

    args = parser.parse_args()

    result = main(artist=args.artist, output_log_path=args.output)
    print(json.dumps(result, indent=2))
