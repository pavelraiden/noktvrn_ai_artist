"""
Mock implementation of image/visual asset generation capabilities.

This module provides a simulated image generation system that can be used
for testing the full artist creation flow before integrating with real
image generation APIs.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import os
import time
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("image_generator")


def generate_mock_image(prompt: str) -> dict:
    """
    Generate a mock image based on a text prompt.

    Args:
        prompt: A text prompt (profile cover prompt or track cover prompt)

    Returns:
        Dictionary containing mock image information with the following structure:
        {
            "image_url": "https://mock-storage.com/images/artist-session-id-cover1.png",
            "style": "VHS Retro",
            "theme": "Dark Neon Nights"
        }
    """
    logger.info("Generating mock image from prompt")

    # Set random seed based on prompt for reproducibility
    seed = sum(ord(c) for c in prompt[:20])
    random.seed(seed)

    # Generate a random session ID and image number for the URL
    session_id = f"session-{random.randint(10000, 99999)}"
    image_num = random.randint(1, 10)

    # Base URL for mock storage
    base_url = "https://mock-storage.com/images"

    # Determine image type from prompt
    image_type = "cover"
    if "profile" in prompt.lower():
        image_type = "profile"
    elif "album" in prompt.lower():
        image_type = "album"
    elif "track" in prompt.lower():
        image_type = "track"

    # Generate image URL
    image_url = f"{base_url}/artist-{session_id}-{image_type}{image_num}.png"

    # Extract style from prompt
    style_patterns = [
        r"(retro|vintage|modern|futuristic|minimalist|abstract|realistic|surreal|cartoon|anime)",
        r"(vhs|film|digital|painted|drawn|photographic|glitch|neon|cyberpunk|vaporwave)",
    ]

    styles = []
    for pattern in style_patterns:
        matches = re.findall(pattern, prompt.lower())
        styles.extend(matches)

    # If no styles found in prompt, generate random ones
    if not styles:
        possible_styles = [
            "Retro",
            "Vintage",
            "Modern",
            "Futuristic",
            "Minimalist",
            "Abstract",
            "Realistic",
            "Surreal",
            "Cartoon",
            "VHS",
            "Film Noir",
            "Digital",
            "Painted",
            "Glitch",
            "Neon",
        ]
        styles = [random.choice(possible_styles)]

        # 50% chance to add a style modifier
        if random.random() > 0.5:
            style_modifiers = [
                "Dark",
                "Bright",
                "Grainy",
                "Smooth",
                "Distorted",
                "Clean",
            ]
            styles.insert(0, random.choice(style_modifiers))

    # Format style
    style_str = " ".join(s.capitalize() for s in styles[:2])

    # Extract theme from prompt
    theme_keywords = [
        "night",
        "day",
        "urban",
        "nature",
        "space",
        "ocean",
        "desert",
        "forest",
        "city",
        "street",
        "studio",
        "stage",
        "bedroom",
        "club",
        "underground",
        "neon",
        "dark",
        "light",
        "colorful",
        "monochrome",
        "dystopian",
        "utopian",
    ]

    themes = []
    for keyword in theme_keywords:
        if keyword in prompt.lower():
            themes.append(keyword)

    # If no themes found in prompt, generate random ones
    if not themes:
        possible_themes = [
            "Night Sky",
            "City Lights",
            "Urban Jungle",
            "Neon Streets",
            "Dark Alley",
            "Cosmic Void",
            "Desert Mirage",
            "Ocean Depths",
            "Mountain Peak",
            "Studio Portrait",
            "Stage Lights",
            "Underground Club",
        ]
        themes = [random.choice(possible_themes)]
    else:
        # Format existing themes into a coherent phrase
        if "night" in themes:
            if "city" in themes or "urban" in themes or "street" in themes:
                themes = ["Night City"]
            elif "neon" in themes:
                themes = ["Neon Nights"]
        elif "urban" in themes or "city" in themes:
            if "dark" in themes:
                themes = ["Dark City"]

        # If we couldn't create a compound theme, just use the first theme
        if len(themes) > 1:
            themes = [themes[0].capitalize()]

    # Format theme
    theme_str = themes[0].capitalize()
    if len(themes[0].split()) == 1:
        # Add a descriptor if the theme is just one word
        descriptors = [
            "Vibrant",
            "Moody",
            "Atmospheric",
            "Dramatic",
            "Serene",
            "Chaotic",
        ]
        theme_str = f"{random.choice(descriptors)} {theme_str}"

    # Return the mock image info
    return {"image_url": image_url, "style": style_str, "theme": theme_str}


class MockImageGenerator:
    """
    Mock implementation of an image generation system.

    This class simulates the behavior of a real image generation system,
    providing the same interface but returning mock data instead of
    actually generating images.
    """

    def __init__(
        self,
        output_dir: str = "/tmp/artist_flow/images",
        generation_delay: float = 1.5,  # Simulated generation time in seconds
    ):
        """
        Initialize the mock image generator.

        Args:
            output_dir: Directory where mock image files will be "saved"
            generation_delay: Simulated generation time in seconds
        """
        self.output_dir = output_dir
        self.generation_delay = generation_delay

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        logger.info("Initialized MockImageGenerator")

    def generate_image(
        self,
        prompt: Dict[str, Any],
        artist_profile: Dict[str, Any],
        session_id: str,
        image_type: str = "profile",
        image_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a mock image based on the provided prompt.

        Args:
            prompt: The image generation prompt
            artist_profile: The artist profile
            session_id: Session ID for tracking
            image_type: Type of image (profile, album_cover, etc.)
            image_name: Optional name for the image (generated if None)

        Returns:
            Dictionary containing the mock image information
        """
        logger.info(f"Generating mock {image_type} image for session {session_id}")

        # Simulate generation time
        time.sleep(self.generation_delay)

        # Generate image name if not provided
        if not image_name:
            image_name = f"{image_type}_{random.randint(1000, 9999)}"

        # Create a safe filename
        safe_name = "".join(c if c.isalnum() else "_" for c in image_name)

        # Create image directory
        image_dir = os.path.join(self.output_dir, session_id)
        os.makedirs(image_dir, exist_ok=True)

        # Mock file path
        file_path = os.path.join(image_dir, f"{safe_name}.png")

        # Create an empty file to simulate the image
        with open(file_path, "w") as f:
            f.write("This is a mock image file")

        # Generate random dimensions based on image type
        if image_type == "profile":
            width, height = 1024, 1024
        elif image_type == "album_cover":
            width, height = 1500, 1500
        elif image_type == "banner":
            width, height = 1920, 1080
        else:
            width, height = 800, 800

        # Return mock image information
        return {
            "image_id": f"{session_id}_{safe_name}",
            "name": image_name,
            "file_path": file_path,
            "width": width,
            "height": height,
            "format": "png",
            "type": image_type,
            "created_at": datetime.now().isoformat(),
            "prompt_used": prompt.get("prompt", ""),
            "metadata": {
                "style": artist_profile.get("style", "Unknown"),
                "is_mock": True,
            },
        }

    def generate_artist_image_set(
        self,
        artist_profile: Dict[str, Any],
        prompts: Dict[str, Dict[str, Any]],
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Generate a complete set of artist images.

        Args:
            artist_profile: The artist profile
            prompts: Dictionary of image prompts by type
            session_id: Session ID for tracking

        Returns:
            Dictionary containing all generated images
        """
        logger.info(f"Generating artist image set for session {session_id}")

        # Create image set directory
        image_set_dir = os.path.join(self.output_dir, session_id, "image_set")
        os.makedirs(image_set_dir, exist_ok=True)

        # Generate images for each type
        images = {}
        for image_type, prompt in prompts.items():
            image = self.generate_image(
                prompt=prompt,
                artist_profile=artist_profile,
                session_id=session_id,
                image_type=image_type,
                image_name=f"{artist_profile.get('name', 'Artist')}_{image_type}",
            )

            images[image_type] = image

        # Return the complete image set
        return {
            "set_id": f"{session_id}_image_set",
            "artist": artist_profile.get("name", "Unknown Artist"),
            "images": images,
            "total_images": len(images),
            "created_at": datetime.now().isoformat(),
            "directory": image_set_dir,
            "metadata": {
                "style": artist_profile.get("style", "Unknown"),
                "is_mock": True,
            },
        }

    def generate_album_artwork(
        self,
        album_info: Dict[str, Any],
        artist_profile: Dict[str, Any],
        prompt: Dict[str, Any],
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Generate artwork for an album.

        Args:
            album_info: Information about the album
            artist_profile: The artist profile
            prompt: The image generation prompt
            session_id: Session ID for tracking

        Returns:
            Dictionary containing the album artwork information
        """
        logger.info(f"Generating album artwork for session {session_id}")

        # Generate the album cover
        album_cover = self.generate_image(
            prompt=prompt,
            artist_profile=artist_profile,
            session_id=session_id,
            image_type="album_cover",
            image_name=f"{album_info.get('title', 'Album')}_cover",
        )

        # Return the album artwork information
        return {
            "album_id": album_info.get("album_id", f"{session_id}_album"),
            "title": album_info.get("title", "Untitled Album"),
            "artist": artist_profile.get("name", "Unknown Artist"),
            "cover_image": album_cover,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "style": artist_profile.get("style", "Unknown"),
                "is_mock": True,
            },
        }


