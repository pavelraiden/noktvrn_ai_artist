# /home/ubuntu/ai_artist_system_clone/services/video_editing_service.py

import logging
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# Configure logging
logger = logging.getLogger(__name__)

# Explicitly tell MoviePy where to find ImageMagick's convert binary if needed
# This might be necessary in some environments if auto-detection fails.
# Check if IMAGEMAGICK_BINARY environment variable is set, otherwise try common paths.
imagemagick_path = os.getenv("IMAGEMAGICK_BINARY", "/usr/bin/convert")
if os.path.exists(imagemagick_path):
    try:
        change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
        logger.info(f"Set ImageMagick binary path to: {imagemagick_path}")
    except Exception as e:
        logger.warning(f"Failed to set ImageMagick path: {e}. Text rendering might fail if not found.")
else:
    logger.warning(f"ImageMagick binary not found at {imagemagick_path}. Text rendering might fail.")

class VideoEditingError(Exception):
    """Custom exception for video editing errors."""
    pass

def add_text_overlay(
    input_video_path: str,
    output_video_path: str,
    text: str,
    fontsize: int = 24,
    color: str = 'white',
    font: str = 'DejaVu-Sans', # Use a commonly available font
    position: tuple = ('center', 'bottom'), # e.g., ('center', 'bottom'), (10, 10), ('left', 50)
    start_time: float = 0,
    duration: float | None = None,
    margin: int = 10, # Margin from edge if position is like ('center', 'bottom')
    bg_color: str | None = None, # Optional background color for text
    stroke_color: str | None = None, # Optional stroke color
    stroke_width: int = 1
) -> str:
    """
    Adds a text overlay to a video using MoviePy.

    Args:
        input_video_path: Path to the input video file.
        output_video_path: Path to save the output video file.
        text: The text content to overlay.
        fontsize: Font size of the text.
        color: Color of the text (MoviePy/ImageMagick color name or hex).
        font: Name of the font to use (must be available to ImageMagick/MoviePy).
        position: Position of the text. Can be tuple like ('center', 'bottom'),
                  ('left', 'top'), ('right', 'center'), or coordinates (x, y)
                  from top-left corner.
        start_time: Time in seconds when the text should appear.
        duration: Duration in seconds the text should be visible. If None, stays till end.
        margin: Margin in pixels from the edge when using relative positions.
        bg_color: Optional background color for the text clip.
        stroke_color: Optional color for the text stroke/outline.
        stroke_width: Width of the text stroke.

    Returns:
        The path to the output video file.

    Raises:
        VideoEditingError: If any error occurs during the process.
        FileNotFoundError: If the input video file does not exist.
    """
    logger.info(f"Starting text overlay process for {input_video_path}")

    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video not found: {input_video_path}")

    try:
        # Load the main video clip
        video_clip = VideoFileClip(input_video_path)
        logger.debug(f"Video clip loaded: Duration={video_clip.duration}s, Size={video_clip.size}")

        # Determine text duration
        if duration is None:
            text_duration = video_clip.duration - start_time
        else:
            text_duration = duration
        # Ensure duration doesn't exceed video length
        text_duration = max(0, min(text_duration, video_clip.duration - start_time))

        if text_duration <= 0:
             logger.warning("Calculated text duration is zero or negative. Skipping overlay.")
             # Optionally copy the original video if no overlay is added
             # For now, we'll just return the original path or handle error
             # Copying might be safer:
             # import shutil
             # shutil.copy2(input_video_path, output_video_path)
             # return output_video_path
             raise VideoEditingError("Text duration is zero or negative.")


        # Create the text clip
        # Note: MoviePy's TextClip relies on ImageMagick. Ensure it's installed.
        txt_clip = TextClip(
            txt=text,
            fontsize=fontsize,
            color=color,
            font=font,
            bg_color=bg_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            size=video_clip.size # Important for positioning
        )

        # Set the position of the text clip
        # Handle string-based positions with margin
        pos_x, pos_y = position
        if isinstance(pos_x, str):
            if pos_x == 'left':
                final_pos_x = margin
            elif pos_x == 'center':
                final_pos_x = (video_clip.w - txt_clip.w) / 2
            elif pos_x == 'right':
                final_pos_x = video_clip.w - txt_clip.w - margin
            else:
                final_pos_x = pos_x # Assume it's a numeric value passed as string?
        else: # Assume numeric
             final_pos_x = pos_x

        if isinstance(pos_y, str):
            if pos_y == 'top':
                final_pos_y = margin
            elif pos_y == 'center':
                final_pos_y = (video_clip.h - txt_clip.h) / 2
            elif pos_y == 'bottom':
                final_pos_y = video_clip.h - txt_clip.h - margin
            else:
                final_pos_y = pos_y
        else: # Assume numeric
            final_pos_y = pos_y

        txt_clip = txt_clip.set_position((final_pos_x, final_pos_y))
        txt_clip = txt_clip.set_start(start_time)
        txt_clip = txt_clip.set_duration(text_duration)

        logger.debug(f"Text clip created: Duration={txt_clip.duration}s, Position=({final_pos_x}, {final_pos_y})")

        # Composite the text clip over the video clip
        video_with_overlay = CompositeVideoClip([video_clip, txt_clip])

        # Write the result to a file
        logger.info(f"Writing output video to: {output_video_path}")
        # Use appropriate codec, bitrate etc. Consider making these configurable.
        # Default libx264 codec is generally good. Specify audio codec if needed.
        video_with_overlay.write_videofile(
            output_video_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a', # Recommended by MoviePy docs
            remove_temp=True,
            threads=4, # Use multiple threads for faster encoding
            logger='bar' # Show progress bar
        )

        # Close clips to release resources
        txt_clip.close()
        video_clip.close()
        video_with_overlay.close()

        logger.info("Video editing completed successfully.")
        return output_video_path

    except FileNotFoundError as e: # Catch specific error
        logger.error(f"Video editing failed: {e}")
        raise e # Re-raise FileNotFoundError
    except Exception as e:
        logger.error(f"Video editing failed: {e}", exc_info=True)
        # Clean up clips if they exist
        if 'video_clip' in locals() and video_clip: video_clip.close()
        if 'txt_clip' in locals() and txt_clip: txt_clip.close()
        if 'video_with_overlay' in locals() and video_with_overlay: video_with_overlay.close()
        raise VideoEditingError(f"Failed to add text overlay: {e}")

