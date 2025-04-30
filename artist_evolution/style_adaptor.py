import logging
from typing import Dict, Any
import random

logger = logging.getLogger(__name__)

class StyleAdaptationError(Exception):
    """Custom exception for style adaptation errors."""
    pass

def adapt_generation_parameters(artist_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Adapts content generation parameters based on the evolved artist profile.

    This function translates the high-level profile attributes (genres, keywords)
    into more concrete parameters that might be used by generation services
    (like Suno prompt adjustments, Luma style references, etc.).

    Args:
        artist_profile: The evolved artist profile dictionary.

    Returns:
        A dictionary containing adapted parameters for content generation.
        The structure of this dictionary depends heavily on how the generation
        services (Suno, Luma, etc.) are prompted or configured.
    """
    logger.info(f"Adapting generation parameters for artist ID: {artist_profile.get("id")}")
    adapted_params = {
        "suno_prompt_modifiers": [],
        "luma_style_reference": None, # Placeholder for potential Luma style image/prompt
        "video_keywords": [] # Keywords for stock video search
    }

    try:
        genres = artist_profile.get("genres", [])
        keywords = artist_profile.get("style_keywords", [])

        # --- Suno Prompt Adaptation --- 
        # Combine genres and keywords, prioritize keywords
        suno_elements = keywords + genres
        # Simple approach: randomly pick a few elements, ensure primary genre is included
        prompt_parts = []
        if genres:
            prompt_parts.append(random.choice(genres)) # Ensure at least one genre
        
        num_keywords_to_add = min(len(keywords), 3) # Add up to 3 keywords
        if num_keywords_to_add > 0:
            prompt_parts.extend(random.sample(keywords, num_keywords_to_add))
        
        # Remove duplicates and limit length
        adapted_params["suno_prompt_modifiers"] = list(dict.fromkeys(prompt_parts))[:4] # Limit total modifiers
        logger.debug(f"Suno prompt modifiers: {adapted_params["suno_prompt_modifiers"]}")

        # --- Luma Style Adaptation --- 
        # Placeholder: Could involve selecting a reference image based on keywords
        # or generating a specific style prompt for Luma.
        if "cinematic" in keywords:
            adapted_params["luma_style_reference"] = "cinematic lighting, high detail"
        elif "retro" in keywords:
             adapted_params["luma_style_reference"] = "80s film grain, neon glow"
        logger.debug(f"Luma style reference: {adapted_params["luma_style_reference"]}")

        # --- Stock Video Keyword Adaptation --- 
        # Use genres and keywords for video search
        video_elements = keywords + genres
        adapted_params["video_keywords"] = list(dict.fromkeys(video_elements))[:5] # Limit keywords
        logger.debug(f"Stock video keywords: {adapted_params["video_keywords"]}")

        # --- TODO: Integration Point --- 
        # These adapted_params would then be passed to the respective service calls:
        # - track_service.generate_track(..., prompt_modifiers=adapted_params["suno_prompt_modifiers"])
        # - video_service.generate_video(..., style_reference=adapted_params["luma_style_reference"])
        # - video_selector.select_stock_videos(..., query_keywords=adapted_params["video_keywords"])

        logger.info(f"Successfully adapted generation parameters for artist ID: {artist_profile.get("id")}")
        return adapted_params

    except Exception as e:
        logger.error(f"Error adapting generation parameters for artist {artist_profile.get("id")}: {e}", exc_info=True)
        raise StyleAdaptationError(f"Failed to adapt parameters: {e}")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.DEBUG, format=	%(asctime)s - %(name)s - %(levelname)s - %(message)s	)

    # Example evolved profile (could come from artist_evolution_service)
    test_profile = {
        "id": 1,
        "name": "Synthwave Dreamer",
        "genres": ["synthwave", "electronic", "ambient"],
        "style_keywords": ["80s", "retro", "neon", "dreamy", "engaging"], # Added "engaging"
        "evolution_log": ["2025-04-30 10:00:00: Added keyword engaging due to high likes."]
    }

    print("--- Adapting Parameters --- ")
    try:
        params = adapt_generation_parameters(test_profile)
        print("\nAdapted Parameters:")
        print(json.dumps(params, indent=2))
    except StyleAdaptationError as e:
        print(f"Adaptation Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

