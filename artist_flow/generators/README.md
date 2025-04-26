# Artist Prompt Generator

This module provides a comprehensive system for generating detailed prompts for AI artist creation based on user-defined parameters. It creates rich, detailed prompts suitable for multi-agent communication between LLMs in the artist creation process.

## Overview

The Artist Prompt Generator creates prompts that cover all aspects of an artist's identity:

- Artist name
- Artist style and mood
- Preferred genres
- Persona traits (e.g., mysterious, energetic, soft)
- Target audience
- Visual identity hints
- Language for lyrics
- Themes or values represented
- Lifestyle/attitude hints
- Special notes for AI enhancement

## Usage

### Basic Usage

```python
from artist_flow.generators.artist_prompt_generator import generate_artist_prompt

# Define artist parameters
params = {
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "persona": "mysterious, energetic",
    "target_audience": "Young adults, night owls",
    "visual_identity": "Always wears a black hood and mask",
    "lyrics_language": "English",
    "themes": "Urban isolation, night life, inner struggles",
    "lifestyle": "Urban night life, digital nomad",
    "special_notes": "Should have a distinctive vocal processing effect"
}

# Generate a comprehensive artist prompt
result = generate_artist_prompt(params)

# Access the generated prompt
prompt = result["prompt"]
print(prompt)

# Access metadata
metadata = result["metadata"]
```

### Advanced Usage

For more control, you can create an instance of the `ArtistPromptGenerator` class:

```python
from artist_flow.generators.artist_prompt_generator import ArtistPromptGenerator

# Create a generator with a specific seed for reproducible results
generator = ArtistPromptGenerator(template_variety=3, seed=42)

# Generate a full artist prompt
artist_prompt = generator.generate_artist_prompt(params)

# Generate a focused prompt for artist name creation
name_prompt = generator.generate_artist_name_prompt(params)

# Generate a focused prompt for visual identity creation
visual_prompt = generator.generate_visual_identity_prompt(params)

# Generate a focused prompt for artist backstory creation
backstory_prompt = generator.generate_backstory_prompt(params)
```

## Customization

### Environment Variables

The module supports customization through environment variables:

- `ARTIST_GENRE_DB_PATH`: Path to a custom JSON file with genre definitions
- `ARTIST_VISUAL_DB_PATH`: Path to a custom JSON file with visual style definitions

Example `.env` file:
```
ARTIST_GENRE_DB_PATH=/path/to/custom_genres.json
ARTIST_VISUAL_DB_PATH=/path/to/custom_visuals.json
```

### Custom Genre and Visual Databases

You can extend the built-in genre and visual style databases by providing custom JSON files. The format should match the internal structure:

```json
{
  "new_genre": {
    "instruments": ["instrument1", "instrument2"],
    "tempo_range": [100, 130],
    "themes": ["theme1", "theme2"],
    "mood": ["mood1", "mood2"],
    "production": ["technique1", "technique2"],
    "audience": ["audience1", "audience2"],
    "visual_aesthetic": ["aesthetic1", "aesthetic2"]
  }
}
```

## Integration

This module is designed to integrate with the broader artist creation flow:

1. Generate artist prompts using this module
2. Pass prompts to LLM orchestration systems
3. Process LLM responses to create artist profiles
4. Use the profiles to generate music, visuals, and other assets

## Requirements

- Python 3.7+
- dotenv (optional, for environment variable loading)

## License

This module is part of the Artist Creation System and follows the project's licensing terms.
