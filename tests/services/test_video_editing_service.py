# /home/ubuntu/ai_artist_system_clone/tests/services/test_video_editing_service.py
"""Unit tests for the Video Editing Service."""

import pytest
import os
import sys
import shutil
import logging  # Added logging

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.append(PROJECT_ROOT)

logger = logging.getLogger(__name__)  # Added logger

# --- Check for MoviePy and FFmpeg availability ---
MOVIEPY_AVAILABLE = False
FFMPEG_AVAILABLE = False
SKIP_REASON = "moviepy library not found."

try:
    from moviepy.config import get_setting, change_settings

    MOVIEPY_AVAILABLE = True
    logger.info("MoviePy library found.")

    # Check for ffmpeg
    try:
        ffmpeg_binary = get_setting("FFMPEG_BINARY")
        if ffmpeg_binary == "ffmpeg-imageio" or not shutil.which(
            ffmpeg_binary
        ):
            logger.warning(
                "MoviePy default ffmpeg not found, searching PATH..."
            )
            ffmpeg_path_in_path = shutil.which("ffmpeg")
            if ffmpeg_path_in_path:
                logger.info(f"Found ffmpeg in PATH: {ffmpeg_path_in_path}")
                try:
                    # Attempt to explicitly set the path for MoviePy
                    change_settings({"FFMPEG_BINARY": ffmpeg_path_in_path})
                    FFMPEG_AVAILABLE = True
                    logger.info("Successfully set ffmpeg path for MoviePy.")
                except Exception as e_cfg:
                    logger.warning(
                        f"Failed to set ffmpeg path in MoviePy config: {e_cfg}"
                    )
                    # Proceed, hoping MoviePy finds it anyway
                    FFMPEG_AVAILABLE = (
                        True  # Assume available if found in PATH
                    )
            else:
                SKIP_REASON = (
                    "ffmpeg binary not found in PATH or MoviePy config."
                )
                logger.error(SKIP_REASON)
        else:
            FFMPEG_AVAILABLE = True
            logger.info(
                f"ffmpeg binary configured in MoviePy: {ffmpeg_binary}"
            )
    except Exception as e_ffmpeg:
        SKIP_REASON = f"Error checking ffmpeg availability: {e_ffmpeg}"
        logger.error(SKIP_REASON)

except ImportError:
    SKIP_REASON = "moviepy library not found."
    logger.error(SKIP_REASON)

# --- Conditional Import --- #
if MOVIEPY_AVAILABLE and FFMPEG_AVAILABLE:
    try:
        # Ensure the service path is correct relative to the project root
        from services.video_editing_service import (
            add_text_overlay,  # Import the function directly
            VideoEditingError,
        )
    except ImportError as e_import:
        MOVIEPY_AVAILABLE = False  # Treat as unavailable if import fails
        FFMPEG_AVAILABLE = False
        SKIP_REASON = f"Failed to import video_editing_service: {e_import}"
        logger.error(SKIP_REASON)
else:
    # Define dummy classes/functions if imports fail, so tests can be parsed
    class VideoEditingError(Exception):
        pass

    def add_text_overlay(*args, **kwargs):
        raise NotImplementedError("Video service not available")


# --- Test Setup and Fixtures ---

