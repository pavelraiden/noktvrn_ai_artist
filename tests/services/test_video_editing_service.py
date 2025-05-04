# /home/ubuntu/ai_artist_system_clone/tests/services/test_video_editing_service.py
"""Unit tests for the Video Editing Service."""

import pytest
import os
import sys
import shutil

# Add project root to sys.path to allow importing services
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

# Check if moviepy and its dependencies (like ffmpeg) are likely available
try:
    import moviepy.editor

    # Attempt a basic ffmpeg command check via moviepy's config
    from moviepy.config import get_setting

    FFMPEG_BINARY = get_setting("FFMPEG_BINARY")
    if FFMPEG_BINARY == "ffmpeg-imageio":  # Default if auto-detect fails
        # Try finding ffmpeg in PATH
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            MOVIEPY_AVAILABLE = False
            pytest.skip(
                "Skipping video editing tests: ffmpeg binary not found.",
                allow_module_level=True,
            )
        else:
            MOVIEPY_AVAILABLE = True
    else:
        MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    pytest.skip(
        "Skipping video editing tests: moviepy library not found.",
        allow_module_level=True,
    )
except Exception:  # Catch potential errors during ffmpeg check
    MOVIEPY_AVAILABLE = False
    pytest.skip(
        "Skipping video editing tests: Error checking ffmpeg availability.",
        allow_module_level=True,
    )

# Import the service only if moviepy seems available
if MOVIEPY_AVAILABLE:
    from services.video_editing_service import VideoEditingService, VideoEditingError

# --- Test Setup and Fixtures ---

# Define paths relative to the test file
TEST_ASSETS_DIR = os.path.join(PROJECT_ROOT, "tests", "assets")
DUMMY_VIDEO_INPUT = os.path.join(TEST_ASSETS_DIR, "dummy_video.mp4")
TEST_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "output", "video_editing")


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Create necessary directories before tests and clean up after."""
    # Ensure dummy input video exists (it was created in a previous step)
    if not os.path.exists(DUMMY_VIDEO_INPUT):
        pytest.skip(
            f"Skipping video editing tests: Dummy input video not found at {DUMMY_VIDEO_INPUT}",
            allow_module_level=True,
        )

    # Create output directory
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    yield
    # Clean up output directory after tests run
    # Comment out the cleanup if you want to inspect the output files
    # try:
    #     shutil.rmtree(TEST_OUTPUT_DIR)
    # except OSError as e:
    #     print(f"Error cleaning up test output directory {TEST_OUTPUT_DIR}: {e}")
    pass  # Keep output for inspection for now


@pytest.fixture
def video_service():
    """Provides an instance of the VideoEditingService."""
    if not MOVIEPY_AVAILABLE:
        pytest.skip("Moviepy not available")
    return VideoEditingService()


# --- Test Cases ---


@pytest.mark.skipif(not MOVIEPY_AVAILABLE, reason="moviepy or ffmpeg not available")
def test_add_text_overlay_success(video_service):
    """Test adding a simple text overlay successfully."""
    output_path = os.path.join(TEST_OUTPUT_DIR, "output_success.mp4")
    text = "Test Overlay"

    result_path = video_service.add_text_overlay(
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
    assert os.path.getsize(output_path) > 0
    # More advanced checks could involve ffprobe or frame analysis, but are complex


@pytest.mark.skipif(not MOVIEPY_AVAILABLE, reason="moviepy or ffmpeg not available")
def test_add_text_overlay_different_position(video_service):
    """Test adding text overlay at a different position."""
    output_path = os.path.join(TEST_OUTPUT_DIR, "output_top_left.mp4")
    text = "Top Left Text"

    result_path = video_service.add_text_overlay(
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
    assert os.path.getsize(output_path) > 0


@pytest.mark.skipif(not MOVIEPY_AVAILABLE, reason="moviepy or ffmpeg not available")
def test_add_text_overlay_invalid_input_path(video_service):
    """Test error handling for a non-existent input video path."""
    output_path = os.path.join(TEST_OUTPUT_DIR, "output_invalid_input.mp4")
    with pytest.raises(VideoEditingError, match="Input video file not found"):
        video_service.add_text_overlay(
            input_video_path="/path/to/nonexistent/video.mp4",
            output_video_path=output_path,
            text="Error Test",
        )
    assert not os.path.exists(output_path)


@pytest.mark.skipif(not MOVIEPY_AVAILABLE, reason="moviepy or ffmpeg not available")
def test_add_text_overlay_invalid_output_dir(video_service):
    """Test error handling for an invalid output directory."""
    output_path = "/invalid/directory/structure/output_error.mp4"
    # Expecting an OSError or similar from moviepy/os during write
    with pytest.raises(
        Exception
    ):  # Catch broader exception as moviepy might raise various things
        video_service.add_text_overlay(
            input_video_path=DUMMY_VIDEO_INPUT,
            output_video_path=output_path,
            text="Error Test",
            duration=1,  # Keep it short
        )
    assert not os.path.exists(output_path)


# Potential future tests:
# - Test with different fonts (if font selection is added)
# - Test with very long text
# - Test specific error conditions from moviepy (might require mocking)
# - Test performance on longer videos (might need specific markers or timeouts)
