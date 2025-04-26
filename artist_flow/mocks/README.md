# Mock Generators

This directory contains mock implementations of asset generation systems that can be used for testing the full artist creation flow before integrating with real APIs.

## Modules

### Music Generator

The Music Generator provides a simulated music generation system that returns mock track data based on text prompts. It includes:

- A simple function for generating mock tracks with minimal configuration
- A class-based implementation for more complex scenarios
- Intelligent extraction of mood and tempo from prompts
- Reproducible random generation using seed derived from prompts

### Image Generator

The Image Generator provides a simulated image generation system that returns mock image data based on text prompts. It includes:

- A simple function for generating mock images with minimal configuration
- A class-based implementation for more complex scenarios
- Intelligent extraction of style and theme from prompts
- Reproducible random generation using seed derived from prompts

## Usage

### Music Generator

#### Basic Usage

```python
from artist_flow.mocks.music_generator import generate_mock_track

# Define a track prompt
prompt = "Create a dark trap track with mysterious vibes, cold atmosphere, and a slow tempo"

# Generate a mock track
track_info = generate_mock_track(prompt)

# Access the mock track data
track_url = track_info["track_url"]
bpm = track_info["bpm"]
mood = track_info["mood"]
duration = track_info["duration_seconds"]
```

#### Advanced Usage

For more control, you can use the class-based implementation:

```python
from artist_flow.mocks.music_generator import MockMusicGenerator, create_music_generator

# Create a generator instance
generator = create_music_generator(output_dir="/path/to/output")

# Define artist profile
artist_profile = {
    "name": "NightShade",
    "genre": "Dark Trap",
    "style": "Mysterious, Cold"
}

# Define prompt
prompt = {
    "prompt": "Create a dark trap track with mysterious vibes",
    "parameters": {
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "duration_seconds": 180
    }
}

# Generate a track
track = generator.generate_track(
    prompt=prompt,
    artist_profile=artist_profile,
    session_id="test_session_123"
)

# Generate an album
album = generator.generate_album(
    album_concept={
        "album_title": "Midnight Chronicles",
        "concept": "A journey through the night",
        "tracks": [
            {"title": "Dusk", "prompt": "Slow, atmospheric intro"},
            {"title": "Midnight", "prompt": "Peak energy, dark vibes"},
            {"title": "Dawn", "prompt": "Calm, reflective outro"}
        ]
    },
    artist_profile=artist_profile,
    session_id="test_session_123"
)
```

### Image Generator

#### Basic Usage

```python
from artist_flow.mocks.image_generator import generate_mock_image

# Define an image prompt
prompt = "Create a profile image with VHS retro style for a dark trap artist in an urban night setting"

# Generate a mock image
image_info = generate_mock_image(prompt)

# Access the mock image data
image_url = image_info["image_url"]
style = image_info["style"]
theme = image_info["theme"]
```

#### Advanced Usage

For more control, you can use the class-based implementation:

```python
from artist_flow.mocks.image_generator import MockImageGenerator, create_image_generator

# Create a generator instance
generator = create_image_generator(output_dir="/path/to/output")

# Define artist profile
artist_profile = {
    "name": "NightShade",
    "genre": "Dark Trap",
    "style": "Mysterious, Cold"
}

# Define prompt
prompt = {
    "prompt": "Create a mysterious profile image for a dark trap artist",
    "parameters": {
        "style": "Mysterious, Cold",
        "format": "portrait"
    }
}

# Generate an image
image = generator.generate_image(
    prompt=prompt,
    artist_profile=artist_profile,
    session_id="test_session_123",
    image_type="profile"
)

# Generate a complete artist image set
image_set = generator.generate_artist_image_set(
    artist_profile=artist_profile,
    prompts={
        "profile": {"prompt": "Artist profile image with dark atmosphere"},
        "banner": {"prompt": "Wide banner image for social media"},
        "album_cover": {"prompt": "Album cover with mysterious theme"}
    },
    session_id="test_session_123"
)
```

## Integration

These mock generators are designed to integrate with the broader artist creation flow:

1. Artist profiles are generated using prompt generators
2. These mock generators are used to simulate the creation of music and visual assets
3. The resulting mock assets are bundled into the artist passport
4. When real API integration is implemented, these mock generators can be replaced with real API clients

## Extensibility

The mock generators are designed to be easily replaced with real API implementations:

- The interface (function signatures and return structures) will remain consistent
- The factory functions (`create_music_generator` and `create_image_generator`) will be updated to return real implementations
- Code using these generators will not need to be modified when switching to real APIs

## Requirements

- Python 3.7+

## License

These modules are part of the Artist Creation System and follow the project's licensing terms.
