# Artist Profile Schema Documentation

## Overview

This document provides comprehensive documentation for the Artist Profile Schema used in the AI Artist Creation and Management System. The schema defines the structure, required fields, and validation rules for artist profiles to ensure consistency and completeness across the system.

## Schema Structure

The artist profile schema consists of two main components:

1. **Artist Profile**: Core information about the artist
2. **Settings**: Configuration for artist behavior and content generation

### Artist Profile Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `artist_id` | string | Yes | Unique internal identifier for the artist |
| `stage_name` | string | Yes | Public artist name used for releases and promotion |
| `real_name` | string | No | Optional real name for added realism |
| `genre` | string | Yes | Primary music genre of the artist |
| `subgenres` | array of strings | Yes | List of subgenres (minimum 1) |
| `style_description` | string | Yes | Description of the artist's musical style, vibe, and aesthetic |
| `voice_type` | string | Yes | Description of the artist's vocal character and style |
| `personality_traits` | array of strings | Yes | Key behaviors or personality characteristics (minimum 1) |
| `target_audience` | string | Yes | Description of the intended audience for the artist's music |
| `visual_identity_prompt` | string | Yes | Prompt for AI image generation to create artist visuals |
| `song_prompt_generator` | string | Yes | Template for generating song creation prompts |
| `video_prompt_generator` | string | Yes | Template for generating video creation prompts |
| `creation_date` | date | Yes | Date when the artist profile was created |
| `update_history` | array of objects | No | Record of changes made to the profile |
| `notes` | string | No | Additional information or context about the artist |
| `source_prompt` | string | No | Original prompt used to generate the artist (for reference) |
| `session_id` | string | No | Session identifier for tracking purposes |
| `metadata` | object | No | Additional metadata for extensibility |

### Settings Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `release_strategy` | object | Yes | Configuration for track and video releases |
| `llm_assignments` | object | Yes | Assignment of LLM models to different generation tasks |
| `training_data_version` | string | Yes | Version of training data used for the artist |
| `trend_alignment_behavior` | string | Yes | How closely the artist follows trends ("strict", "soft", or "experimental") |
| `behavior_evolution_settings` | object | Yes | Settings that control how the artist evolves over time |

#### Release Strategy Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `track_release_random_days` | array of integers | Yes | Min and max days between track releases [min, max] |
| `video_release_ratio` | float | Yes | Probability (0-1) of creating a video for a track |

#### LLM Assignments Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `artist_prompt_llm` | string | Yes | LLM used for artist profile generation |
| `song_prompt_llm` | string | Yes | LLM used for song prompt generation |
| `video_prompt_llm` | string | Yes | LLM used for video prompt generation |
| `final_validator_llm` | string | Yes | LLM used for final validation |

#### Behavior Evolution Settings Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `allow_minor_genre_shifts` | boolean | Yes | Whether the artist can evolve their genre slightly |
| `allow_personality_shifts` | boolean | Yes | Whether the artist can evolve their personality |
| `safe_mode` | boolean | Yes | Controls whether radical changes are prevented |

### Update History Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `update_date` | date | Yes | Date when the update was made |
| `updated_fields` | array of strings | Yes | List of fields that were updated |

## Example Artist Profile

