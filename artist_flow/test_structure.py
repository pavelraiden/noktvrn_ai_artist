"""
Test script to verify the structure integrity of the Artist Full Creation Flow.

This script imports all modules and performs basic functionality tests
to ensure the structure is properly set up.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("structure_test")

# Import all modules to verify they can be imported
try:
    from artist_flow.artist_creator import ArtistCreator, create_new_artist
    from artist_flow.prompt_generators import (
        MusicPromptGenerator, 
        VisualPromptGenerator, 
        BackstoryPromptGenerator,
        get_prompt_generator
    )
    from artist_flow.mocks.music_generator import MockMusicGenerator, create_music_generator
    from artist_flow.mocks.image_generator import MockImageGenerator, create_image_generator
    from artist_flow.asset_manager import AssetManager, create_asset_manager
    
    logger.info("All modules imported successfully")
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    sys.exit(1)

def test_module_instantiation():
    """Test that all modules can be instantiated."""
    try:
        # Create instances of all classes
        artist_creator = ArtistCreator()
        music_prompt_gen = MusicPromptGenerator()
        visual_prompt_gen = VisualPromptGenerator()
        backstory_prompt_gen = BackstoryPromptGenerator()
        music_gen = MockMusicGenerator()
        image_gen = MockImageGenerator()
        asset_mgr = AssetManager()
        
        logger.info("All modules instantiated successfully")
        return True
    except Exception as e:
        logger.error(f"Instantiation error: {str(e)}")
        return False

def test_factory_functions():
    """Test that all factory functions work."""
    try:
        # Test factory functions
        prompt_gen = get_prompt_generator("music")
        music_gen = create_music_generator(mock=True)
        image_gen = create_image_generator(mock=True)
        asset_mgr = create_asset_manager()
        
        logger.info("All factory functions work correctly")
        return True
    except Exception as e:
        logger.error(f"Factory function error: {str(e)}")
        return False

def test_basic_functionality():
    """Test basic functionality of the modules."""
    try:
        # Create test artist profile
        test_profile = {
            "name": "TestArtist",
            "genre": "Test Genre",
            "style": "Test Style"
        }
        
        # Test prompt generation
        music_prompt_gen = MusicPromptGenerator()
        track_prompt = music_prompt_gen.generate_track_prompt(test_profile)
        
        # Test mock music generation
        music_gen = create_music_generator()
        track = music_gen.generate_track(track_prompt, test_profile, "test_session")
        
        # Test mock image generation
        visual_prompt_gen = VisualPromptGenerator()
        image_prompt = visual_prompt_gen.generate_profile_image_prompt(test_profile)
        
        image_gen = create_image_generator()
        image = image_gen.generate_image(image_prompt, test_profile, "test_session")
        
        # Test asset management
        asset_mgr = create_asset_manager()
        saved_profile = asset_mgr.save_artist_profile(test_profile, "test_session")
        
        logger.info("Basic functionality tests passed")
        return True
    except Exception as e:
        logger.error(f"Functionality error: {str(e)}")
        return False

def run_all_tests():
    """Run all structure integrity tests."""
    logger.info("Starting structure integrity tests")
    
    # Run tests
    import_success = True  # We've already imported modules
    instantiation_success = test_module_instantiation()
    factory_success = test_factory_functions()
    functionality_success = test_basic_functionality()
    
    # Report results
    logger.info("Structure integrity test results:")
    logger.info(f"- Import test: {'PASSED' if import_success else 'FAILED'}")
    logger.info(f"- Instantiation test: {'PASSED' if instantiation_success else 'FAILED'}")
    logger.info(f"- Factory function test: {'PASSED' if factory_success else 'FAILED'}")
    logger.info(f"- Basic functionality test: {'PASSED' if functionality_success else 'FAILED'}")
    
    all_passed = import_success and instantiation_success and factory_success and functionality_success
    logger.info(f"Overall result: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