# --- Example Usage (for testing) --- #
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Create dummy directories if they don't exist
    input_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_videos')
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'edited_videos')
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Define input and output paths (using the placeholder created earlier)
    test_input_video = os.path.join(input_dir, 'placeholder_video.mp4')
    test_output_video = os.path.join(output_dir, 'placeholder_video_with_overlay.mp4')

    # Check if placeholder exists, create if not (redundant if previous step worked)
    if not os.path.exists(test_input_video):
        logger.warning(f"Placeholder video not found at {test_input_video}. Attempting to create.")
        try:
            os.system(f"ffmpeg -y -f lavfi -i color=c=black:s=1280x720:d=5 -vf \"drawtext=text='Placeholder Video':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=(h-text_h)/2\" {test_input_video}")
            logger.info("Placeholder video created.")
        except Exception as e:
            logger.error(f"Failed to create placeholder video: {e}. Cannot run test.")
            sys.exit(1)

    # --- Test Case 1: Simple Centered Text --- #
    try:
        logger.info("--- Running Test Case 1: Simple Centered Text ---")
        output_path = add_text_overlay(
            input_video_path=test_input_video,
            output_video_path=test_output_video.replace('.mp4', '_test1.mp4'),
            text="AI Artist: Synthwave Dreamer",
            fontsize=40,
            color='cyan',
            position=('center', 'bottom'),
            margin=20,
            start_time=0.5,
            duration=4.0
        )
        logger.info(f"Test Case 1 successful. Output: {output_path}")
    except (VideoEditingError, FileNotFoundError) as e:
        logger.error(f"Test Case 1 failed: {e}")

    # --- Test Case 2: Top-Left Text with Background --- #
    try:
        logger.info("--- Running Test Case 2: Top-Left Text with Background ---")
        output_path = add_text_overlay(
            input_video_path=test_input_video,
            output_video_path=test_output_video.replace('.mp4', '_test2.mp4'),
            text="Track: Midnight Drive",
            fontsize=30,
            color='yellow',
            font='DejaVu-Sans-Bold', # Example of different font weight
            position=('left', 'top'),
            margin=15,
            start_time=0,
            duration=None, # Stays till end
            bg_color='rgba(0, 0, 0, 0.5)', # Semi-transparent black background
            stroke_color='black',
            stroke_width=1
        )
        logger.info(f"Test Case 2 successful. Output: {output_path}")
    except (VideoEditingError, FileNotFoundError) as e:
        logger.error(f"Test Case 2 failed: {e}")

    # --- Test Case 3: Specific Coordinates --- #
    try:
        logger.info("--- Running Test Case 3: Specific Coordinates ---")
        output_path = add_text_overlay(
            input_video_path=test_input_video,
            output_video_path=test_output_video.replace('.mp4', '_test3.mp4'),
            text="v1.1",
            fontsize=18,
            color='grey',
            position=(1180, 680), # Bottom right corner (approx for 1280x720)
            start_time=0,
            duration=None
        )
        logger.info(f"Test Case 3 successful. Output: {output_path}")
    except (VideoEditingError, FileNotFoundError) as e:
        logger.error(f"Test Case 3 failed: {e}")

    logger.info("Video editing service tests finished.")

