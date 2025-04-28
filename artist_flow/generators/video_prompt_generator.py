"""
Video Prompt Generator Module

This module provides a system for generating detailed prompts for short-form video content
(TikTok, Threads, YouTube Shorts) based on an artist's style, song mood, and social trends.
It creates well-structured, detailed prompts suitable for automated video assembly.

The module generates prompts covering various aspects of video content including:
- Desired visual style
- Target audience emotions
- Recommended tempo of visual cuts
- Suggested types of footage
- Special effects hints
- Scene dynamics
- Hashtag and social trend integration
"""

from typing import Dict, List, Optional, Any, Union
import logging
import random
import os
import json
from pathlib import Path
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("video_prompt_generator")

# Try to load environment variables if .env exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    logger.info("dotenv not installed, skipping environment variable loading")


class VideoPromptGenerator:
    """
    Generates detailed prompts for short-form video content based on artist profiles and tracks.

    This class provides methods to generate well-structured prompts covering all aspects
    of video content, suitable for automated video assembly for platforms like TikTok,
    Threads, and YouTube Shorts.
    """

    def __init__(self, template_variety: int = 3, seed: Optional[int] = None):
        """
        Initialize the video prompt generator.

        Args:
            template_variety: Number of template variations to use for each section
            seed: Optional random seed for reproducible generation
        """
        self.template_variety = template_variety

        # Set random seed if provided
        if seed is not None:
            random.seed(seed)

        # Load visual style database
        self.visual_style_elements = self._load_visual_style_database()

        # Load footage type database
        self.footage_type_elements = self._load_footage_type_database()

        # Load special effects database
        self.special_effects_elements = self._load_special_effects_database()

        # Load social trends database
        self.social_trends_elements = self._load_social_trends_database()

        logger.info("Initialized VideoPromptGenerator")

    def _load_visual_style_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the visual style database with elements for different video aesthetics.

        Returns:
            Dictionary mapping style names to their visual elements
        """
        # Visual style elements dictionary
        visual_style_elements = {
            "vhs retro": {
                "description": "Nostalgic 80s/90s VHS tape aesthetic with tracking lines and analog feel",
                "color_palette": [
                    "muted colors",
                    "high contrast",
                    "slight color bleeding",
                    "occasional color distortion",
                ],
                "visual_elements": [
                    "tracking lines",
                    "timestamp overlay",
                    "4:3 aspect ratio",
                    "slight wobble",
                    "static noise",
                ],
                "editing_style": [
                    "jump cuts",
                    "zoom transitions",
                    "occasional glitches",
                    "date/time stamps",
                ],
                "lighting": [
                    "high contrast",
                    "slightly washed out",
                    "lens flares",
                    "night scenes with glow",
                ],
                "suitable_genres": [
                    "synthwave",
                    "vaporwave",
                    "lo-fi",
                    "phonk",
                    "retro trap",
                ],
            },
            "cinematic noir": {
                "description": "Dark, moody, film-noir inspired aesthetic with dramatic shadows and contrast",
                "color_palette": [
                    "high contrast",
                    "desaturated",
                    "black and white",
                    "dark blues",
                    "deep shadows",
                ],
                "visual_elements": [
                    "dramatic shadows",
                    "silhouettes",
                    "rain-soaked streets",
                    "neon reflections",
                    "smoke",
                ],
                "editing_style": [
                    "slow pans",
                    "dramatic cuts",
                    "lingering shots",
                    "extreme close-ups",
                ],
                "lighting": [
                    "dramatic side lighting",
                    "harsh shadows",
                    "low key",
                    "spotlight effects",
                ],
                "suitable_genres": [
                    "dark trap",
                    "jazz-influenced",
                    "moody electronic",
                    "atmospheric",
                ],
            },
            "urban grime": {
                "description": "Raw, gritty urban aesthetic with street culture elements and rough textures",
                "color_palette": [
                    "desaturated",
                    "high contrast",
                    "occasional color pops",
                    "urban tones",
                ],
                "visual_elements": [
                    "graffiti",
                    "concrete textures",
                    "chain-link fences",
                    "urban decay",
                    "street signs",
                ],
                "editing_style": [
                    "quick cuts",
                    "handheld camera feel",
                    "occasional shake",
                    "raw transitions",
                ],
                "lighting": [
                    "harsh street lights",
                    "night scenes",
                    "flashy highlights",
                    "shadows",
                ],
                "suitable_genres": ["hip hop", "trap", "drill", "grime", "street rap"],
            },
            "neon cyberpunk": {
                "description": "Futuristic aesthetic with bright neon colors, digital elements, and urban nightscapes",
                "color_palette": [
                    "neon pink",
                    "electric blue",
                    "bright purple",
                    "deep blacks",
                    "high contrast",
                ],
                "visual_elements": [
                    "neon signs",
                    "reflective surfaces",
                    "digital overlays",
                    "cityscapes",
                    "tech elements",
                ],
                "editing_style": [
                    "glitch transitions",
                    "digital distortion",
                    "quick cuts",
                    "overlay effects",
                ],
                "lighting": [
                    "neon glow",
                    "high contrast",
                    "colored lighting",
                    "lens flares",
                ],
                "suitable_genres": [
                    "synthwave",
                    "cyberpunk electronic",
                    "future bass",
                    "techno",
                    "electronic",
                ],
            },
            "dreamy aesthetic": {
                "description": "Soft, ethereal visuals with dreamy lighting, pastel colors, and gentle movements",
                "color_palette": [
                    "pastel tones",
                    "soft whites",
                    "gentle pinks",
                    "baby blues",
                    "light exposure",
                ],
                "visual_elements": [
                    "lens flares",
                    "soft focus",
                    "floating particles",
                    "nature elements",
                    "clouds",
                ],
                "editing_style": [
                    "slow motion",
                    "gentle transitions",
                    "overlays",
                    "soft fades",
                ],
                "lighting": [
                    "soft diffused light",
                    "golden hour",
                    "lens flares",
                    "overexposure",
                ],
                "suitable_genres": [
                    "ambient",
                    "chill",
                    "lo-fi",
                    "dream pop",
                    "soft electronic",
                ],
            },
            "hyper pop": {
                "description": "Exaggerated, colorful, internet-culture inspired aesthetic with digital elements",
                "color_palette": [
                    "saturated colors",
                    "neon",
                    "pastel",
                    "high contrast",
                    "color shifts",
                ],
                "visual_elements": [
                    "digital icons",
                    "emojis",
                    "3D renders",
                    "internet culture references",
                    "glitch art",
                ],
                "editing_style": [
                    "extremely fast cuts",
                    "digital transitions",
                    "chaotic rhythm",
                    "distortion effects",
                ],
                "lighting": [
                    "bright",
                    "colorful",
                    "shifting",
                    "digital",
                    "high contrast",
                ],
                "suitable_genres": [
                    "hyper pop",
                    "glitch pop",
                    "experimental electronic",
                    "digital hardcore",
                ],
            },
            "anime inspired": {
                "description": "Japanese animation inspired aesthetic with bold colors, dynamic movement, and stylized elements",
                "color_palette": [
                    "bold colors",
                    "high contrast",
                    "flat color areas",
                    "stylized lighting",
                ],
                "visual_elements": [
                    "anime clips",
                    "manga panels",
                    "Japanese text",
                    "stylized effects",
                    "character focus",
                ],
                "editing_style": [
                    "dynamic cuts",
                    "speed lines",
                    "impact frames",
                    "dramatic pauses",
                ],
                "lighting": [
                    "dramatic",
                    "stylized",
                    "high contrast",
                    "colored shadows",
                ],
                "suitable_genres": [
                    "j-pop influenced",
                    "anime soundtracks",
                    "future bass",
                    "electronic",
                ],
            },
            "minimalist": {
                "description": "Clean, simple aesthetic with focus on negative space, simple compositions, and subtle movements",
                "color_palette": [
                    "monochrome",
                    "limited palette",
                    "high contrast",
                    "clean whites",
                    "deep blacks",
                ],
                "visual_elements": [
                    "simple shapes",
                    "negative space",
                    "clean typography",
                    "minimal textures",
                ],
                "editing_style": [
                    "simple cuts",
                    "static shots",
                    "minimal movement",
                    "deliberate pacing",
                ],
                "lighting": ["clean", "even", "dramatic shadows", "high key"],
                "suitable_genres": [
                    "minimal electronic",
                    "ambient",
                    "experimental",
                    "modern classical",
                ],
            },
        }

        # Check for environment variable with custom visual style database path
        custom_db_path = os.getenv("VIDEO_STYLE_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, "r") as f:
                    custom_styles = json.load(f)
                    # Merge with default styles, with custom styles taking precedence
                    visual_style_elements.update(custom_styles)
                    logger.info(
                        f"Loaded custom visual style database from {custom_db_path}"
                    )
            except Exception as e:
                logger.warning(f"Failed to load custom visual style database: {e}")

        return visual_style_elements

    def _load_footage_type_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the footage type database with elements for different video content.

        Returns:
            Dictionary mapping footage categories to their elements
        """
        # Footage type elements dictionary
        footage_type_elements = {
            "urban": {
                "description": "City and urban environment footage",
                "examples": [
                    "city skylines",
                    "urban streets",
                    "neon-lit alleys",
                    "subway stations",
                    "rooftops",
                    "traffic",
                    "city lights at night",
                    "urban architecture",
                ],
                "mood_associations": [
                    "energetic",
                    "moody",
                    "atmospheric",
                    "gritty",
                    "modern",
                ],
                "suitable_genres": ["hip hop", "trap", "electronic", "pop", "r&b"],
            },
            "nature": {
                "description": "Natural environments and landscapes",
                "examples": [
                    "forests",
                    "mountains",
                    "oceans",
                    "rivers",
                    "deserts",
                    "clouds",
                    "sunsets",
                    "wildlife",
                    "plants",
                    "rain",
                    "snow",
                ],
                "mood_associations": [
                    "peaceful",
                    "majestic",
                    "melancholic",
                    "inspiring",
                    "reflective",
                ],
                "suitable_genres": ["ambient", "folk", "chill", "lo-fi", "acoustic"],
            },
            "abstract": {
                "description": "Non-representational, artistic, and experimental visuals",
                "examples": [
                    "ink in water",
                    "light patterns",
                    "particle effects",
                    "glitch art",
                    "3D renders",
                    "abstract animations",
                    "kaleidoscope effects",
                ],
                "mood_associations": [
                    "mysterious",
                    "experimental",
                    "psychedelic",
                    "artistic",
                    "emotional",
                ],
                "suitable_genres": [
                    "electronic",
                    "experimental",
                    "ambient",
                    "psychedelic",
                    "avant-garde",
                ],
            },
            "lifestyle": {
                "description": "People engaged in various activities and lifestyles",
                "examples": [
                    "fashion",
                    "parties",
                    "workouts",
                    "dancing",
                    "skateboarding",
                    "driving",
                    "shopping",
                    "dining",
                    "traveling",
                ],
                "mood_associations": [
                    "energetic",
                    "aspirational",
                    "social",
                    "trendy",
                    "relatable",
                ],
                "suitable_genres": ["pop", "hip hop", "dance", "electronic", "r&b"],
            },
            "nostalgic": {
                "description": "Retro and vintage-inspired footage evoking nostalgia",
                "examples": [
                    "vintage film",
                    "old TV shows",
                    "retro video games",
                    "childhood toys",
                    "vintage cars",
                    "old technology",
                    "historical footage",
                ],
                "mood_associations": [
                    "nostalgic",
                    "warm",
                    "bittersweet",
                    "comforting",
                    "reflective",
                ],
                "suitable_genres": [
                    "lo-fi",
                    "synthwave",
                    "vaporwave",
                    "indie",
                    "retro-inspired",
                ],
            },
            "automotive": {
                "description": "Cars, motorcycles, and automotive culture",
                "examples": [
                    "drifting cars",
                    "night drives",
                    "car meets",
                    "motorcycles",
                    "racing",
                    "car details",
                    "highway driving",
                    "automotive POV",
                ],
                "mood_associations": [
                    "exciting",
                    "fast-paced",
                    "cool",
                    "powerful",
                    "freedom",
                ],
                "suitable_genres": ["phonk", "trap", "electronic", "hip hop", "rock"],
            },
            "anime": {
                "description": "Japanese animation and anime-inspired content",
                "examples": [
                    "anime clips",
                    "manga panels",
                    "anime characters",
                    "anime scenery",
                    "anime effects",
                    "stylized animations",
                ],
                "mood_associations": [
                    "expressive",
                    "emotional",
                    "stylized",
                    "energetic",
                    "dramatic",
                ],
                "suitable_genres": [
                    "j-pop",
                    "future bass",
                    "electronic",
                    "lo-fi",
                    "anime soundtracks",
                ],
            },
            "cyberpunk": {
                "description": "Futuristic, high-tech, dystopian urban environments",
                "examples": [
                    "neon cities",
                    "futuristic technology",
                    "holograms",
                    "cybernetic elements",
                    "digital interfaces",
                    "dystopian urban scenes",
                ],
                "mood_associations": [
                    "futuristic",
                    "edgy",
                    "dark",
                    "technological",
                    "atmospheric",
                ],
                "suitable_genres": [
                    "synthwave",
                    "cyberpunk electronic",
                    "techno",
                    "industrial",
                    "electronic",
                ],
            },
        }

        # Check for environment variable with custom footage type database path
        custom_db_path = os.getenv("VIDEO_FOOTAGE_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, "r") as f:
                    custom_footage = json.load(f)
                    # Merge with default footage types, with custom footage taking precedence
                    footage_type_elements.update(custom_footage)
                    logger.info(
                        f"Loaded custom footage type database from {custom_db_path}"
                    )
            except Exception as e:
                logger.warning(f"Failed to load custom footage type database: {e}")

        return footage_type_elements

    def _load_special_effects_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the special effects database with elements for video effects.

        Returns:
            Dictionary mapping effect categories to their elements
        """
        # Special effects elements dictionary
        special_effects_elements = {
            "retro": {
                "description": "Effects that create a vintage or retro feel",
                "examples": [
                    "VHS tracking lines",
                    "film grain",
                    "color aberration",
                    "date/time stamps",
                    "old TV static",
                    "film burns",
                    "light leaks",
                    "VHS rewind effects",
                ],
                "suitable_styles": ["vhs retro", "nostalgic", "lo-fi"],
                "suitable_genres": ["synthwave", "vaporwave", "lo-fi", "phonk"],
            },
            "glitch": {
                "description": "Digital distortion and glitch-based effects",
                "examples": [
                    "digital glitches",
                    "pixel sorting",
                    "datamoshing",
                    "RGB splits",
                    "digital artifacts",
                    "scan lines",
                    "digital noise",
                    "frame drops",
                ],
                "suitable_styles": ["cyberpunk", "hyper pop", "digital"],
                "suitable_genres": [
                    "electronic",
                    "glitch hop",
                    "experimental",
                    "digital hardcore",
                ],
            },
            "cinematic": {
                "description": "Effects that create a film-like quality",
                "examples": [
                    "letterboxing",
                    "film grain",
                    "color grading",
                    "lens flares",
                    "anamorphic lens effects",
                    "cinematic transitions",
                    "depth of field",
                ],
                "suitable_styles": ["cinematic noir", "dreamy aesthetic", "minimalist"],
                "suitable_genres": ["orchestral", "ambient", "cinematic", "emotional"],
            },
            "motion": {
                "description": "Effects that enhance or stylize movement",
                "examples": [
                    "slow motion",
                    "time lapse",
                    "motion blur",
                    "speed ramping",
                    "freeze frames",
                    "reverse playback",
                    "stutter cuts",
                ],
                "suitable_styles": ["urban grime", "cinematic noir", "hyper pop"],
                "suitable_genres": ["trap", "hip hop", "electronic", "dance"],
            },
            "overlay": {
                "description": "Elements that overlay on top of footage",
                "examples": [
                    "text overlays",
                    "lyrics display",
                    "animated graphics",
                    "emoji",
                    "particle effects",
                    "light leaks",
                    "dust particles",
                    "weather effects",
                ],
                "suitable_styles": ["hyper pop", "anime inspired", "dreamy aesthetic"],
                "suitable_genres": ["pop", "electronic", "hip hop", "trap"],
            },
            "transition": {
                "description": "Stylized transitions between shots",
                "examples": [
                    "glitch transitions",
                    "whip pans",
                    "zoom transitions",
                    "light leaks",
                    "digital distortion",
                    "color shifts",
                    "wipes",
                    "dissolves",
                ],
                "suitable_styles": ["vhs retro", "hyper pop", "urban grime"],
                "suitable_genres": ["electronic", "trap", "hip hop", "dance"],
            },
            "color": {
                "description": "Effects that manipulate color",
                "examples": [
                    "color grading",
                    "duotone",
                    "color shifting",
                    "selective color",
                    "RGB splits",
                    "color flashes",
                    "hue rotation",
                    "saturation pulses",
                ],
                "suitable_styles": ["neon cyberpunk", "dreamy aesthetic", "hyper pop"],
                "suitable_genres": ["electronic", "pop", "synthwave", "trap"],
            },
            "3D": {
                "description": "Three-dimensional and depth-based effects",
                "examples": [
                    "3D animations",
                    "3D text",
                    "parallax effects",
                    "3D particle systems",
                    "3D scene transitions",
                    "depth mapping",
                    "3D glitches",
                ],
                "suitable_styles": ["hyper pop", "neon cyberpunk", "minimalist"],
                "suitable_genres": [
                    "electronic",
                    "future bass",
                    "trap",
                    "experimental",
                ],
            },
        }

        # Check for environment variable with custom special effects database path
        custom_db_path = os.getenv("VIDEO_EFFECTS_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, "r") as f:
                    custom_effects = json.load(f)
                    # Merge with default effects, with custom effects taking precedence
                    special_effects_elements.update(custom_effects)
                    logger.info(
                        f"Loaded custom special effects database from {custom_db_path}"
                    )
            except Exception as e:
                logger.warning(f"Failed to load custom special effects database: {e}")

        return special_effects_elements

    def _load_social_trends_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the social trends database with elements for different platforms.

        Returns:
            Dictionary mapping platform names to their trend elements
        """
        # Social trends elements dictionary
        social_trends_elements = {
            "tiktok": {
                "description": "Trends and formats popular on TikTok",
                "trending_formats": [
                    "transition reveals",
                    "text-based storytelling",
                    "POV videos",
                    "before/after reveals",
                    "lip syncing",
                    "dance challenges",
                    "day in the life",
                    "outfit transitions",
                ],
                "popular_hashtags": [
                    "#fyp",
                    "#foryoupage",
                    "#viral",
                    "#trending",
                    "#aesthetic",
                    "#vibes",
                    "#pov",
                    "#transition",
                ],
                "engagement_techniques": [
                    "hook in first 3 seconds",
                    "text overlay storytelling",
                    "trending sound usage",
                    "call to action",
                    "loop-worthy content",
                ],
                "optimal_length": "15-60 seconds",
            },
            "instagram_reels": {
                "description": "Trends and formats popular on Instagram Reels",
                "trending_formats": [
                    "aesthetic montages",
                    "tutorial snippets",
                    "outfit showcases",
                    "behind the scenes",
                    "day in the life",
                    "transition videos",
                    "quote/text reveals",
                    "product showcases",
                ],
                "popular_hashtags": [
                    "#reels",
                    "#instareels",
                    "#trending",
                    "#viral",
                    "#aesthetic",
                    "#vibes",
                    "#explore",
                    "#music",
                ],
                "engagement_techniques": [
                    "visually appealing aesthetic",
                    "trending audio usage",
                    "question prompts",
                    "high-quality visuals",
                    "lifestyle content",
                ],
                "optimal_length": "15-30 seconds",
            },
            "youtube_shorts": {
                "description": "Trends and formats popular on YouTube Shorts",
                "trending_formats": [
                    "quick tutorials",
                    "facts/information",
                    "reaction clips",
                    "comedy sketches",
                    "music highlights",
                    "gaming clips",
                    "behind the scenes",
                    "quick reviews",
                ],
                "popular_hashtags": [
                    "#shorts",
                    "#youtubeshorts",
                    "#viral",
                    "#trending",
                    "#music",
                    "#gaming",
                    "#tutorial",
                    "#reaction",
                ],
                "engagement_techniques": [
                    "clear value proposition",
                    "question hooks",
                    "curiosity gaps",
                    "quick educational content",
                    "entertainment focus",
                ],
                "optimal_length": "15-60 seconds",
            },
            "threads": {
                "description": "Trends and formats popular on Threads",
                "trending_formats": [
                    "aesthetic loops",
                    "minimalist content",
                    "text-heavy overlays",
                    "conversation starters",
                    "quick takes",
                    "visual loops",
                    "behind the scenes",
                    "casual content",
                ],
                "popular_hashtags": [
                    "#threads",
                    "#trending",
                    "#aesthetic",
                    "#vibes",
                    "#loop",
                    "#dailycontent",
                    "#creator",
                    "#mood",
                ],
                "engagement_techniques": [
                    "conversation starters",
                    "relatable content",
                    "aesthetic focus",
                    "casual authentic feel",
                    "community engagement",
                ],
                "optimal_length": "10-30 seconds",
            },
        }

        # Check for environment variable with custom social trends database path
        custom_db_path = os.getenv("VIDEO_TRENDS_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, "r") as f:
                    custom_trends = json.load(f)
                    # Merge with default trends, with custom trends taking precedence
                    social_trends_elements.update(custom_trends)
                    logger.info(
                        f"Loaded custom social trends database from {custom_db_path}"
                    )
            except Exception as e:
                logger.warning(f"Failed to load custom social trends database: {e}")

        return social_trends_elements

    def _extract_visual_style_elements(self, style: str) -> Dict[str, Any]:
        """
        Extract key visual elements associated with a style.

        Args:
            style: Visual style description

        Returns:
            Dictionary of visual style elements
        """
        # Extract style keywords
        style_keywords = [word.strip().lower() for word in style.split(",")]

        # Look for direct matches first
        for keyword in style_keywords:
            if keyword in self.visual_style_elements:
                return self.visual_style_elements[keyword]

        # Try to match partial keywords
        for keyword in style_keywords:
            for style_name, elements in self.visual_style_elements.items():
                if keyword in style_name or style_name in keyword:
                    return elements

        # If no matches found, return a default style based on genre or mood
        # Default to "vhs retro" as a fallback
        return self.visual_style_elements["vhs retro"]

    def _extract_footage_types(self, genre: str, mood: str) -> List[str]:
        """
        Extract appropriate footage types based on genre and mood.

        Args:
            genre: Music genre
            mood: Track mood

        Returns:
            List of suggested footage types
        """
        suitable_footage = []

        # Normalize inputs
        genre_lower = genre.lower()
        mood_lower = mood.lower()

        # Check each footage type for suitability
        for footage_name, footage_data in self.footage_type_elements.items():
            # Check if genre matches
            genre_match = any(
                g.lower() in genre_lower or genre_lower in g.lower()
                for g in footage_data["suitable_genres"]
            )

            # Check if mood matches
            mood_match = any(
                m.lower() in mood_lower or mood_lower in m.lower()
                for m in footage_data["mood_associations"]
            )

            # If either matches, add some examples from this footage type
            if genre_match or mood_match:
                examples = footage_data["examples"]
                suitable_footage.extend(random.sample(examples, min(2, len(examples))))

        # If we didn't find any suitable footage, return some generic options
        if not suitable_footage:
            suitable_footage = [
                "urban streets",
                "city lights",
                "abstract visuals",
                "stylized scenes",
                "atmospheric footage",
            ]

        # Remove duplicates while preserving order
        seen = set()
        return [x for x in suitable_footage if not (x in seen or seen.add(x))]

    def _extract_special_effects(self, visual_style: str) -> List[str]:
        """
        Extract appropriate special effects based on visual style.

        Args:
            visual_style: Visual style description

        Returns:
            List of suggested special effects
        """
        suitable_effects = []

        # Normalize input
        style_lower = visual_style.lower()

        # Check each effect type for suitability
        for effect_name, effect_data in self.special_effects_elements.items():
            # Check if style matches
            style_match = any(
                s.lower() in style_lower or style_lower in s.lower()
                for s in effect_data["suitable_styles"]
            )

            # If matches, add some examples from this effect type
            if style_match:
                examples = effect_data["examples"]
                suitable_effects.extend(random.sample(examples, min(2, len(examples))))

        # If we didn't find any suitable effects, return some generic options
        if not suitable_effects:
            suitable_effects = [
                "color grading",
                "subtle transitions",
                "text overlays",
                "motion effects",
                "atmospheric elements",
            ]

        # Remove duplicates while preserving order
        seen = set()
        return [x for x in suitable_effects if not (x in seen or seen.add(x))]

    def _extract_social_trends(self, platform: str) -> Dict[str, Any]:
        """
        Extract social trends for a specific platform.

        Args:
            platform: Social media platform name

        Returns:
            Dictionary of platform-specific trend elements
        """
        # Normalize platform name
        platform_lower = platform.lower()

        # Direct lookup
        if platform_lower in self.social_trends_elements:
            return self.social_trends_elements[platform_lower]

        # Try to match based on partial matches
        for platform_name, elements in self.social_trends_elements.items():
            if platform_name in platform_lower or platform_lower in platform_name:
                return elements

        # Default to TikTok if no match found
        return self.social_trends_elements["tiktok"]

    def _determine_visual_tempo(self, music_tempo: str, mood: str) -> str:
        """
        Determine appropriate visual editing tempo based on music tempo and mood.

        Args:
            music_tempo: Music tempo category (slow, medium, fast)
            mood: Track mood

        Returns:
            Visual editing tempo recommendation
        """
        # Normalize inputs
        tempo_lower = music_tempo.lower() if music_tempo else "medium"
        mood_lower = mood.lower() if mood else ""

        # Energetic moods tend to have faster visual tempo
        energetic_moods = ["energetic", "aggressive", "upbeat", "hype", "intense"]
        mood_is_energetic = any(m in mood_lower for m in energetic_moods)

        # Calm moods tend to have slower visual tempo
        calm_moods = ["calm", "melancholic", "sad", "peaceful", "ambient", "chill"]
        mood_is_calm = any(m in mood_lower for m in calm_moods)

        # Determine visual tempo based on music tempo and mood
        if "slow" in tempo_lower:
            if mood_is_energetic:
                return "moderate"
            else:
                return "slow"
        elif "fast" in tempo_lower:
            if mood_is_calm:
                return "moderate"
            else:
                return "rapid"
        else:  # medium tempo
            if mood_is_energetic:
                return "moderately fast"
            elif mood_is_calm:
                return "moderately slow"
            else:
                return "moderate"

    def _determine_scene_dynamics(self, music_tempo: str, genre: str) -> str:
        """
        Determine appropriate scene dynamics based on music tempo and genre.

        Args:
            music_tempo: Music tempo category (slow, medium, fast)
            genre: Music genre

        Returns:
            Scene dynamics recommendation
        """
        # Normalize inputs
        tempo_lower = music_tempo.lower() if music_tempo else "medium"
        genre_lower = genre.lower() if genre else ""

        # Genres that often have more dynamic visuals
        dynamic_genres = [
            "edm",
            "trap",
            "electronic",
            "dance",
            "pop",
            "hip hop",
            "phonk",
        ]
        genre_is_dynamic = any(g in genre_lower for g in dynamic_genres)

        # Genres that often have more static or atmospheric visuals
        static_genres = ["ambient", "lo-fi", "chill", "acoustic", "jazz", "classical"]
        genre_is_static = any(g in genre_lower for g in static_genres)

        # Determine scene dynamics based on tempo and genre
        if "slow" in tempo_lower:
            if genre_is_dynamic:
                return "slow but deliberate movement, occasional dynamic moments"
            else:
                return "static shots with minimal movement, atmospheric"
        elif "fast" in tempo_lower:
            if genre_is_static:
                return "moderate movement with rhythmic patterns"
            else:
                return "highly dynamic, constant movement, energetic flow"
        else:  # medium tempo
            if genre_is_dynamic:
                return (
                    "steady movement with rhythmic patterns, occasional dynamic moments"
                )
            elif genre_is_static:
                return "gentle movement, flowing transitions, atmospheric"
            else:
                return "balanced movement, natural flow, rhythmic patterns"

    def generate_video_prompt(
        self,
        artist_profile: Dict[str, Any],
        track_info: Dict[str, Any],
        platform: str = "tiktok",
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive prompt for creating short-form video content.

        Args:
            artist_profile: Dictionary containing the artist's profile information
            track_info: Dictionary containing track information
            platform: Target social media platform (tiktok, instagram_reels, youtube_shorts, threads)
            overrides: Optional dictionary with specific overrides for this video:
                - visual_style: Desired visual style
                - audience_emotion: Target audience emotion
                - footage_types: Suggested types of footage
                - special_effects: Special effects hints
                - scene_dynamics: Scene dynamics description
                - hashtags: Specific hashtags to include

        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(
            f"Generating video prompt for artist: {artist_profile.get('name', 'Unknown')}"
        )

        # Initialize overrides if None
        if overrides is None:
            overrides = {}

        # Extract key elements from the profiles
        artist_name = artist_profile.get("name", "Artist")
        genre = artist_profile.get("genre", "Electronic")
        artist_style = artist_profile.get("style", "Unique")

        # Extract track information
        track_title = track_info.get("title", "Track")
        track_mood = track_info.get("mood", artist_style)
        track_tempo = track_info.get("tempo", "medium")
        audience_emotion = track_info.get("audience_emotion", "")

        # Get visual style from overrides or derive from artist style and track mood
        visual_style = overrides.get("visual_style", "")
        if not visual_style:
            # Combine artist style and track mood for visual style
            visual_style = f"{artist_style}, {track_mood}"

        # Get audience emotion from overrides or track info
        target_emotion = overrides.get("audience_emotion", audience_emotion)
        if not target_emotion:
            target_emotion = "emotional connection, engagement"

        # Determine visual tempo based on track tempo and mood
        visual_tempo = overrides.get("visual_tempo", "")
        if not visual_tempo:
            visual_tempo = self._determine_visual_tempo(track_tempo, track_mood)

        # Get footage types from overrides or derive from genre and mood
        footage_types = overrides.get("footage_types", [])
        if not footage_types:
            footage_types = self._extract_footage_types(genre, track_mood)

        # Get special effects from overrides or derive from visual style
        special_effects = overrides.get("special_effects", [])
        if not special_effects:
            special_effects = self._extract_special_effects(visual_style)

        # Get scene dynamics from overrides or derive from tempo and genre
        scene_dynamics = overrides.get("scene_dynamics", "")
        if not scene_dynamics:
            scene_dynamics = self._determine_scene_dynamics(track_tempo, genre)

        # Extract visual style elements
        style_elements = self._extract_visual_style_elements(visual_style)

        # Extract social trends for the specified platform
        platform_trends = self._extract_social_trends(platform)

        # Get hashtags from overrides or platform trends
        hashtags = overrides.get("hashtags", [])
        if not hashtags:
            hashtags = random.sample(
                platform_trends["popular_hashtags"],
                min(4, len(platform_trends["popular_hashtags"])),
            )

        # Build the comprehensive prompt
        prompt = f"""# Video Content Prompt for {artist_name} - "{track_title}"

## Core Video Identity
Create a {visual_style} style short-form video for {platform.capitalize()} featuring {artist_name}'s track "{track_title}".

## Visual Direction
- **Visual Style:** {visual_style}
- **Color Palette:** {', '.join(random.sample(style_elements['color_palette'], min(3, len(style_elements['color_palette']))))}
- **Key Visual Elements:** {', '.join(random.sample(style_elements['visual_elements'], min(3, len(style_elements['visual_elements']))))}
- **Editing Style:** {', '.join(random.sample(style_elements['editing_style'], min(2, len(style_elements['editing_style']))))}
- **Lighting:** {', '.join(random.sample(style_elements['lighting'], min(2, len(style_elements['lighting']))))}

## Content Direction
- **Footage Types:** {', '.join(footage_types)}
- **Visual Tempo:** {visual_tempo} cuts and transitions
- **Scene Dynamics:** {scene_dynamics}
- **Target Audience Emotion:** {target_emotion}
"""

        # Add special effects if available
        if special_effects:
            prompt += f"- **Special Effects:** {', '.join(special_effects)}\n"

        # Add platform-specific guidance
        prompt += f"""
## Platform Optimization for {platform.capitalize()}
- **Optimal Length:** {platform_trends['optimal_length']}
- **Recommended Format:** {', '.join(random.sample(platform_trends['trending_formats'], min(2, len(platform_trends['trending_formats']))))}
- **Engagement Techniques:** {', '.join(random.sample(platform_trends['engagement_techniques'], min(2, len(platform_trends['engagement_techniques']))))}
- **Hashtags:** {' '.join(hashtags)}
"""

        # Add final instructions
        prompt += """
## Creation Instructions
1. Create a video that authentically represents the artist's style and the track's mood
2. Ensure visual elements and editing rhythm complement the music
3. Optimize for mobile viewing (vertical format, readable text, clear visuals)
4. Include artist name and track title text overlay at appropriate moments
5. Design for loop-worthiness and repeat viewing
6. Focus on creating a strong hook in the first 3 seconds

The final video should be attention-grabbing, shareable, and effectively showcase the artist and track.
"""

        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "artist_name": artist_name,
                "track_title": track_title,
                "genre": genre,
                "visual_style": visual_style,
                "platform": platform,
                "timestamp": self._get_timestamp(),
            },
        }

    def generate_transition_prompt(
        self,
        artist_profile: Dict[str, Any],
        track_info: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating video transitions.

        Args:
            artist_profile: Dictionary containing the artist's profile information
            track_info: Dictionary containing track information
            overrides: Optional dictionary with specific overrides

        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(
            f"Generating transition prompt for artist: {artist_profile.get('name', 'Unknown')}"
        )

        # Initialize overrides if None
        if overrides is None:
            overrides = {}

        # Extract key elements from the profiles
        artist_name = artist_profile.get("name", "Artist")
        genre = artist_profile.get("genre", "Electronic")
        artist_style = artist_profile.get("style", "Unique")

        # Extract track information
        track_title = track_info.get("title", "Track")
        track_mood = track_info.get("mood", artist_style)
        track_tempo = track_info.get("tempo", "medium")

        # Get visual style from overrides or derive from artist style and track mood
        visual_style = overrides.get("visual_style", "")
        if not visual_style:
            # Combine artist style and track mood for visual style
            visual_style = f"{artist_style}, {track_mood}"

        # Extract visual style elements
        style_elements = self._extract_visual_style_elements(visual_style)

        # Get special effects focused on transitions
        transition_effects = []
        for effect_name, effect_data in self.special_effects_elements.items():
            if effect_name == "transition":
                transition_effects = effect_data["examples"]
                break

        # If no specific transition effects found, use general effects
        if not transition_effects:
            transition_effects = self._extract_special_effects(visual_style)

        # Build the transition prompt
        prompt = f"""# Video Transition Prompt for {artist_name} - "{track_title}"

## Transition Style Direction
Create video transitions for {artist_name}'s track "{track_title}" that match the {visual_style} visual style.

## Transition Types
- **Primary Transition Style:** {', '.join(random.sample(transition_effects, min(3, len(transition_effects))))}
- **Visual Aesthetic:** {', '.join(random.sample(style_elements['visual_elements'], min(2, len(style_elements['visual_elements']))))}
- **Color Treatment:** {', '.join(random.sample(style_elements['color_palette'], min(2, len(style_elements['color_palette']))))}

## Timing and Rhythm
- **Transition Tempo:** Match the {track_tempo} tempo of the track
- **Key Moments:** Place transitions at beat drops, chorus starts, and other key musical moments
- **Duration:** Keep transitions brief but impactful (typically 0.5-1 second)

## Technical Specifications
- **Transition Types to Create:**
  1. Scene-to-scene transitions
  2. Intro/title reveal transition
  3. Artist name/track title reveal
  4. Outro/call-to-action transition
  5. Beat-matched micro transitions for visual rhythm

The transitions should feel cohesive with the overall visual style while adding dynamic energy to the video.
"""

        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "artist_name": artist_name,
                "track_title": track_title,
                "genre": genre,
                "visual_style": visual_style,
                "timestamp": self._get_timestamp(),
            },
        }

    def generate_text_overlay_prompt(
        self,
        artist_profile: Dict[str, Any],
        track_info: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating text overlays for videos.

        Args:
            artist_profile: Dictionary containing the artist's profile information
            track_info: Dictionary containing track information
            overrides: Optional dictionary with specific overrides

        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(
            f"Generating text overlay prompt for artist: {artist_profile.get('name', 'Unknown')}"
        )

        # Initialize overrides if None
        if overrides is None:
            overrides = {}

        # Extract key elements from the profiles
        artist_name = artist_profile.get("name", "Artist")
        genre = artist_profile.get("genre", "Electronic")
        artist_style = artist_profile.get("style", "Unique")

        # Extract track information
        track_title = track_info.get("title", "Track")
        track_mood = track_info.get("mood", artist_style)

        # Get visual style from overrides or derive from artist style and track mood
        visual_style = overrides.get("visual_style", "")
        if not visual_style:
            # Combine artist style and track mood for visual style
            visual_style = f"{artist_style}, {track_mood}"

        # Extract visual style elements
        style_elements = self._extract_visual_style_elements(visual_style)

        # Build the text overlay prompt
        prompt = f"""# Text Overlay Prompt for {artist_name} - "{track_title}"

## Text Style Direction
Create text overlays for {artist_name}'s track "{track_title}" that match the {visual_style} visual style.

## Typography and Design
- **Font Style:** Choose fonts that reflect the {visual_style} aesthetic
- **Color Scheme:** Use colors from the palette: {', '.join(random.sample(style_elements['color_palette'], min(2, len(style_elements['color_palette']))))}
- **Animation Style:** {', '.join(random.sample(style_elements['editing_style'], min(2, len(style_elements['editing_style']))))}
- **Text Effects:** Consider {', '.join(random.sample(self._extract_special_effects(visual_style), min(2, len(self._extract_special_effects(visual_style)))))} for text animations

## Content Elements
- **Essential Text Elements:**
  1. Artist name: "{artist_name}"
  2. Track title: "{track_title}"
  3. Call-to-action (e.g., "Follow for more", "Stream now")
  4. Optional: brief lyric highlights or mood phrases

## Placement and Timing
- **Intro:** Include artist name and track title within first 3-5 seconds
- **Throughout:** Consider subtle lyric highlights at key moments if appropriate
- **Outro:** Repeat artist name and include call-to-action
- **Positioning:** Ensure text is readable on mobile devices (avoid extreme edges)

## Technical Specifications
- **Text Hierarchy:** Establish clear size difference between primary and secondary text
- **Legibility:** Ensure high contrast against backgrounds
- **Duration:** Give viewers enough time to read each text element
- **Consistency:** Maintain consistent style throughout while adding visual interest

The text overlays should enhance the video without distracting from the visual content or feeling disconnected from the overall aesthetic.
"""

        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "artist_name": artist_name,
                "track_title": track_title,
                "genre": genre,
                "visual_style": visual_style,
                "timestamp": self._get_timestamp(),
            },
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()


