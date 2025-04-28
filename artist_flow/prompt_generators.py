"""
Specialized prompt generation module for different artist aspects.

This module provides prompt generation capabilities for various aspects of artist creation,
including music creation, visual identity, and artist backstory enhancement.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prompt_generators")


class MusicPromptGenerator:
    """
    Generates prompts for music creation based on artist profile.

    This class creates specialized prompts that can be used with music generation
    systems to create tracks that match the artist's style and genre.
    """

    def __init__(self, template_variety: int = 3):
        """
        Initialize the music prompt generator.

        Args:
            template_variety: Number of template variations to use
        """
        self.template_variety = template_variety
        logger.info("Initialized MusicPromptGenerator")

    def generate_track_prompt(
        self,
        artist_profile: Dict[str, Any],
        track_type: str = "main",
        duration_seconds: int = 180,
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating a music track.

        Args:
            artist_profile: The artist profile containing genre, style, etc.
            track_type: Type of track (main, intro, outro, etc.)
            duration_seconds: Desired track duration in seconds

        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(
            f"Generating {track_type} track prompt for artist {artist_profile.get('name', 'Unknown')}"
        )

        # This is a stub - would be replaced with actual implementation
        # that generates appropriate prompts based on the artist profile

        # Mock implementation for structure
        return {
            "prompt": f"Create a {artist_profile.get('genre', 'Unknown')} track with {artist_profile.get('style', 'Unknown')} vibes",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "duration_seconds": duration_seconds,
                "track_type": track_type,
            },
            "system_instructions": "The track should match the artist's unique style and sound signature.",
        }

    def generate_album_concept(
        self, artist_profile: Dict[str, Any], track_count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a concept for an entire album including track list.

        Args:
            artist_profile: The artist profile containing genre, style, etc.
            track_count: Number of tracks to include in the album

        Returns:
            Dictionary containing the album concept and track prompts
        """
        logger.info(
            f"Generating album concept for artist {artist_profile.get('name', 'Unknown')}"
        )

        # This is a stub - would be replaced with actual implementation

        # Mock implementation for structure
        tracks = []
        for i in range(track_count):
            tracks.append(
                {
                    "title": f"Track {i+1}",
                    "prompt": f"Create a {artist_profile.get('genre', 'Unknown')} track number {i+1} for the album",
                    "duration_seconds": 180 + (i * 30),  # Varying durations
                }
            )

        return {
            "album_title": "Album Title",
            "concept": "Album concept description",
            "tracks": tracks,
            "total_duration_minutes": sum(t["duration_seconds"] for t in tracks) // 60,
        }


