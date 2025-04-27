# Artist Profile Builder

The Artist Profile Builder is a core module of the AI Artist Creation and Management System that handles the creation, validation, storage, and evolution of AI artist profiles.

## Overview

The Artist Profile Builder takes initial user inputs about an artist and expands them into a complete artist profile through an LLM-enhanced generation pipeline. It ensures all profiles conform to the required schema, provides robust error handling, and includes hooks for future expansion.

## Architecture

The Artist Profile Builder follows a modular architecture with clear separation of concerns:

```
artist_builder/
├── builder/
│   ├── __init__.py
│   ├── input_handler.py       # Processes and validates user inputs
│   ├── llm_pipeline.py        # Integrates with LLM for profile generation
│   ├── profile_validator.py   # Validates profiles against schema
│   ├── storage_manager.py     # Handles profile storage and retrieval
│   ├── future_hooks.py        # Integration points for future expansion
│   ├── error_handler.py       # Logging and error handling
│   ├── profile_builder.py     # Main module integrating all components
│   └── test_profile_builder.py # Tests for the profile builder
├── schema/
│   ├── __init__.py
│   ├── artist_profile_schema.py # Schema definition using Pydantic
│   ├── schema_converter.py      # Conversion between schema versions
│   ├── schema_defaults.py       # Default values for schema fields
│   └── SCHEMA_DOCUMENTATION.md  # Detailed schema documentation
└── README.md                    # Module documentation
```

## Components

### Input Handler

The Input Handler processes and validates initial user inputs before they are passed to the LLM pipeline. It ensures that required fields are present and properly formatted.

Key features:
- Input validation for different input sources (API, CLI, GUI, file)
- Type checking and format validation
- Default value generation for missing fields
- Consistent error reporting

### LLM Pipeline

The LLM Pipeline integrates with the LLM Orchestrator to generate complete artist profiles from initial inputs. It handles prompt construction, LLM interaction, and response parsing.

Key features:
- Flexible prompt templates for different artist types
- Integration with multiple LLM providers
- Response parsing and formatting
- Error handling for LLM failures

### Profile Validator

The Profile Validator ensures that generated artist profiles conform to the required schema. It validates profiles against the schema, corrects issues when possible, and provides detailed validation reports.

Key features:
- Schema validation using Pydantic models
- Automatic correction of common issues
- Detailed validation reports
- Custom validation rules

### Storage Manager

The Storage Manager handles the storage and retrieval of artist profiles. It provides a consistent interface for saving, loading, updating, and deleting profiles.

Key features:
- UUID-based profile identification
- JSON file storage with automatic backup
- Profile versioning and history tracking
- Search and filtering capabilities

### Future Hooks

The Future Hooks module provides integration points for future expansion of the Artist Profile Builder. It includes hooks for trend analysis, behavior adaptation, profile evolution tracking, and custom validation.

Key features:
- Trend analysis integration
- Behavior adaptation based on performance data
- Profile evolution tracking
- Custom validation rules
- Post-generation hooks

### Error Handler

The Error Handler provides consistent logging and comprehensive error handling for the Artist Profile Builder. It ensures that errors are properly logged, tracked, and reported.

Key features:
- Consistent error logging across all components
- Error categorization and tracking
- Detailed error reports with context
- Error recovery strategies

### Profile Builder

The Profile Builder is the main module that integrates all components to provide a complete workflow for creating, validating, and storing artist profiles.

Key features:
- End-to-end profile creation workflow
- Profile updating and evolution
- Profile retrieval and listing
- Trend analysis and behavior adaptation
- Comprehensive error handling

## Usage

### Creating a Profile

```python
from artist_builder.builder.profile_builder import ArtistProfileBuilder

# Initialize the profile builder
builder = ArtistProfileBuilder()

# Define initial inputs
input_data = {
    "stage_name": "Neon Horizon",
    "genre": "Electronic",
    "subgenres": ["Synthwave", "Chillwave"],
    "style_description": "Retro-futuristic electronic music with nostalgic 80s influences",
    "voice_type": "Ethereal female vocals with vocoder effects",
    "personality_traits": ["Mysterious", "Introspective"],
    "target_audience": "25-35 year old electronic music fans",
    "visual_identity_prompt": "Neon cityscape at night with purple and blue color palette"
}

# Create the profile
profile = builder.create_artist_profile(input_data, "api")

# Print the profile ID
print(f"Created profile: {profile['stage_name']} ({profile['artist_id']})")
```

### Updating a Profile

```python
# Update the profile
updates = {
    "backstory": "Neon Horizon emerged from the digital underground in 2025...",
    "update_reason": "Added backstory"
}
updated_profile = builder.update_artist_profile(profile["artist_id"], updates)
```

### Applying Trend Analysis

```python
# Apply trend analysis
trend_data = {
    "trending_subgenres": ["Darksynth", "Vaporwave"],
    "genre_compatibility": {
        "Electronic": {
            "Darksynth": 0.9,
            "Vaporwave": 0.8
        }
    }
}
trend_profile = builder.apply_trend_analysis(profile["artist_id"], trend_data)
```

### Adapting Behavior

```python
# Apply behavior adaptation
performance_data = {
    "trait_performance": {
        "Mysterious": 0.85,
        "Introspective": 0.65
    }
}
behavior_profile = builder.adapt_behavior(profile["artist_id"], performance_data)
```

## Error Handling

The Artist Profile Builder provides comprehensive error handling with specific exception types:

- `ArtistBuilderError`: Base exception for all Artist Profile Builder errors
- `InputError`: Raised for errors in the input data
- `LLMPipelineError`: Raised for errors in the LLM pipeline
- `ValidationError`: Raised for errors in profile validation
- `StorageError`: Raised for errors in profile storage operations
- `IntegrationError`: Raised for errors in integration with other modules

Example error handling:

```python
from artist_builder.builder.error_handler import ArtistBuilderError, InputError

try:
    profile = builder.create_artist_profile(input_data, "api")
except InputError as e:
    print(f"Input error: {e}")
except ArtistBuilderError as e:
    print(f"Error creating profile: {e}")
```

## Future Expansion

The Artist Profile Builder is designed for future expansion through the Future Hooks module. To add new functionality:

1. Create a new hook function
2. Register it with the Future Hooks module
3. The hook will be automatically called at the appropriate time

Example hook registration:

```python
from artist_builder.builder.future_hooks import FutureHooks

# Create a hook function
def my_trend_analyzer(profile, trend_data):
    # Analyze trends and update profile
    return updated_profile

# Register the hook
hooks = FutureHooks()
hooks.register_trend_analyzer("my_trend_analyzer", my_trend_analyzer)
```

## Testing

The Artist Profile Builder includes a comprehensive test suite to ensure all components work together properly. To run the tests:

```python
from artist_builder.builder.test_profile_builder import run_tests

# Run the tests
run_tests()
```

## Integration with Other Modules

The Artist Profile Builder integrates with other modules of the AI Artist Creation and Management System:

- **LLM Orchestrator**: For generating profile content
- **Artist Flow**: For passing completed profiles to the next stage
- **Trend Analyzer**: For adapting profiles based on trends
- **Performance Tracker**: For evolving profiles based on performance data

## Schema Documentation

For detailed information about the artist profile schema, see the [Schema Documentation](../schema/SCHEMA_DOCUMENTATION.md).
