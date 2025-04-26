# Artist Creator

This directory contains modules for creating and managing complete AI artist profiles, consolidating various generator outputs into unified artist representations.

## Modules

### Artist Passport Generator

The Artist Passport Generator creates a unified "Artist Passport" object that consolidates all prompts and generated assets into a single structured package. It serves as the central integration point for the artist creation flow, bringing together:

- **Artist Profile**
  - Name
  - Style, mood, persona
  - Genres and subgenres
  - Visual identity hints
  - Target audience
  - Lyrics language
  - Themes and values
  - Lifestyle and attitude

- **Initial Song**
  - Track prompt
  - Mock track metadata (from music_generator)
  - Track details (BPM, mood, duration)

- **Initial Visual Assets**
  - Profile cover prompt
  - Track cover prompt
  - Mock image metadata (from image_generator)
  - Style and theme information

- **Initial Video Plan**
  - Video prompt (linked to the initial song)
  - Platform-specific optimization
  - Visual style and content direction

## Usage

### Basic Usage

```python
from artist_flow.creator.artist_passport_generator import generate_artist_passport

# Define artist brief
artist_brief = {
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "persona": "mysterious, energetic",
    "target_audience": "Young adults, night owls",
    "visual_identity": "Always wears a black hood and mask",
    "lyrics_language": "English",
    "themes": "Urban isolation, night life, inner struggles",
    "lifestyle": "Urban night life, digital nomad"
}

# Generate a comprehensive artist passport
passport = generate_artist_passport(artist_brief)

# Access the generated passport components
artist_name = passport['artist_profile']['profile']['name']
track_title = passport['initial_track']['title']
track_url = passport['initial_track']['mock_track']['track_url']
profile_image_url = passport['visual_assets']['profile_cover']['mock_image']['image_url']
video_prompt = passport['video_plan']['prompt']
```

### Advanced Usage

For more control, you can create an instance of the `ArtistPassportGenerator` class:

```python
from artist_flow.creator.artist_passport_generator import ArtistPassportGenerator

# Create a generator with a specific seed for reproducible results
generator = ArtistPassportGenerator(seed=42)

# Generate a full artist passport
passport = generator.generate_artist_passport(artist_brief)
```

## Integration

The Artist Passport Generator is designed to integrate with the broader artist creation flow:

1. User provides an artist brief with key parameters
2. The passport generator uses various prompt generators internally:
   - Artist Prompt Generator for artist profile
   - Track Prompt Generator for initial song
   - Video Prompt Generator for video plan
3. Mock generators are used to simulate asset creation:
   - Music Generator for track assets
   - Image Generator for visual assets
4. The resulting passport can be used to:
   - Display a complete artist preview
   - Generate additional content based on the established identity
   - Export to various platforms and formats

## Extensibility

The Artist Passport Generator is designed to be easily extended when real APIs are integrated:

- The mock generators can be replaced with real API clients
- The passport structure remains consistent regardless of the underlying implementation
- New asset types can be added to the passport without breaking existing functionality

## Requirements

- Python 3.7+
- Access to the artist_flow.generators and artist_flow.mocks modules

## License

This module is part of the Artist Creation System and follows the project's licensing terms.
