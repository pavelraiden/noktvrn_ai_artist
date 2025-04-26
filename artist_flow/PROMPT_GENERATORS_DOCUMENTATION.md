# Prompt Generators Implementation Documentation

## Overview
This document provides detailed information about the implementation of real prompt generation functions in the Artist Creation Flow. These functions generate detailed prompts for various aspects of the artist creation process, including artist profiles, songs, and visual assets.

## Implemented Functions

### 1. `generate_artist_profile_prompt(artist_brief: dict) -> str`

**Purpose:**  
Generates a detailed prompt to create a full artist profile based on the input brief.

**Implementation Details:**
- Takes an artist brief with style, genre, atmosphere, and vibe parameters
- Extracts genre-specific elements using the `_extract_genre_elements` helper function
- Builds a comprehensive prompt with sections for:
  - Artist name creation
  - Musical identity (genre, sub-genres, signature sound)
  - Visual identity (aesthetic, color palette, visual motifs)
  - Artist backstory (origin, influences, philosophy)
  - Target audience and thematic elements
  - Career trajectory
- Includes randomization for variety in generated prompts
- Returns a clean text prompt as a string

**Example Input:**
```python
artist_brief = {
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "atmosphere": "Nocturnal, Urban",
    "vibe": "Introspective, Intense"
}
```

### 2. `generate_song_prompt(artist_profile: dict) -> str`

**Purpose:**  
Generates a detailed prompt for the LLM to write a new song for the artist.

**Implementation Details:**
- Takes an artist profile with name, genre, style, themes, and sound parameters
- Extracts genre-specific elements using the `_extract_genre_elements` helper function
- Handles both flat and nested profile structures
- Builds a comprehensive prompt with sections for:
  - Song structure requirements
  - Genre, mood, and themes
  - Tempo and musical elements
  - Instrumentation and production notes
  - Special directions for lyrics and composition
- Includes genre-appropriate tempo ranges and instrumentation
- Returns a clean text prompt as a string

**Example Input:**
```python
artist_profile = {
    "name": "NightShade",
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "themes": ["isolation", "night life", "inner demons"]
}
```

### 3. `generate_profile_cover_prompt(artist_profile: dict) -> str`

**Purpose:**  
Generates a prompt for creating an AI-generated profile picture or avatar based on the artist's style and story.

**Implementation Details:**
- Takes an artist profile with name, genre, style, and visual identity parameters
- Extracts visual elements using the `_extract_visual_elements` helper function
- Handles both structured visual identity objects and string descriptions
- Builds a comprehensive prompt with sections for:
  - Key visual elements (style, color palette, motifs, textures)
  - Important requirements (avoiding realistic human faces)
  - Artistic approach for the image
- Ensures the prompt specifies non-human representation
- Returns a clean text prompt as a string

**Example Input:**
```python
artist_profile = {
    "name": "NightShade",
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "visual_identity": {
        "aesthetic": "Nocturnal, Urban",
        "color_palette": ["midnight blue", "silver", "deep purple"]
    }
}
```

### 4. `generate_track_cover_prompt(artist_profile: dict, song_theme: str) -> str`

**Purpose:**  
Generates a prompt to create the cover art for a specific song that reflects the emotion and visual aesthetics of the song.

**Implementation Details:**
- Takes an artist profile and a song theme string
- Extracts visual elements using the `_extract_visual_elements` helper function
- Analyzes the song theme to detect mood indicators
- Builds a comprehensive prompt with sections for:
  - Artwork requirements (style, color palette, composition, mood)
  - Visual elements to include
  - Technical specifications for music platforms
- Ensures the artwork reflects both the artist's identity and the specific song
- Returns a clean text prompt as a string

**Example Input:**
```python
artist_profile = {
    "name": "NightShade",
    "genre": "Dark Trap",
    "style": "Mysterious, Cold"
}
song_theme = "Midnight Shadows"
```

## Helper Functions

### 1. `_extract_genre_elements(genre: str) -> Dict[str, Any]`

**Purpose:**  
Extract key musical and stylistic elements associated with a genre.

**Implementation Details:**
- Contains a dictionary of genre-specific elements for common genres
- Each genre includes instruments, tempo range, themes, mood, and production elements
- Handles multi-word genres and partial matches
- Provides sensible defaults for unrecognized genres

### 2. `_extract_visual_elements(style: str) -> Dict[str, Any]`

**Purpose:**  
Extract key visual elements associated with an artist style.

**Implementation Details:**
- Contains a dictionary of visual styles with associated elements
- Each style includes colors, imagery, composition, and textures
- Parses comma-separated style descriptions
- Combines elements from multiple matching styles
- Provides sensible defaults for unrecognized styles

## Testing

A comprehensive test suite was implemented in `test_prompt_generators.py` that:
- Tests all four main functions with various input scenarios
- Verifies correct handling of complete profiles, minimal profiles, and edge cases
- Ensures prompts contain required elements and meet length requirements
- Confirms proper handling of different data structures (nested objects, strings, etc.)

All tests pass successfully, confirming the implementation meets requirements.

## Integration

The new functions integrate seamlessly with the existing class-based structure in `prompt_generators.py`. They are implemented as standalone functions at the module level, making them easy to import and use in the artist creation flow.

## Future Enhancements

Potential future enhancements could include:
- Expanding the genre and style dictionaries with more specialized elements
- Adding more sophisticated prompt templates for different use cases
- Implementing language model-based enhancement of the generated prompts
- Adding support for more specific visual styles and musical genres
