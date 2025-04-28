# Artist Creator Module

## Overview

The Artist Creator module provides a comprehensive flow for creating AI artists, from profile generation to prompt design and lyrics creation. This module is part of the AI Artist Creation and Management System and follows the system's self-learning principles.

## Components

The Artist Creator module consists of three main components:

1. **Artist Profile Builder**: Creates detailed artist profiles with personality traits, musical style, and visual aesthetics
2. **Prompt Designer**: Generates creative prompts for songs, videos, and social media content
3. **Lyrics Generator**: Creates song lyrics based on prompts (with LLM integration)

## Directory Structure

```
artist_creator/
├── __init__.py                 # Package initialization
├── artist_profile_builder.py   # Artist profile creation
├── prompt_designer.py          # Prompt generation for various content
├── lyrics_generator.py         # Lyrics generation from prompts
├── artist_creation_flow.py     # Integration of all components
└── tests/                      # Test scripts
    └── test_artist_creation_flow.py  # End-to-end test
```

## Usage

### Creating an Artist Profile

```python
from artist_creator import create_artist_profile

profile = create_artist_profile(
    artist_name="Nebula Drift",
    main_genre="Electronic",
    subgenres=["Ambient", "Downtempo"],
    style_tags=["atmospheric", "ethereal", "cinematic"],
    vibe_description="Dreamy soundscapes with pulsing rhythms that evoke cosmic journeys",
    target_audience="Young adults and professionals who enjoy immersive listening experiences"
)
```

### Generating Prompts

```python
from artist_creator import generate_prompts_for_artist_profile

prompts = generate_prompts_for_artist_profile(artist_profile)
```

### Generating Lyrics

```python
from artist_creator import generate_lyrics_from_prompt

lyrics_data = generate_lyrics_from_prompt(
    prompt_text=song_prompt,
    artist_slug="artist-name"
)
```

### Running the Full Flow

```python
from artist_creator.artist_creation_flow import run_full_artist_creation_flow

result = run_full_artist_creation_flow(
    artist_name="Nebula Drift",
    main_genre="Electronic",
    subgenres=["Ambient", "Downtempo"],
    style_tags=["atmospheric", "ethereal", "cinematic"],
    vibe_description="Dreamy soundscapes with pulsing rhythms that evoke cosmic journeys",
    target_audience="Young adults and professionals who enjoy immersive listening experiences"
)
```

## Output Structure

The Artist Creator module creates the following directory structure for each artist:

```
artists/
└── {artist-slug}/
    ├── profile.json            # Complete artist profile
    ├── prompts/                # Generated prompts
    │   ├── song_prompt.txt     # Prompt for first song
    │   ├── video_prompt.txt    # Prompt for video concept
    │   └── social_prompt.txt   # Prompt for social media content
    └── lyrics/                 # Generated lyrics
        └── {song-slug}.txt     # Lyrics for songs
```

## Self-Learning Capabilities

The Artist Creator module is designed with self-learning principles in mind:

1. **Expandable Architecture**: Each component is designed to be extended with more sophisticated generation capabilities
2. **Feedback Integration**: The system can be enhanced to incorporate feedback on generated content
3. **Adaptive Generation**: The prompt and lyrics generation can evolve based on performance metrics

## Future Enhancements

Planned enhancements for the Artist Creator module include:

1. **Advanced LLM Integration**: Replace stub implementations with actual LLM API calls
2. **Feedback Loop**: Add mechanisms to learn from user feedback on generated content
3. **Style Evolution**: Implement algorithms to evolve artist styles based on trends and performance
4. **Multi-Modal Generation**: Extend to generate visual assets alongside textual content

## Testing

Run the test script to verify the full artist creation flow:

```bash
python -m artist_creator.tests.test_artist_creation_flow
```

This will create a test artist and verify that all expected files are generated correctly.
