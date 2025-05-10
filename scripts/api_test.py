"""
API Integration Test Script

This script tests the integration with Suno, Pixabay, and Pexels APIs
to ensure they are properly configured and working.
"""

from scripts.utils.env_utils import load_env_file
import os
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/api_test.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("api_test")

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Load environment variables from .env file

env_loaded = load_env_file()
if not env_loaded:
    logger.error("Failed to load environment variables from .env file")
    # sys.exit(1) # Commented out to allow pytest collection
else:
    logger.info("Successfully loaded environment variables from .env file")

# Import modules to test
try:
    from artist_gen.suno_song_generator import SunoSongGenerator
    from video_gen.fetch_assets import fetch_pixabay, fetch_pexels
except ImportError as e:
    logger.error(f"Error importing modules: {str(e)}")
    logger.error(
        "Make sure you're running this script from the project root directory"
    )
    # sys.exit(1) # Commented out to allow pytest collection

# Test data
TEST_SONG_TITLE = "Test Song"
TEST_SONG_PROMPT = (
    "A catchy electronic song with a futuristic vibe and upbeat tempo"
)
TEST_ARTIST_SLUG = "test_artist"
TEST_VIDEO_KEYWORDS = [
    "retro car race",
    "city night lights",
    "electronic music concert",
]


def test_suno_api():
    """Test Suno API integration.

    Returns:
        dict: Test results
    """
    logger.info("Testing Suno API integration...")

    # Check if API key is set
    suno_api_key = os.getenv("SUNO_API_KEY")
    if not suno_api_key:
        logger.error("SUNO_API_KEY not found in environment variables")
        return {
            "status": "error",
            "message": "SUNO_API_KEY not found in environment variables",
        }

    try:
        # Initialize generator
        generator = SunoSongGenerator()

        # Generate a test song
        logger.info(f"Generating test song: {TEST_SONG_TITLE}")
        result = generator.generate_song(
            title=TEST_SONG_TITLE,
            prompt=TEST_SONG_PROMPT,
            artist_slug=TEST_ARTIST_SLUG,
            genre="Electronic",
            wait_for_completion=False,  # Set to True to wait (takes longer)
        )

        # Check result
        if "error" in result:
            logger.error(f"Suno API error: {result['error']}")
            return {
                "status": "error",
                "message": f"Suno API error: {result['error']}",
                "raw_response": result,
            }

        generation_id = result.get("id")
        if not generation_id:
            logger.error("No generation ID returned from Suno API")
            return {
                "status": "error",
                "message": "No generation ID returned from Suno API",
                "raw_response": result,
            }

        logger.info(
            f"Successfully initiated song generation with ID: {generation_id}"
        )
        return {
            "status": "success",
            "message": f"Successfully initiated song generation with ID: {generation_id}",
            "generation_id": generation_id,
            "raw_response": result,
        }

    except Exception as e:
        logger.error(f"Error testing Suno API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error testing Suno API: {str(e)}",
        }


def test_pixabay_api():
    """Test Pixabay API integration.

    Returns:
        dict: Test results
    """
    logger.info("Testing Pixabay API integration...")

    # Check if API key is set
    pixabay_api_key = os.getenv("PIXABAY_KEY")
    if not pixabay_api_key:
        logger.error("PIXABAY_KEY not found in environment variables")
        return {
            "status": "error",
            "message": "PIXABAY_KEY not found in environment variables",
        }

    results = {}
    success_count = 0

    try:
        # Test with multiple keywords
        for keyword in TEST_VIDEO_KEYWORDS:
            logger.info(f"Fetching video from Pixabay for keyword: {keyword}")
            video_url = fetch_pixabay(keyword)

            if video_url:
                logger.info(
                    f"Successfully fetched video from Pixabay for keyword: {keyword}"
                )
                results[keyword] = {"status": "success", "url": video_url}
                success_count += 1
            else:
                logger.warning(
                    f"No video found on Pixabay for keyword: {keyword}"
                )
                results[keyword] = {
                    "status": "warning",
                    "message": "No video found",
                }

        # Overall status
        if success_count == 0:
            overall_status = "error"
            message = "Failed to fetch any videos from Pixabay"
        elif success_count < len(TEST_VIDEO_KEYWORDS):
            overall_status = "partial_success"
            message = (
                f"Successfully fetched {success_count} out of "
                f"{len(TEST_VIDEO_KEYWORDS)} videos from Pixabay"
            )
        else:
            overall_status = "success"
            # Corrected multi-line f-string
            message = (
                f"Successfully fetched all {len(TEST_VIDEO_KEYWORDS)} "
                f"videos from Pixabay"
            )

        return {
            "status": overall_status,
            "message": message,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error testing Pixabay API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error testing Pixabay API: {str(e)}",
            "results": results,
        }