# Define paths relative to the test file
TEST_ASSETS_DIR = os.path.join(PROJECT_ROOT, "tests", "assets")
DUMMY_VIDEO_INPUT = os.path.join(TEST_ASSETS_DIR, "dummy_video.mp4")
TEST_OUTPUT_DIR = os.path.join(
    PROJECT_ROOT, "tests", "output", "video_editing"
)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Create necessary directories before tests and clean up after."""
    # Create dummy input video if it doesn't exist
    os.makedirs(TEST_ASSETS_DIR, exist_ok=True)
    if not os.path.exists(DUMMY_VIDEO_INPUT):
        if not FFMPEG_AVAILABLE:
            pytest.skip(
                f"Skipping video tests: Cannot create dummy video, {SKIP_REASON}",
                allow_module_level=True,
            )
        logger.warning(
            f"Dummy input video not found at {DUMMY_VIDEO_INPUT}. Creating..."
        )
        try:
            # Use ffmpeg command to create a short black video with text
            cmd = (
                f"ffmpeg -y -f lavfi -i color=c=black:s=640x360:d=5 "
                f"-vf \"drawtext=text=\\'Dummy Video\\':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=(h-text_h)/2\" "
                f"{DUMMY_VIDEO_INPUT}"
            )
            logger.info(f"Running command: {cmd}")
            result_code = os.system(cmd)
            if result_code != 0 or not os.path.exists(DUMMY_VIDEO_INPUT):
                raise OSError(f"ffmpeg command failed with code {result_code}")
            logger.info("Dummy input video created successfully.")
        except Exception as e:
            pytest.skip(
                f"Skipping video tests: Failed to create dummy input video: {e}",
                allow_module_level=True,
            )

    # Create output directory
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    logger.info(f"Ensured test output directory exists: {TEST_OUTPUT_DIR}")

    yield

    # Clean up output directory after tests run (optional)
    # logger.info(f"Cleaning up test output directory: {TEST_OUTPUT_DIR}")
    # try:
    #     shutil.rmtree(TEST_OUTPUT_DIR)
    # except OSError as e:
    #     logger.error(f"Error cleaning up test output directory {TEST_OUTPUT_DIR}: {e}")
    logger.info("Test environment teardown complete (cleanup skipped).")


# --- Test Cases ---

# Use a single skipif decorator based on the final availability status
pytestmark = pytest.mark.skipif(
    not (MOVIEPY_AVAILABLE and FFMPEG_AVAILABLE),
    reason=f"Skipping video editing tests: {SKIP_REASON}",
)


def test_add_text_overlay_success():
    """Test adding a simple text overlay successfully."""
    output_path = os.path.join(TEST_OUTPUT_DIR, "output_success.mp4")
    text = "Test Overlay Success"

    result_path = add_text_overlay(
        input_video_path=DUMMY_VIDEO_INPUT,
        output_video_path=output_path,
        text=text,
        position=("center", "bottom"),
        fontsize=24,
        color="white",
        duration=3,  # Process only first 3 seconds for speed
    )

    assert result_path == output_path
    assert os.path.exists(output_path)
    # Basic check: output file size should be > 0
    assert os.path.getsize(output_path) > 1000  # Expect at least 1KB
    logger.info(
        f"Test 'test_add_text_overlay_success' passed. Output: {output_path}"
    )


def test_add_text_overlay_different_position():
    """Test adding text overlay at a different position."""
    output_path = os.path.join(TEST_OUTPUT_DIR, "output_top_left.mp4")
    text = "Top Left Text"

    result_path = add_text_overlay(
        input_video_path=DUMMY_VIDEO_INPUT,
        output_video_path=output_path,
        text=text,
        position=("left", "top"),
        fontsize=18,
        color="yellow",
        duration=2,
    )

    assert result_path == output_path
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 1000
    logger.info(
        f"Test 'test_add_text_overlay_different_position' passed. Output: {output_path}"
    )


def test_add_text_overlay_invalid_input_path():
    """Test error handling for a non-existent input video path."""
    output_path = os.path.join(TEST_OUTPUT_DIR, "output_invalid_input.mp4")
    # Expecting FileNotFoundError directly from the service function's check
    with pytest.raises(FileNotFoundError, match="Input video not found"):
        add_text_overlay(
            input_video_path="/path/to/nonexistent/video.mp4",
            output_video_path=output_path,
            text="Error Test",
        )
    assert not os.path.exists(output_path)
    logger.info("Test 'test_add_text_overlay_invalid_input_path' passed.")


def test_add_text_overlay_invalid_output_dir():
    """Test error handling for an invalid output directory.
    MoviePy might raise various errors (OSError, ffmpeg errors).
    """
    output_path = "/invalid/directory/structure/output_error.mp4"
    # Expecting an Exception because the exact error from MoviePy/ffmpeg can vary
    with pytest.raises(Exception) as excinfo:
        add_text_overlay(
            input_video_path=DUMMY_VIDEO_INPUT,
            output_video_path=output_path,
            text="Error Test Invalid Output",
            duration=1,  # Keep it short
        )
    # Check that the error is not the specific FileNotFoundError for input
    assert not isinstance(excinfo.value, FileNotFoundError)
    logger.info(
        f"Test 'test_add_text_overlay_invalid_output_dir' passed (Caught expected exception: {excinfo.type.__name__})."
    )
    assert not os.path.exists(output_path)


# Potential future tests:
# - Test with different fonts (if font selection is added)
# - Test with very long text
# - Test specific error conditions from moviepy (might require mocking internal calls)
# - Test performance on longer videos (might need specific markers or timeouts)
