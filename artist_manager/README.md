# Artist Manager

The Artist Manager module provides a comprehensive system for creating, validating, managing, and evolving AI artist profiles. This module serves as the foundational system for the AI Artist Creation and Management System, enabling the creation and dynamic evolution of virtual artists.

## Overview

The Artist Manager module consists of three main components:

1. **Artist**: Core class for managing artist profiles according to the schema
2. **ArtistInitializer**: Class for creating new artist profiles with default values
3. **ArtistUpdater**: Class for updating existing profiles and applying trend-based evolution

## Features

- **Schema-based Validation**: All artist profiles are validated against a comprehensive YAML schema
- **Serialization**: Support for both JSON and YAML formats
- **Default Values**: Intelligent application of default values for missing fields
- **Trend-based Evolution**: Dynamic evolution of artist profiles based on trend analysis
- **Change Tracking**: Complete history of all updates made to artist profiles
- **Flexible Access**: Dot notation for accessing nested fields

## Usage Examples

### Creating a New Artist

```python
from artist_manager import ArtistInitializer

# Initialize with minimal information
initializer = ArtistInitializer()
artist = initializer.create_minimal_artist("Neon Horizon", "Electronic")

# Save the artist profile
artist.save("/path/to/artists/neon_horizon.json")
```

### Loading and Updating an Artist

```python
from artist_manager import Artist, ArtistUpdater

# Load an existing artist profile
artist = Artist.load("/path/to/artists/neon_horizon.json")

# Update specific fields
updater = ArtistUpdater()
updates = {
    "style_description": "A unique blend of synthwave and ambient electronic music",
    "settings.release_strategy.video_release_ratio": 0.8
}
success, warnings = updater.update_artist(artist, updates, "Style refinement", "manual_update")

# Save the updated profile
artist.save("/path/to/artists/neon_horizon.json")
```

### Applying Trend-based Updates

```python
from artist_manager import Artist, ArtistUpdater

# Load an existing artist profile
artist = Artist.load("/path/to/artists/neon_horizon.json")

# Apply trend-based updates
updater = ArtistUpdater()
trend_data = {
    "genre_trends": {"Vaporwave": 0.85, "Lofi": 0.65},
    "personality_trends": {"Nostalgic": 0.9, "Dreamy": 0.7},
    "visual_trends": {"Cyberpunk": 0.8},
    "release_trends": {"frequency": 0.7, "video_ratio": 0.8}
}
success, applied_updates, warnings = updater.apply_trend_updates(artist, trend_data)

# Log the updates
updater.save_update_log(artist, applied_updates, "/path/to/logs")

# Save the updated profile
artist.save("/path/to/artists/neon_horizon.json")
```

## Schema Structure

The artist profile schema defines the structure and validation rules for artist profiles. Key components include:

- **Core Identity**: Artist ID, stage name, real name
- **Musical Style**: Genre, subgenres, style description, voice type
- **Personality**: Personality traits, target audience
- **Visual Identity**: Visual identity prompt
- **Content Generation**: Song and video prompt generators
- **Settings**: Release strategy, LLM assignments, evolution settings
- **Performance Tracking**: Metrics for tracking artist performance
- **Evolution Parameters**: Settings that control how the artist evolves over time

For detailed schema information, see the `artist_profile_schema.yaml` file.

## Integration

The Artist Manager module is designed to integrate with:

- **Trend Analyzer**: For providing trend data to drive artist evolution
- **Content Plan Generator**: For creating content plans based on artist profiles
- **Performance Tracking**: For monitoring artist performance metrics
- **Asset Management**: For managing artist assets and content

## Future Enhancements

Planned enhancements for the Artist Manager module include:

- **Advanced Evolution Algorithms**: More sophisticated algorithms for artist evolution
- **Machine Learning Integration**: Using ML to optimize artist parameters
- **Collaborative Artists**: Support for artist collaborations and groups
- **Genre-specific Templates**: Specialized templates for different music genres
- **Performance Feedback Loop**: Automatic evolution based on performance metrics