class VisualPromptGenerator:
    """
    Generates prompts for visual asset creation based on artist profile.

    This class creates specialized prompts that can be used with image generation
    systems to create visual assets that match the artist's identity.
    """

    def __init__(self):
        """Initialize the visual prompt generator."""
        logger.info("Initialized VisualPromptGenerator")

    def generate_profile_image_prompt(
        self, artist_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating an artist profile image.

        Args:
            artist_profile: The artist profile containing style, appearance, etc.

        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(
            f"Generating profile image prompt for artist {artist_profile.get('name', 'Unknown')}"
        )

        # This is a stub - would be replaced with actual implementation

        # Mock implementation for structure
        return {
            "prompt": f"Create a profile image for a {artist_profile.get('genre', 'Unknown')} artist with {artist_profile.get('style', 'Unknown')} aesthetic",
            "parameters": {
                "style": artist_profile.get("style", "Unknown"),
                "appearance": artist_profile.get("appearance", "Unknown"),
                "mood": "professional, artistic",
                "format": "portrait",
            },
            "negative_prompt": "low quality, blurry, distorted",
        }

    def generate_album_cover_prompt(
        self,
        artist_profile: Dict[str, Any],
        album_concept: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating an album cover.

        Args:
            artist_profile: The artist profile containing style, genre, etc.
            album_concept: Optional album concept information

        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(
            f"Generating album cover prompt for artist {artist_profile.get('name', 'Unknown')}"
        )

        # This is a stub - would be replaced with actual implementation

        # Mock implementation for structure
        album_title = (
            album_concept.get("album_title", "Untitled Album")
            if album_concept
            else "Untitled Album"
        )

        return {
            "prompt": f"Create an album cover for '{album_title}' by {artist_profile.get('name', 'Unknown')}, a {artist_profile.get('genre', 'Unknown')} artist",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "title": album_title,
                "format": "square, high resolution",
            },
            "negative_prompt": "text, words, low quality, blurry",
        }


class BackstoryPromptGenerator:
    """
    Generates prompts for enhancing artist backstory and personality.

    This class creates specialized prompts that can be used to develop
    rich backstories and personalities for artists.
    """

    def __init__(self):
        """Initialize the backstory prompt generator."""
        logger.info("Initialized BackstoryPromptGenerator")

    def generate_backstory_prompt(
        self, artist_profile: Dict[str, Any], depth: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating or enhancing an artist backstory.

        Args:
            artist_profile: The artist profile containing basic information
            depth: Level of detail for the backstory (brief, detailed, comprehensive)

        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(
            f"Generating {depth} backstory prompt for artist {artist_profile.get('name', 'Unknown')}"
        )

        # This is a stub - would be replaced with actual implementation

        # Mock implementation for structure
        return {
            "prompt": f"Create a {depth} backstory for {artist_profile.get('name', 'Unknown')}, a {artist_profile.get('genre', 'Unknown')} artist",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "depth": depth,
                "focus_areas": ["origin", "influences", "journey", "philosophy"],
            },
            "system_instructions": "Create a compelling and authentic backstory that aligns with the artist's musical style and genre.",
        }

    def generate_social_media_persona_prompt(
        self, artist_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a prompt for creating a social media persona for the artist.

        Args:
            artist_profile: The artist profile containing style, genre, etc.

        Returns:
            Dictionary containing the prompt and metadata
        """
        logger.info(
            f"Generating social media persona prompt for artist {artist_profile.get('name', 'Unknown')}"
        )

        # This is a stub - would be replaced with actual implementation

        # Mock implementation for structure
        return {
            "prompt": f"Create a social media persona for {artist_profile.get('name', 'Unknown')}, a {artist_profile.get('genre', 'Unknown')} artist",
            "parameters": {
                "genre": artist_profile.get("genre", "Unknown"),
                "style": artist_profile.get("style", "Unknown"),
                "platforms": ["Instagram", "Twitter", "TikTok"],
                "tone": "authentic, engaging, mysterious",
            },
            "system_instructions": "Create a consistent and engaging social media persona that will resonate with fans of the genre.",
        }


# Factory function to get appropriate prompt generator
def get_prompt_generator(generator_type: str) -> Any:
    """
    Factory function to get the appropriate prompt generator.

    Args:
        generator_type: Type of generator to return (music, visual, backstory)

    Returns:
        Instance of the requested generator
    """
    generators = {
        "music": MusicPromptGenerator(),
        "visual": VisualPromptGenerator(),
        "backstory": BackstoryPromptGenerator(),
    }

    return generators.get(generator_type.lower(), MusicPromptGenerator())


# Helper functions for prompt generation
def _extract_genre_elements(genre: str) -> Dict[str, Any]:
    """
    Extract key musical and stylistic elements associated with a genre.

    Args:
        genre: Music genre name

    Returns:
        Dictionary of genre elements
    """
    # Genre-specific elements dictionary
    genre_elements = {
        "trap": {
            "instruments": ["808 bass", "hi-hats", "snares", "synthesizers"],
            "tempo_range": (120, 160),
            "themes": ["street life", "ambition", "struggle", "success"],
            "mood": ["dark", "atmospheric", "intense", "moody"],
            "production": ["heavy bass", "layered beats", "vocal effects"],
        },
        "dark trap": {
            "instruments": [
                "distorted 808s",
                "atmospheric pads",
                "minor keys",
                "deep bass",
            ],
            "tempo_range": (110, 150),
            "themes": ["darkness", "inner demons", "night life", "isolation"],
            "mood": ["ominous", "mysterious", "haunting", "melancholic"],
            "production": ["reverb", "echo", "distortion", "ambient sounds"],
        },
        "phonk": {
            "instruments": [
                "cowbell",
                "memphis drums",
                "vinyl crackle",
                "pitched vocals",
            ],
            "tempo_range": (130, 160),
            "themes": ["nostalgia", "retro", "driving", "night cruising"],
            "mood": ["eerie", "energetic", "hypnotic", "aggressive"],
            "production": ["chopped samples", "lo-fi elements", "heavy sidechaining"],
        },
        "lofi": {
            "instruments": [
                "mellow piano",
                "jazz samples",
                "vinyl crackle",
                "soft drums",
            ],
            "tempo_range": (70, 90),
            "themes": ["relaxation", "study", "nostalgia", "introspection"],
            "mood": ["calm", "melancholic", "peaceful", "warm"],
            "production": ["sample-based", "vinyl effects", "subtle imperfections"],
        },
        "edm": {
            "instruments": ["synthesizers", "drum machines", "vocal chops", "risers"],
            "tempo_range": (120, 150),
            "themes": ["celebration", "energy", "euphoria", "freedom"],
            "mood": ["uplifting", "energetic", "exciting", "positive"],
            "production": ["drops", "buildups", "layered synths", "clean mixing"],
        },
        "hip hop": {
            "instruments": ["drum breaks", "samples", "bass lines", "scratching"],
            "tempo_range": (85, 110),
            "themes": [
                "urban life",
                "social commentary",
                "personal growth",
                "storytelling",
            ],
            "mood": ["confident", "reflective", "assertive", "authentic"],
            "production": ["sample-based", "boom bap", "layered vocals"],
        },
        "ambient": {
            "instruments": [
                "synthesizer pads",
                "field recordings",
                "processed sounds",
                "drones",
            ],
            "tempo_range": (60, 80),
            "themes": ["nature", "space", "meditation", "transcendence"],
            "mood": ["atmospheric", "ethereal", "spacious", "contemplative"],
            "production": ["reverb", "delay", "textural layers", "minimal percussion"],
        },
    }

    # Normalize genre name for lookup
    normalized_genre = genre.lower()

    # Check for multi-word genres first
    if normalized_genre in genre_elements:
        return genre_elements[normalized_genre]

    # Try to match single words if full genre not found
    for key in genre_elements:
        if key in normalized_genre:
            return genre_elements[key]

    # Default elements if genre not recognized
    return {
        "instruments": ["synthesizers", "drums", "bass", "vocals"],
        "tempo_range": (90, 130),
        "themes": ["expression", "emotion", "experience", "storytelling"],
        "mood": ["expressive", "emotive", "atmospheric"],
        "production": ["professional", "balanced", "clear"],
    }


def _extract_visual_elements(style: str) -> Dict[str, Any]:
    """
    Extract key visual elements associated with an artist style.

    Args:
        style: Artist style description

    Returns:
        Dictionary of visual elements
    """
    # Common visual styles
    visual_elements = {
        "mysterious": {
            "colors": ["dark blue", "purple", "black", "silver"],
            "imagery": ["shadows", "fog", "silhouettes", "hidden faces"],
            "composition": ["asymmetrical", "obscured", "dramatic lighting"],
            "textures": ["smoky", "misty", "velvet", "metallic"],
        },
        "cold": {
            "colors": ["ice blue", "white", "silver", "pale gray"],
            "imagery": ["frost", "minimalist", "geometric", "sharp edges"],
            "composition": ["sparse", "clean lines", "negative space"],
            "textures": ["icy", "smooth", "glass-like", "crystalline"],
        },
        "energetic": {
            "colors": ["bright red", "electric blue", "neon yellow", "orange"],
            "imagery": ["motion blur", "dynamic shapes", "action", "light streaks"],
            "composition": ["diagonal lines", "asymmetry", "movement"],
            "textures": ["glossy", "vibrant", "electric", "sharp"],
        },
        "nostalgic": {
            "colors": ["sepia", "faded blue", "muted red", "cream"],
            "imagery": [
                "vintage objects",
                "film grain",
                "old photographs",
                "retro tech",
            ],
            "composition": ["centered", "framed", "symmetrical"],
            "textures": ["worn", "grainy", "paper", "aged"],
        },
        "futuristic": {
            "colors": ["neon blue", "purple", "black", "electric green"],
            "imagery": ["technology", "glitches", "holograms", "geometric patterns"],
            "composition": ["grid-based", "floating elements", "perspective"],
            "textures": ["glossy", "metallic", "digital", "glowing"],
        },
        "organic": {
            "colors": ["earth tones", "forest green", "terracotta", "natural blue"],
            "imagery": ["plants", "natural elements", "flowing forms", "handmade"],
            "composition": ["flowing", "natural balance", "asymmetrical"],
            "textures": ["rough", "tactile", "natural", "handcrafted"],
        },
    }

    # Extract style keywords
    style_keywords = [word.strip().lower() for word in style.split(",")]

    # Collect elements from matching styles
    combined_elements = {"colors": [], "imagery": [], "composition": [], "textures": []}

    matches_found = False

    # Look for direct matches
    for keyword in style_keywords:
        if keyword in visual_elements:
            matches_found = True
            for category in combined_elements:
                combined_elements[category].extend(visual_elements[keyword][category])

    # If no direct matches, look for partial matches
    if not matches_found:
        for keyword in style_keywords:
            for style_name, elements in visual_elements.items():
                if keyword in style_name or style_name in keyword:
                    for category in combined_elements:
                        combined_elements[category].extend(elements[category])

    # If still no matches, use default elements
    if not any(combined_elements.values()):
        return {
            "colors": ["black", "white", "primary colors", "contrasting tones"],
            "imagery": ["abstract shapes", "symbolic elements", "representative icons"],
            "composition": ["balanced", "focused", "intentional"],
            "textures": ["mixed", "appropriate to genre", "distinctive"],
        }

    # Remove duplicates while preserving order
    for category in combined_elements:
        seen = set()
        combined_elements[category] = [
            x for x in combined_elements[category] if not (x in seen or seen.add(x))
        ]

    return combined_elements


def generate_artist_profile_prompt(artist_brief: Dict[str, Any]) -> str:
    """
    Generate a detailed prompt to create a full artist profile based on the input brief.

    This function creates a comprehensive prompt for an LLM to develop a complete
    artist profile, including personality traits, musical style, inspirations,
    target audience, and emotional tone.

    Args:
        artist_brief: Dictionary containing basic artist information such as:
            - style: Artist's stylistic description (e.g., "Mysterious, Cold")
            - genre: Musical genre (e.g., "Dark Trap", "Phonk")
            - atmosphere: Overall mood/atmosphere (e.g., "Nocturnal, Urban")
            - vibe: General feeling/vibe (e.g., "Introspective, Intense")

    Returns:
        A detailed text prompt for creating a full artist profile
    """
    logger.info(
        f"Generating artist profile prompt for genre: {artist_brief.get('genre', 'Unknown')}"
    )

    # Extract key elements from the brief
    genre = artist_brief.get("genre", "Electronic")
    style = artist_brief.get("style", "Unique, Distinctive")
    atmosphere = artist_brief.get("atmosphere", "Immersive")
    vibe = artist_brief.get("vibe", "Authentic")

    # Get genre-specific elements
    genre_elements = _extract_genre_elements(genre)

    # Randomly select themes and moods for variety
    themes = random.sample(
        genre_elements["themes"], min(2, len(genre_elements["themes"]))
    )
    moods = random.sample(genre_elements["mood"], min(2, len(genre_elements["mood"])))

    # Build the prompt
    prompt = f"""Create a detailed profile for a new {genre} music artist with a {style} style. 

The artist should embody a {atmosphere} atmosphere and a {vibe} vibe. Develop a complete artist identity including:

1. Artist Name: Create a unique, memorable name that reflects the {genre} genre and {style} style.

2. Musical Identity:
   - Primary genre: {genre}
   - Sub-genres or influences: Select appropriate sub-genres that complement the main style
   - Signature sound: Describe distinctive elements like {', '.join(random.sample(genre_elements["instruments"], min(2, len(genre_elements["instruments"]))))}
   - Production style: {', '.join(random.sample(genre_elements["production"], min(2, len(genre_elements["production"]))))}
   - Vocal style (if applicable): How their voice or vocal processing sounds

3. Visual Identity:
   - Overall aesthetic: {style} with {atmosphere} elements
   - Color palette: Colors that represent their brand
   - Visual motifs: Recurring symbols or imagery
   - Performance style: How they present themselves in performances or videos

4. Artist Backstory:
   - Origin story: Where they came from and how they started
   - Influences: Artists or experiences that shaped their sound
   - Philosophy: Their approach to music and creative vision
   - Narrative: Any storyline or concept behind their music

5. Target Audience:
   - Primary demographic: Who would most connect with this music
   - Listener experience: How the music makes listeners feel ({', '.join(moods)})
   - Contexts: When and where people would listen to this music

6. Thematic Elements:
   - Lyrical themes: Common subjects like {', '.join(themes)}
   - Emotional tone: The feelings the music evokes
   - Messaging: Any underlying messages or purpose

7. Career Trajectory:
   - Current status: Emerging, established, underground, etc.
   - Goals: Where they're headed artistically
   - Unique selling points: What makes them stand out in the {genre} scene

Make the profile cohesive, authentic, and distinctive within the {genre} genre while maintaining the {style} style throughout. Ensure all elements work together to create a compelling and marketable artist identity.
"""

    return prompt


def generate_song_prompt(artist_profile: Dict[str, Any]) -> str:
    """
    Generate a detailed prompt for the LLM to write a new song for the artist.

    This function creates a comprehensive prompt for song creation that aligns
    with the artist's established style, genre, and thematic elements.

    Args:
        artist_profile: Dictionary containing the artist's profile information including:
            - name: Artist name
            - genre: Musical genre
            - style: Artistic style
            - themes: Thematic elements
            - sound: Sound characteristics

    Returns:
        A detailed text prompt for creating a song for the artist
    """
    logger.info(
        f"Generating song prompt for artist: {artist_profile.get('name', 'Unknown')}"
    )

    # Extract key elements from the profile
    artist_name = artist_profile.get("name", "Artist")
    genre = artist_profile.get("genre", "Electronic")
    style = artist_profile.get("style", "Unique")

    # Get additional elements from profile if available
    themes = artist_profile.get("themes", [])
    if not themes and "thematic_elements" in artist_profile:
        themes = artist_profile.get("thematic_elements", {}).get("lyrical_themes", [])

    sound = artist_profile.get("sound", {})
    if not sound and "musical_identity" in artist_profile:
        sound = artist_profile.get("musical_identity", {}).get("signature_sound", "")

    # Get genre-specific elements
    genre_elements = _extract_genre_elements(genre)

    # Select random elements for variety
    if not themes or len(themes) == 0:
        themes = genre_elements["themes"]
    selected_themes = random.sample(
        themes if isinstance(themes, list) else [themes],
        min(2, len(themes) if isinstance(themes, list) else 1),
    )

    mood_options = genre_elements["mood"]
    selected_mood = random.sample(mood_options, min(2, len(mood_options)))

    # Determine tempo range based on genre
    tempo_range = genre_elements["tempo_range"]
    suggested_tempo = random.randint(tempo_range[0], tempo_range[1])

    # Build the prompt
    prompt = f"""Write a complete song for {artist_name}, a {genre} artist with a {style} style.

Song Requirements:
1. Structure: Create a full song with verse(s), chorus, and optionally a bridge or breakdown
2. Genre: {genre}
3. Mood: {', '.join(selected_mood)}
4. Themes: Focus on {', '.join(selected_themes)}
5. Tempo: Approximately {suggested_tempo} BPM
6. Lyrical Style: Match the artist's established voice and perspective

Musical Elements to Include:
- Instrumentation: Feature {', '.join(random.sample(genre_elements["instruments"], min(3, len(genre_elements["instruments"]))))}
- Production Notes: Include {', '.join(random.sample(genre_elements["production"], min(2, len(genre_elements["production"]))))}
- Sound Characteristics: {sound if isinstance(sound, str) else ', '.join(sound) if isinstance(sound, list) else 'Signature sound elements'}

Special Directions:
- Create a memorable hook/chorus that captures the essence of {artist_name}'s style
- Include at least one standout lyrical moment that could be quoted or featured
- Ensure the song has a natural flow and progression
- Consider dynamics between sections (intensity, energy levels)
- Make the lyrics authentic to the {genre} genre while avoiding clichés

The song should feel like a natural extension of {artist_name}'s catalog while bringing something fresh to their sound. It should resonate emotionally with listeners and showcase what makes this artist unique in the {genre} scene.
"""

    return prompt


def generate_profile_cover_prompt(artist_profile: Dict[str, Any]) -> str:
    """
    Generate a prompt for creating an AI-generated profile picture or avatar.

    This function creates a detailed prompt for generating a visual representation
    of the artist that reflects their branding without showing a real human face.

    Args:
        artist_profile: Dictionary containing the artist's profile information including:
            - name: Artist name
            - genre: Musical genre
            - style: Artistic style
            - visual_identity: Visual branding elements

    Returns:
        A detailed text prompt for creating an artist profile image
    """
    logger.info(
        f"Generating profile cover prompt for artist: {artist_profile.get('name', 'Unknown')}"
    )

    # Extract key elements from the profile
    artist_name = artist_profile.get("name", "Artist")
    genre = artist_profile.get("genre", "Electronic")
    style = artist_profile.get("style", "Unique")

    # Get visual identity elements if available
    visual_identity = artist_profile.get("visual_identity", {})
    if isinstance(visual_identity, str):
        visual_identity = {"aesthetic": visual_identity}

    aesthetic = visual_identity.get("aesthetic", style)
    color_palette = visual_identity.get("color_palette", [])
    visual_motifs = visual_identity.get("visual_motifs", [])

    # Extract visual elements based on style
    visual_elements = _extract_visual_elements(style)

    # Use provided color palette or default to extracted colors
    if not color_palette or len(color_palette) == 0:
        color_palette = visual_elements["colors"]

    if isinstance(color_palette, str):
        color_palette = [color_palette]

    # Use provided visual motifs or default to extracted imagery
    if not visual_motifs or len(visual_motifs) == 0:
        visual_motifs = visual_elements["imagery"]

    if isinstance(visual_motifs, str):
        visual_motifs = [visual_motifs]

    # Select composition and texture elements
    composition = random.sample(
        visual_elements["composition"], min(2, len(visual_elements["composition"]))
    )
    textures = random.sample(
        visual_elements["textures"], min(2, len(visual_elements["textures"]))
    )

    # Build the prompt
    prompt = f"""Create a striking profile image for {artist_name}, a {genre} music artist with a {aesthetic} aesthetic.

Key Visual Elements:
1. Style: {style} with a {', '.join(composition)} composition
2. Color Palette: Prominently feature {', '.join(random.sample(color_palette, min(3, len(color_palette))))}
3. Visual Motifs: Include elements like {', '.join(random.sample(visual_motifs, min(2, len(visual_motifs))))}
4. Textures: Incorporate {', '.join(textures)} textures
5. Mood: Convey a {genre}-appropriate atmosphere

Important Requirements:
- DO NOT show a realistic human face or portrait
- Instead, represent the artist through stylized, abstract, or symbolic imagery
- The image should be instantly recognizable as a {genre} artist's profile
- Create a distinctive visual identity that stands out in thumbnails and small formats
- Ensure the image reflects the artist's musical style and brand identity

Artistic Approach:
- Use {random.choice(["dramatic lighting", "bold contrasts", "subtle gradients", "striking silhouettes"])}
- Incorporate {random.choice(["digital elements", "analog/vintage effects", "mixed media aesthetics", "minimalist design"])}
- Consider the image will be used across music platforms and social media
- Create something that would look compelling as an artist profile on streaming services

The final image should be visually striking, genre-appropriate, and instantly communicate the essence of {artist_name}'s musical identity without relying on photorealistic human representation.
"""

    return prompt


def generate_track_cover_prompt(artist_profile: Dict[str, Any], song_theme: str) -> str:
    """
    Generate a prompt to create the cover art for a specific song.

    This function creates a detailed prompt for generating cover artwork that
    reflects both the artist's visual identity and the specific song's theme.

    Args:
        artist_profile: Dictionary containing the artist's profile information
        song_theme: String describing the theme or mood of the specific song

    Returns:
        A detailed text prompt for creating song cover artwork
    """
    logger.info(
        f"Generating track cover prompt for artist: {artist_profile.get('name', 'Unknown')}"
    )

    # Extract key elements from the profile
    artist_name = artist_profile.get("name", "Artist")
    genre = artist_profile.get("genre", "Electronic")
    style = artist_profile.get("style", "Unique")

    # Get visual identity elements if available
    visual_identity = artist_profile.get("visual_identity", {})
    if isinstance(visual_identity, str):
        visual_identity = {"aesthetic": visual_identity}

    aesthetic = visual_identity.get("aesthetic", style)
    color_palette = visual_identity.get("color_palette", [])

    # Extract visual elements based on style
    visual_elements = _extract_visual_elements(style)

    # Use provided color palette or default to extracted colors
    if not color_palette or len(color_palette) == 0:
        color_palette = visual_elements["colors"]

    if isinstance(color_palette, str):
        color_palette = [color_palette]

    # Extract mood from song theme
    theme_words = song_theme.lower().split()
    mood_indicators = [
        "dark",
        "light",
        "energetic",
        "calm",
        "aggressive",
        "peaceful",
        "melancholic",
        "uplifting",
        "nostalgic",
        "futuristic",
        "mysterious",
    ]

    detected_moods = [word for word in theme_words if word in mood_indicators]
    if detected_moods:
        mood = detected_moods[0]
    else:
        # Default mood based on genre
        genre_elements = _extract_genre_elements(genre)
        mood = random.choice(genre_elements["mood"])

    # Build the prompt
    prompt = f"""Create a captivating cover artwork for a {genre} track titled "{song_theme}" by {artist_name}.

Artwork Requirements:
1. Style: Maintain {artist_name}'s {aesthetic} aesthetic while specifically reflecting the song theme: "{song_theme}"
2. Color Palette: Use {', '.join(random.sample(color_palette, min(3, len(color_palette))))} with emphasis on colors that evoke the song's mood
3. Composition: Create a {random.choice(["square", "square", "square"])} format suitable for music platforms
4. Mood: Convey a {mood} atmosphere that matches the song's theme

Visual Elements to Include:
- Incorporate imagery that represents "{song_theme}" in a {genre}-appropriate way
- Use {random.choice(visual_elements["textures"])} textures to add depth
- Include subtle visual references to the song's lyrical content
- Balance artistic expression with genre expectations

Technical Specifications:
- Design for a square format (1:1 ratio)
- Ensure the image is clear and impactful even at thumbnail size
- Create a cohesive look with the artist's other releases while making this cover distinctive
- Consider how text might be incorporated (though don't include text in the image itself)

The artwork should instantly communicate the emotional essence of "{song_theme}" while maintaining {artist_name}'s established visual identity. It should stand out in music platform browsing contexts while feeling like a natural extension of the artist's catalog.
"""

    return prompt


# Example usage
if __name__ == "__main__":
    # Example artist brief
    example_brief = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "atmosphere": "Nocturnal, Urban",
        "vibe": "Introspective, Intense",
    }

    # Example artist profile
    example_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "visual_identity": {
            "aesthetic": "Nocturnal, Urban",
            "color_palette": ["midnight blue", "silver", "deep purple", "black"],
            "visual_motifs": ["shadows", "city skylines", "masks", "reflections"],
        },
        "themes": ["isolation", "night life", "inner demons", "urban decay"],
    }

    # Generate and print example prompts
    print("\nARTIST PROFILE PROMPT:")
    print(generate_artist_profile_prompt(example_brief))

    print("\nSONG PROMPT:")
    print(generate_song_prompt(example_profile))

    print("\nPROFILE COVER PROMPT:")
    print(generate_profile_cover_prompt(example_profile))

    print("\nTRACK COVER PROMPT:")
    print(generate_track_cover_prompt(example_profile, "Midnight Shadows"))
