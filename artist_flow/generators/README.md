# AI Artist Generators

This directory contains modules for generating detailed prompts for various aspects of AI artist creation. These modules create rich, detailed prompts suitable for multi-agent communication between LLMs in the artist creation process.

## Modules

### Artist Prompt Generator

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

### Track Prompt Generator

The Track Prompt Generator creates prompts for AI-written songs based on an artist's style, mood, and audience. It covers:

- Desired song mood and emotion (e.g., "melancholic nostalgia")
- Tempo (slow, medium, fast)
- Genre and subgenres (e.g., "Phonk", "Dark Trap", "Retro synthwave")
- Special lyrical themes (e.g., love, street life, mental struggles)
- Key musical cues (e.g., strong bass, emotional hook, melodic chorus)
- Indication of where drops, transitions, and bass-heavy sections should appear
- Language for the lyrics
- Target audience emotion to trigger (e.g., "crying in the car", "dancing at night")
- Stylistic notes (e.g., "make it feel like early 2000s mixtape style")

## Usage

### Artist Prompt Generator

#### Basic Usage

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

#### Advanced Usage

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

### Track Prompt Generator

#### Basic Usage

```python
from artist_flow.generators.track_prompt_generator import generate_track_prompt

# Define artist profile
artist_profile = {
    "name": "NightShade",
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "themes": "Urban isolation, night life, inner struggles",
    "lyrics_language": "English"
}

# Optional overrides for this specific track
overrides = {
    "mood": "melancholic, dark",
    "tempo": "medium",
    "audience_emotion": "crying in the car, night drive vibes",
    "stylistic_notes": "Should have a nostalgic quality reminiscent of early 2000s mixtape style"
}

# Generate a comprehensive track prompt
result = generate_track_prompt(artist_profile, overrides)

# Access the generated prompt
prompt = result["prompt"]
print(prompt)

# Access metadata
metadata = result["metadata"]
```

#### Advanced Usage

For more control, you can create an instance of the `TrackPromptGenerator` class:

```python
from artist_flow.generators.track_prompt_generator import TrackPromptGenerator

# Create a generator with a specific seed for reproducible results
generator = TrackPromptGenerator(template_variety=3, seed=42)

# Generate a full track prompt
track_prompt = generator.generate_track_prompt(artist_profile, overrides)

# Generate a focused prompt for lyrics creation
lyrics_prompt = generator.generate_lyrics_prompt(artist_profile, overrides)

# Generate a focused prompt for melody creation
melody_prompt = generator.generate_melody_prompt(artist_profile, overrides)
```

## Customization

### Environment Variables

The modules support customization through environment variables:

#### Artist Prompt Generator
- `ARTIST_GENRE_DB_PATH`: Path to a custom JSON file with genre definitions
- `ARTIST_VISUAL_DB_PATH`: Path to a custom JSON file with visual style definitions

#### Track Prompt Generator
- `TRACK_GENRE_DB_PATH`: Path to a custom JSON file with genre definitions
- `TRACK_MOOD_DB_PATH`: Path to a custom JSON file with mood definitions
- `TRACK_TEMPO_DB_PATH`: Path to a custom JSON file with tempo definitions

Example `.env` file:
```
ARTIST_GENRE_DB_PATH=/path/to/custom_genres.json
ARTIST_VISUAL_DB_PATH=/path/to/custom_visuals.json
TRACK_MOOD_DB_PATH=/path/to/custom_moods.json
```

### Custom Databases

You can extend the built-in databases by providing custom JSON files. The format should match the internal structure of each module.

## Integration

These modules are designed to integrate with the broader artist creation flow:

1. Generate artist profile using the Artist Prompt Generator
2. Use the artist profile to generate track prompts with the Track Prompt Generator
3. Pass prompts to LLM orchestration systems
4. Process LLM responses to create artist profiles and tracks
5. Use the profiles and track specifications to generate music, visuals, and other assets

## Requirements

- Python 3.7+
- dotenv (optional, for environment variable loading)

## License

These modules are part of the Artist Creation System and follow the project's licensing terms.
