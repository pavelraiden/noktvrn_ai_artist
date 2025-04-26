"""
Mock implementation of music generation capabilities.

This module provides a simulated music generation system that can be used
for testing the full artist creation flow before integrating with real
music generation APIs.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import os
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("music_generator")


class MockMusicGenerator:
    """
    Mock implementation of a music generation system.
    
    This class simulates the behavior of a real music generation system,
    providing the same interface but returning mock data instead of
    actually generating music.
    """
    
    def __init__(
        self,
        output_dir: str = "/tmp/artist_flow/music",
        generation_delay: float = 1.0  # Simulated generation time in seconds
    ):
        """
        Initialize the mock music generator.
        
        Args:
            output_dir: Directory where mock music files will be "saved"
            generation_delay: Simulated generation time in seconds
        """
        self.output_dir = output_dir
        self.generation_delay = generation_delay
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("Initialized MockMusicGenerator")
    
    def generate_track(
        self,
        prompt: Dict[str, Any],
        artist_profile: Dict[str, Any],
        session_id: str,
        track_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a mock music track based on the provided prompt.
        
        Args:
            prompt: The music generation prompt
            artist_profile: The artist profile
            session_id: Session ID for tracking
            track_name: Optional name for the track (generated if None)
            
        Returns:
            Dictionary containing the mock track information
        """
        logger.info(f"Generating mock track for session {session_id}")
        
        # Simulate generation time
        time.sleep(self.generation_delay)
        
        # Generate track name if not provided
        if not track_name:
            track_name = f"Track_{random.randint(1000, 9999)}"
        
        # Create a safe filename
        safe_name = "".join(c if c.isalnum() else "_" for c in track_name)
        
        # Create track directory
        track_dir = os.path.join(self.output_dir, session_id)
        os.makedirs(track_dir, exist_ok=True)
        
        # Mock file path
        file_path = os.path.join(track_dir, f"{safe_name}.mp3")
        
        # Create an empty file to simulate the track
        with open(file_path, "w") as f:
            f.write("This is a mock music file")
        
        # Generate random duration between 2 and 5 minutes
        duration_seconds = random.randint(120, 300)
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        duration_str = f"{minutes}:{seconds:02d}"
        
        # Return mock track information
        return {
            "track_id": f"{session_id}_{safe_name}",
            "title": track_name,
            "file_path": file_path,
            "duration": duration_str,
            "duration_seconds": duration_seconds,
            "format": "mp3",
            "genre": artist_profile.get("genre", "Unknown"),
            "created_at": datetime.now().isoformat(),
            "prompt_used": prompt.get("prompt", ""),
            "metadata": {
                "bpm": random.randint(80, 160),
                "key": random.choice(["C", "D", "E", "F", "G", "A", "B"]) + random.choice(["", "m"]),
                "is_mock": True
            }
        }
    
    def generate_album(
        self,
        album_concept: Dict[str, Any],
        artist_profile: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate a mock album based on the provided concept.
        
        Args:
            album_concept: The album concept including track prompts
            artist_profile: The artist profile
            session_id: Session ID for tracking
            
        Returns:
            Dictionary containing the mock album information
        """
        logger.info(f"Generating mock album for session {session_id}")
        
        # Create album directory
        album_dir = os.path.join(self.output_dir, session_id, "album")
        os.makedirs(album_dir, exist_ok=True)
        
        # Generate tracks
        tracks = []
        for i, track_info in enumerate(album_concept.get("tracks", [])):
            # Create track prompt
            track_prompt = {
                "prompt": track_info.get("prompt", ""),
                "parameters": {
                    "duration_seconds": track_info.get("duration_seconds", 180)
                }
            }
            
            # Generate the track
            track = self.generate_track(
                prompt=track_prompt,
                artist_profile=artist_profile,
                session_id=session_id,
                track_name=track_info.get("title", f"Track {i+1}")
            )
            
            tracks.append(track)
        
        # Return mock album information
        return {
            "album_id": f"{session_id}_album",
            "title": album_concept.get("album_title", "Untitled Album"),
            "artist": artist_profile.get("name", "Unknown Artist"),
            "tracks": tracks,
            "total_tracks": len(tracks),
            "total_duration_seconds": sum(t.get("duration_seconds", 0) for t in tracks),
            "created_at": datetime.now().isoformat(),
            "directory": album_dir,
            "metadata": {
                "concept": album_concept.get("concept", ""),
                "genre": artist_profile.get("genre", "Unknown"),
                "is_mock": True
            }
        }


# Factory function to create a music generator
def create_music_generator(
    output_dir: str = "/tmp/artist_flow/music",
    mock: bool = True
) -> Any:
    """
    Factory function to create a music generator.
    
    Args:
        output_dir: Directory where music files will be saved
        mock: Whether to use the mock implementation
        
    Returns:
        A music generator instance
    """
    if mock:
        return MockMusicGenerator(output_dir=output_dir)
    else:
        # In the future, this would return a real implementation
        logger.warning("Real music generator not implemented, using mock")
        return MockMusicGenerator(output_dir=output_dir)


# Example usage
if __name__ == "__main__":
    # Create a music generator
    generator = create_music_generator()
    
    # Example artist profile
    example_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold"
    }
    
    # Example prompt
    example_prompt = {
        "prompt": "Create a dark trap track with mysterious vibes",
        "parameters": {
            "genre": "Dark Trap",
            "style": "Mysterious, Cold",
            "duration_seconds": 180
        }
    }
    
    # Generate a track
    track = generator.generate_track(
        prompt=example_prompt,
        artist_profile=example_profile,
        session_id="test_session_123"
    )
    
    # Print the result
    import json
    print(json.dumps(track, indent=2))
