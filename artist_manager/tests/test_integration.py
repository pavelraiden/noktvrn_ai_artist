"""
Integration test for the Artist Manager module.

This script demonstrates how the Artist Manager module integrates with
the existing system components, particularly the artist_flow module.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artist_manager import Artist, ArtistInitializer, ArtistUpdater


def test_integration_with_artist_flow():
    """
    Test integration with the artist_flow module.
    
    This function demonstrates how the Artist Manager module can be used
    to create and manage artist profiles that are compatible with the
    existing artist_flow module.
    """
    print("Testing integration with artist_flow module...")
    
    # Step 1: Create a new artist profile
    print("\nStep 1: Creating a new artist profile")
    initializer = ArtistInitializer()
    
    # Create artist with parameters that would be used in artist_flow
    artist_parameters = {
        "stage_name": "Neon Horizon",
        "genre": "Electronic",
        "subgenres": ["Synthwave", "Chillwave"],
        "style_description": "A unique electronic sound with retro influences and futuristic elements",
        "voice_type": "Ethereal vocals with digital effects and atmospheric textures",
        "personality_traits": ["Mysterious", "Innovative", "Futuristic"],
        "target_audience": "Electronic music fans who appreciate atmospheric sounds and nostalgic elements",
        "visual_identity_prompt": "Neon cityscape with retro-futuristic elements, purple and blue color scheme"
    }
    
    artist, warnings = initializer.initialize_artist(artist_parameters)
    
    if warnings:
        print(f"Warnings during initialization: {warnings}")
    
    # Step 2: Validate the artist profile
    print("\nStep 2: Validating the artist profile")
    is_valid, errors = artist.validate()
    
    if is_valid:
        print("Artist profile is valid")
    else:
        print(f"Validation errors: {errors}")
        return
    
    # Step 3: Save the artist profile to a file
    print("\nStep 3: Saving the artist profile")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = os.path.join(output_dir, f"{artist.profile['artist_id']}.json")
    yaml_path = os.path.join(output_dir, f"{artist.profile['artist_id']}.yaml")
    
    artist.save(json_path, "json")
    artist.save(yaml_path, "yaml")
    
    print(f"Saved artist profile to {json_path} and {yaml_path}")
    
    # Step 4: Simulate integration with artist_flow
    print("\nStep 4: Simulating integration with artist_flow")
    
    # Convert to format expected by artist_flow
    artist_flow_format = {
        "name": artist.profile["stage_name"],
        "genre": artist.profile["genre"],
        "style": ", ".join(artist.profile["subgenres"]),
        "background": artist.profile.get("backstory", ""),
        "created_at": datetime.now().isoformat(),
        "artist_id": artist.profile["artist_id"],
        "voice_type": artist.profile["voice_type"],
        "personality": ", ".join(artist.profile["personality_traits"]),
        "target_audience": artist.profile["target_audience"],
        "visual_prompt": artist.profile["visual_identity_prompt"],
        "release_frequency": artist.profile["settings"]["release_strategy"]["track_release_random_days"]
    }
    
    # Save in artist_flow format
    artist_flow_path = os.path.join(output_dir, f"artist_flow_{artist.profile['artist_id']}.json")
    with open(artist_flow_path, 'w') as f:
        json.dump(artist_flow_format, f, indent=2)
    
    print(f"Saved artist profile in artist_flow format to {artist_flow_path}")
    
    # Step 5: Apply trend-based updates
    print("\nStep 5: Applying trend-based updates")
    updater = ArtistUpdater()
    
    # Simulate trend data from trend analyzer
    trend_data = {
        "genre_trends": {
            "Vaporwave": 0.85,
            "Lofi": 0.65,
            "Ambient": 0.45
        },
        "personality_trends": {
            "Nostalgic": 0.9,
            "Dreamy": 0.7
        },
        "visual_trends": {
            "Cyberpunk": 0.8,
            "Retro Gaming": 0.6
        },
        "release_trends": {
            "frequency": 0.85,
            "video_ratio": 0.7
        }
    }
    
    success, applied_updates, warnings = updater.apply_trend_updates(artist, trend_data)
    
    if success:
        print(f"Successfully applied {len(applied_updates)} trend-based updates:")
        for update in applied_updates:
            print(f"  - {update}")
        
        if warnings:
            print(f"Warnings during update: {warnings}")
    else:
        print("Failed to apply trend-based updates")
        return
    
    # Step 6: Save the updated profile
    print("\nStep 6: Saving the updated profile")
    updated_json_path = os.path.join(output_dir, f"{artist.profile['artist_id']}_updated.json")
    artist.save(updated_json_path, "json")
    
    print(f"Saved updated artist profile to {updated_json_path}")
    
    # Step 7: Verify backward compatibility
    print("\nStep 7: Verifying backward compatibility")
    
    # Load the original profile
    original_artist = Artist.load(json_path)
    
    # Load the updated profile
    updated_artist = Artist.load(updated_json_path)
    
    # Compare key fields
    print(f"Original stage name: {original_artist.profile['stage_name']}")
    print(f"Updated stage name: {updated_artist.profile['stage_name']}")
    
    print(f"Original genre: {original_artist.profile['genre']}")
    print(f"Updated genre: {updated_artist.profile['genre']}")
    
    print(f"Original subgenres: {original_artist.profile['subgenres']}")
    print(f"Updated subgenres: {updated_artist.profile['subgenres']}")
    
    # Check update history
    print(f"\nUpdate history entries: {len(updated_artist.profile['update_history'])}")
    
    print("\nIntegration test completed successfully!")


if __name__ == "__main__":
    test_integration_with_artist_flow()