```json
{
  "artist_id": "artist_20250427123456_7890",
  "stage_name": "Phantom Shadow",
  "real_name": null,
  "genre": "Trap",
  "subgenres": ["Hip Hop", "Dark Trap", "Cloud Rap"],
  "style_description": "A Trap artist with a Mysterious, Intense vibe. Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound.",
  "voice_type": "Deep, raspy voice that delivers lyrics about city life and personal struggles.",
  "personality_traits": ["Mysterious", "Intense", "Authentic"],
  "target_audience": "Young urban listeners who appreciate dark atmospheric beats",
  "visual_identity_prompt": "Professional portrait photograph of a music artist wearing a black hood and mask, identity hidden, creating an enigmatic presence in an urban night setting.",
  "song_prompt_generator": "Create a Trap track with a Mysterious, Intense vibe. The music should combine haunting melodies with heavy bass, creating a unique atmospheric sound. The track should represent the artist's unique sound and appeal to young urban listeners who appreciate dark atmospheric beats.",
  "video_prompt_generator": "Create a music video teaser for a Trap track with a Mysterious, Intense atmosphere. Visual style: Artist wearing a black hood and mask, identity hidden. The video should capture the essence of the artist's identity and complement their music, appealing to young urban listeners who appreciate dark atmospheric beats.",
  "creation_date": "2025-04-27",
  "update_history": [
    {
      "update_date": "2025-04-27",
      "updated_fields": ["initial_creation"]
    }
  ],
  "notes": "A mysterious dark trap artist who thrives in the urban night scene.",
  "settings": {
    "release_strategy": {
      "track_release_random_days": [3, 15],
      "video_release_ratio": 0.7
    },
    "llm_assignments": {
      "artist_prompt_llm": "gpt-4",
      "song_prompt_llm": "gpt-4",
      "video_prompt_llm": "gpt-4",
      "final_validator_llm": "gpt-4"
    },
    "training_data_version": "1.0",
    "trend_alignment_behavior": "soft",
    "behavior_evolution_settings": {
      "allow_minor_genre_shifts": true,
      "allow_personality_shifts": true,
      "safe_mode": true
    }
  },
  "source_prompt": "A mysterious dark trap artist who thrives in the urban night scene. Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound. Always seen wearing a black hood and mask, their identity remains hidden, adding to their enigmatic presence. Their deep, raspy voice delivers lyrics about city life and personal struggles, resonating with listeners who connect with the authentic emotion in their music.",
  "session_id": "test_session_123",
  "metadata": {}
}
```

## Validation Rules

The schema enforces the following validation rules:

1. **Required Fields**: All required fields must be present
2. **Field Types**: Fields must have the correct data types
3. **Array Minimums**: Arrays like `subgenres` and `personality_traits` must have at least one item
4. **Enum Values**: Fields like `trend_alignment_behavior` must have one of the allowed values
5. **Numeric Ranges**: Values like `video_release_ratio` must be within valid ranges (0-1)
6. **Date Formats**: Date fields must be valid dates or ISO format date strings

## Schema Implementation

The schema is implemented using Pydantic models in the `artist_builder/schema/` directory:

- `artist_profile_schema.py`: Schema definition and validation
- `schema_converter.py`: Conversion between schema versions
- `schema_defaults.py`: Default values for schema fields

### Using the Schema

To create a new artist profile:

```python
from artist_builder.composer.artist_profile_composer import ArtistProfileComposer

# Create a composer
composer = ArtistProfileComposer()

# Example prompt
prompt = """
A mysterious dark trap artist who thrives in the urban night scene. 
Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound.
Always seen wearing a black hood and mask, their identity remains hidden, adding to their enigmatic presence.
Their deep, raspy voice delivers lyrics about city life and personal struggles, resonating with listeners
who connect with the authentic emotion in their music.
"""

# Compose a profile (automatically validates against schema)
profile = composer.compose_profile(prompt, session_id="test_session_123")
```

To validate an existing profile:

```python
from artist_builder.schema.artist_profile_schema import validate_artist_profile

# Validate a profile
is_valid, errors = validate_artist_profile(profile_data)
if not is_valid:
    print(f"Validation errors: {errors}")
else:
    print("Profile is valid")
```

## Backward Compatibility

The system maintains backward compatibility with legacy artist profiles through conversion functions:

```python
from artist_builder.schema.schema_converter import legacy_to_new_schema, new_to_legacy_schema

# Convert legacy profile to new schema
new_profile = legacy_to_new_schema(legacy_profile)

# Convert new schema profile to legacy format
legacy_profile = new_to_legacy_schema(new_profile)
```

## Best Practices

1. **Always Validate**: Always validate profiles against the schema before using them
2. **Use Default Generators**: Use the provided default generators for required fields
3. **Maintain History**: Update the `update_history` when modifying profiles
4. **Preserve Metadata**: Store additional information in the `metadata` field
5. **Follow Naming Conventions**: Use consistent naming for artist IDs and fields

## Schema Evolution

As the system evolves, the schema may need to be updated. When updating the schema:

1. Increment the schema version
2. Update the conversion functions
3. Add migration utilities for existing data
4. Update documentation
5. Add tests for new schema features

## Troubleshooting

Common validation errors and solutions:

1. **Missing Required Field**: Ensure all required fields are present
2. **Invalid Field Type**: Check that field values have the correct data type
3. **Empty Array**: Arrays like `subgenres` must have at least one item
4. **Invalid Enum Value**: Check that enum values are one of the allowed options
5. **Date Format Error**: Ensure dates are in the correct format (YYYY-MM-DD or ISO format)