# Factory function to create an image generator
def create_image_generator(
    output_dir: str = "/tmp/artist_flow/images", mock: bool = True
) -> Any:
    """
    Factory function to create an image generator.

    Args:
        output_dir: Directory where image files will be saved
        mock: Whether to use the mock implementation

    Returns:
        An image generator instance
    """
    if mock:
        return MockImageGenerator(output_dir=output_dir)
    else:
        # In the future, this would return a real implementation
        logger.warning("Real image generator not implemented, using mock")
        return MockImageGenerator(output_dir=output_dir)


# Example usage
if __name__ == "__main__":
    # Test the simple generate_mock_image function
    example_prompt = "Create a profile image with VHS retro style for a dark trap artist in an urban night setting"
    image_info = generate_mock_image(example_prompt)
    print("Simple mock image generation:")
    import json

    print(json.dumps(image_info, indent=2))

    # Test the class-based approach
    generator = create_image_generator()

    # Example artist profile
    example_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
    }

    # Example prompt
    example_prompt = {
        "prompt": "Create a mysterious profile image for a dark trap artist",
        "parameters": {"style": "Mysterious, Cold", "format": "portrait"},
    }

    # Generate an image
    image = generator.generate_image(
        prompt=example_prompt,
        artist_profile=example_profile,
        session_id="test_session_123",
        image_type="profile",
    )

    # Print the result
    print("\nClass-based mock image generation:")
    print(json.dumps(image, indent=2))
