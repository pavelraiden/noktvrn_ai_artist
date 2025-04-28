"""
Test script for the Artist Full Creation Flow.

This script tests the complete artist creation flow by creating a test artist
and verifying all outputs are generated correctly.
"""

import os
import json
import logging
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the artist_creator package
sys.path.append(str(Path(__file__).resolve().parents[1]))

from artist_creator.artist_creation_flow import run_full_artist_creation_flow

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_artist_creation_flow")

def test_artist_creation():
    """
    Test the full artist creation flow with a test artist.
    
    Verifies that all expected files are created and contain valid content.
    """
    logger.info("Starting test of artist creation flow")
    
    # Create a test artist
    result = run_full_artist_creation_flow(
        artist_name="Echo Pulse",
        main_genre="Electronic",
        subgenres=["Synthwave", "Chillwave"],
        style_tags=["retro", "nostalgic", "dreamy"],
        vibe_description="Nostalgic electronic soundscapes with retro synth elements and modern production",
        target_audience="Electronic music fans who appreciate both retro and modern sounds"
    )
    
    # Verify the results
    artist_slug = result['artist_profile']['slug']
    base_dir = Path(__file__).resolve().parents[1] / "artists"
    
    # Check that all expected files exist
    expected_files = [
        base_dir / artist_slug / "profile.json",
        base_dir / artist_slug / "prompts" / "song_prompt.txt",
        base_dir / artist_slug / "prompts" / "video_prompt.txt",
        base_dir / artist_slug / "prompts" / "social_prompt.txt",
        base_dir / artist_slug / "lyrics" / f"{result['lyrics']['song_slug']}.txt"
    ]
    
    all_files_exist = True
    for file_path in expected_files:
        if not file_path.exists():
            logger.error(f"Missing expected file: {file_path}")
            all_files_exist = False
        else:
            logger.info(f"Verified file exists: {file_path}")
            
            # Check file content
            with open(file_path, 'r') as f:
                content = f.read()
                if len(content) > 0:
                    logger.info(f"File has content: {file_path}")
                else:
                    logger.error(f"File is empty: {file_path}")
                    all_files_exist = False
    
    # Final verification
    if all_files_exist:
        logger.info("✅ All tests passed! Artist creation flow is working correctly.")
        return True
    else:
        logger.error("❌ Test failed! Some expected files are missing or empty.")
        return False

if __name__ == "__main__":
    success = test_artist_creation()
    
    if success:
        print("\n✅ Artist creation flow test completed successfully!")
        print("All expected files were created with valid content.")
    else:
        print("\n❌ Artist creation flow test failed!")
        print("Some expected files are missing or empty.")