# Factory function to create a video prompt generator
def create_video_prompt_generator(
    template_variety: int = 3, seed: Optional[int] = None
) -> VideoPromptGenerator:
    """
    Factory function to create a video prompt generator.

    Args:
        template_variety: Number of template variations to use
        seed: Optional random seed for reproducible generation

    Returns:
        A video prompt generator instance
    """
    return VideoPromptGenerator(template_variety=template_variety, seed=seed)


# Convenience function for generating video prompts
def generate_video_prompt(
    artist_profile: Dict[str, Any],
    track_info: Dict[str, Any],
    platform: str = "tiktok",
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a comprehensive prompt for creating short-form video content.

    This is a convenience function that creates a generator instance and calls
    generate_video_prompt on it.

    Args:
        artist_profile: Dictionary containing the artist's profile information
        track_info: Dictionary containing track information
        platform: Target social media platform (tiktok, instagram_reels, youtube_shorts, threads)
        overrides: Optional dictionary with specific overrides for this video

    Returns:
        Dictionary containing the generated prompt and metadata
    """
    generator = create_video_prompt_generator()
    return generator.generate_video_prompt(
        artist_profile, track_info, platform, overrides
    )


# Example usage
if __name__ == "__main__":
    # Create a generator
    generator = create_video_prompt_generator(seed=42)

    # Example artist profile
    example_artist = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "themes": "Urban isolation, night life, inner struggles",
        "lyrics_language": "English",
    }

    # Example track info
    example_track = {
        "title": "Midnight Drive",
        "mood": "melancholic, dark",
        "tempo": "medium",
        "audience_emotion": "crying in the car, night drive vibes",
    }

    # Generate a video prompt
    result = generator.generate_video_prompt(example_artist, example_track, "tiktok")

    # Print the result
    print("VIDEO PROMPT:")
    print(result["prompt"])

    # Generate a transition prompt
    transition_result = generator.generate_transition_prompt(
        example_artist, example_track
    )

    # Print the transition prompt
    print("\nTRANSITION PROMPT:")
    print(transition_result["prompt"])
