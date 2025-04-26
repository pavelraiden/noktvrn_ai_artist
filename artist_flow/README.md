# Artist Flow

This directory contains the core modules for the AI Artist Creation System, providing a complete pipeline for generating AI artists with music, visuals, and promotional content.

## Directory Structure

- **generators/** - Prompt generators for artist profiles, tracks, and videos
- **mocks/** - Mock implementations of asset generation systems for testing
- **creator/** - Modules for creating and managing complete artist profiles
- **artist_creator.py** - Main entry point for the artist creation flow
- **asset_manager.py** - Utilities for managing artist assets and files
- **prompt_generators.py** - Legacy prompt generation (being migrated to generators/)
- **test_*.py** - Test files for various components

## Core Components

### Generators

The `generators/` directory contains specialized prompt generators for different aspects of the artist creation process:

- **Artist Prompt Generator** - Creates detailed prompts for AI artist profiles
- **Track Prompt Generator** - Creates prompts for AI-written songs
- **Video Prompt Generator** - Creates prompts for short-form video content

See the [generators README](generators/README.md) for detailed documentation.

### Mock Generators

The `mocks/` directory contains mock implementations of asset generation systems:

- **Music Generator** - Simulates music generation with mock track data
- **Image Generator** - Simulates image generation with mock image data

See the [mocks README](mocks/README.md) for detailed documentation.

### Creator

The `creator/` directory contains modules for creating and managing complete artist profiles:

- **Artist Passport Generator** - Consolidates all prompts and generated assets into a unified package

See the [creator README](creator/README.md) for detailed documentation.

### Asset Manager

The `asset_manager.py` module provides utilities for handling file paths, directory structures, and asset bundling for artists. It includes:

- Creating and managing artist directories
- Saving and loading artist profiles
- Managing music and image assets
- Creating asset bundles for distribution

### Artist Creator

The `artist_creator.py` module serves as the main entry point for the artist creation flow. It coordinates the entire process from initial prompt generation to final asset bundling.

## Usage

### Basic Usage

```python
from artist_flow.artist_creator import create_new_artist

# Define artist parameters
artist_parameters = {
    "genre": "Dark Trap",
    "style": "Mysterious, Cold",
    "persona": "mysterious, energetic",
    "target_audience": "Young adults, night owls",
    "visual_identity": "Always wears a black hood and mask",
    "lyrics_language": "English",
    "themes": "Urban isolation, night life, inner struggles",
    "lifestyle": "Urban night life, digital nomad"
}

# Create a new artist
artist = create_new_artist(artist_parameters)

# Access artist components
artist_profile = artist["profile"]
music_assets = artist["music_assets"]
visual_assets = artist["visual_assets"]
```

### Advanced Usage

For more control over the artist creation process, you can use the individual components directly:

```python
from artist_flow.generators.artist_prompt_generator import generate_artist_prompt
from artist_flow.generators.track_prompt_generator import generate_track_prompt
from artist_flow.creator.artist_passport_generator import generate_artist_passport
from artist_flow.asset_manager import create_asset_manager

# Generate artist profile
artist_profile = generate_artist_prompt(artist_parameters)

# Generate track prompt based on artist profile
track_prompt = generate_track_prompt(artist_profile["metadata"])

# Generate complete artist passport
passport = generate_artist_passport(artist_parameters)

# Create asset manager for file handling
asset_manager = create_asset_manager()
asset_manager.save_artist_profile(passport["artist_profile"])
```

## Integration

The Artist Flow module is designed to integrate with the broader AI Music Label system:

1. User provides artist parameters
2. Artist Flow generates a complete artist with music and visual assets
3. Performance Manager tracks and optimizes artist performance
4. Content Plan Generator creates ongoing content strategy
5. Distribution System publishes content to various platforms

## Migration Notes

The system is currently migrating from the legacy `prompt_generators.py` to the modular generators in the `generators/` directory. New development should use the modular generators.

## Requirements

- Python 3.7+
- Access to mock generators or real API implementations

## License

This module is part of the AI Music Label system and follows the project's licensing terms.