def test_pexels_api():
    """Test Pexels API integration.

    Returns:
        dict: Test results
    """
    logger.info("Testing Pexels API integration...")

    # Check if API key is set
    pexels_api_key = os.getenv("PEXELS_KEY")
    if not pexels_api_key:
        logger.error("PEXELS_KEY not found in environment variables")
        return {
            "status": "error",
            "message": "PEXELS_KEY not found in environment variables",
        }

    results = {}
    success_count = 0

    try:
        # Test with multiple keywords
        for keyword in TEST_VIDEO_KEYWORDS:
            logger.info(f"Fetching video from Pexels for keyword: {keyword}")
            video_url = fetch_pexels(keyword)

            if video_url:
                logger.info(
                    f"Successfully fetched video from Pexels for keyword: {keyword}"
                )
                results[keyword] = {"status": "success", "url": video_url}
                success_count += 1
            else:
                logger.warning(
                    f"No video found on Pexels for keyword: {keyword}"
                )
                results[keyword] = {
                    "status": "warning",
                    "message": "No video found",
                }

        # Overall status
        if success_count == 0:
            overall_status = "error"
            message = "Failed to fetch any videos from Pexels"
        elif success_count < len(TEST_VIDEO_KEYWORDS):
            overall_status = "partial_success"
            # Corrected multi-line f-string
            message = (
                f"Successfully fetched {success_count} out of "
                f"{len(TEST_VIDEO_KEYWORDS)} videos from Pexels"
            )
        else:
            overall_status = "success"
            # Corrected multi-line f-string
            message = (
                f"Successfully fetched all {len(TEST_VIDEO_KEYWORDS)} "
                f"videos from Pexels"
            )

        return {
            "status": overall_status,
            "message": message,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error testing Pexels API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error testing Pexels API: {str(e)}",
            "results": results,
        }


def run_all_tests():
    """Run all API integration tests.

    Returns:
        dict: Combined test results
    """
    logger.info("Starting API integration tests...")

    # Run tests
    suno_results = test_suno_api()
    pixabay_results = test_pixabay_api()
    pexels_results = test_pexels_api()

    # Combine results
    all_results = {
        "suno": suno_results,
        "pixabay": pixabay_results,
        "pexels": pexels_results,
    }

    # Determine overall status
    success_count = sum(
        1
        for api, result in all_results.items()
        if result["status"] == "success"
    )
    partial_success_count = sum(
        1
        for api, result in all_results.items()
        if result["status"] == "partial_success"
    )

    if success_count + partial_success_count == 0:
        overall_status = "error"
        message = "All API tests failed"
    elif success_count == len(all_results):
        overall_status = "success"
        message = "All API tests passed successfully"
    else:
        overall_status = "partial_success"
        message = (
            f"{success_count} API tests passed successfully, "
            f"{partial_success_count} partially succeeded, "
            f"{len(all_results) - success_count - partial_success_count} failed"
        )

    # Save results to file
    results_file = Path("logs/api_test_results.json")
    with open(results_file, "w") as f:
        json.dump(
            {
                "status": overall_status,
                "message": message,
                "results": all_results,
            },
            f,
            indent=2,
        )

    logger.info(f"API test results saved to {results_file}")

    return {
        "status": overall_status,
        "message": message,
        "results": all_results,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test API integrations")
    parser.add_argument(
        "--api",
        choices=["suno", "pixabay", "pexels", "all"],
        default="all",
        help="Which API to test (default: all)",
    )

    args = parser.parse_args()

    if args.api == "suno":
        result = test_suno_api()
    elif args.api == "pixabay":
        result = test_pixabay_api()
    elif args.api == "pexels":
        result = test_pexels_api()
    else:  # all
        result = run_all_tests()

    # Print results
    print("\n" + "=" * 50)
    print(f"API TEST RESULTS: {result['status'].upper()}")
    print("=" * 50)
    print(f"Message: {result['message']}")
    print("=" * 50 + "\n")

    # Print detailed results
    print(json.dumps(result, indent=2))
