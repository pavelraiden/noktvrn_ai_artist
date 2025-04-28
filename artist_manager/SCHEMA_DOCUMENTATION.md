# Artist Manager Module Documentation

## Schema Documentation

The Artist Manager module uses a comprehensive YAML schema to define the structure and validation rules for artist profiles. This document provides detailed information about the schema structure, field definitions, and validation rules.

## Schema Overview

The artist profile schema is defined in `artist_profile_schema.yaml` and includes the following main sections:

1. **Artist Profile**: The top-level schema defining the core artist profile
2. **Update History Item**: Schema for tracking updates to the artist profile
3. **Artist Profile Settings**: Schema for artist settings and configuration
4. **Release Strategy**: Schema for defining content release patterns
5. **LLM Assignments**: Schema for assigning LLMs to different tasks
6. **Behavior Evolution Settings**: Schema for controlling how the artist evolves
7. **Social Media Presence**: Schema for defining social media behavior

## Field Definitions

### Core Artist Profile Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `artist_id` | string | Yes | Unique identifier for the artist |
| `stage_name` | string | Yes | Artist's stage name |
| `real_name` | string | No | Artist's real name (if applicable) |
| `genre` | string | Yes | Primary genre of the artist |
| `subgenres` | array of strings | Yes | List of subgenres that influence the artist's style |
| `style_description` | string | Yes | Detailed description of the artist's musical style |
| `voice_type` | string | Yes | Description of the artist's vocal characteristics |
| `personality_traits` | array of strings | Yes | List of personality traits that define the artist |
| `target_audience` | string | Yes | Description of the target audience for the artist |
| `visual_identity_prompt` | string | Yes | Prompt for generating the artist's visual identity |
| `song_prompt_generator` | string | No | Template or method used for generating song prompts |
| `video_prompt_generator` | string | No | Template or method used for generating video prompts |
| `backstory` | string | No | The artist's fictional backstory and history |
| `influences` | array of strings | No | Artists or genres that influence this artist's style |
| `creation_date` | string (date-time) | No | Date when the artist profile was created |
| `update_history` | array of objects | No | History of updates made to the artist profile |
| `notes` | string | No | Additional notes about the artist |
| `settings` | object | Yes | Settings and configuration for the artist |
| `is_active` | boolean | No | Whether the artist is currently active |
| `last_content_date` | string (date) | No | Date when content was last generated for this artist |
| `performance_rating` | number | No | Overall performance rating of the artist |
| `current_content_plan_id` | string | No | ID of the current content plan for this artist |
| `content_plan_end_date` | string (date) | No | End date of the current content plan |
| `source_prompt` | string | No | Original prompt used to generate the artist |
| `session_id` | string | No | Session ID from the creation process |
| `metadata` | object | No | Additional metadata for the artist |

### Update History Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `update_date` | string (date) | Yes | Date when the update was made |
| `updated_fields` | array of strings | Yes | List of fields that were updated |
| `update_reason` | string | No | Reason for the update |
| `update_source` | string | No | Source of the update (user, system, etc.) |

### Artist Profile Settings Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `release_strategy` | object | Yes | Strategy for releasing content |
| `llm_assignments` | object | Yes | LLM assignments for different tasks |
| `training_data_version` | string | Yes | Version of training data used for this artist |
| `trend_alignment_behavior` | string (enum) | No | How closely to follow trends |
| `behavior_evolution_settings` | object | No | Settings for artist evolution behavior |
| `social_media_presence` | object | No | Social media presence configuration |
| `performance_metrics_tracking` | boolean | No | Whether to track performance metrics |

### Release Strategy Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `track_release_random_days` | array of integers | Yes | Min and max days between track releases |
| `video_release_ratio` | number | Yes | Probability of creating a video for a track |
| `content_plan_length_days` | integer | No | Length of content plan in days |
| `social_media_post_frequency` | integer | No | Number of social media posts per week |

### LLM Assignments Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `artist_prompt_llm` | string | Yes | LLM used for artist prompt generation |
| `song_prompt_llm` | string | Yes | LLM used for song prompt generation |
| `video_prompt_llm` | string | Yes | LLM used for video prompt generation |
| `final_validator_llm` | string | Yes | LLM used for final validation |

### Behavior Evolution Settings Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `allow_minor_genre_shifts` | boolean | No | Whether to allow minor shifts in genre over time |
| `allow_personality_shifts` | boolean | No | Whether to allow personality traits to evolve |
| `safe_mode` | boolean | No | Whether to restrict evolution to safe parameters |
| `evolution_speed` | string (enum) | No | How quickly the artist evolves |
| `preserve_core_identity` | boolean | No | Whether to maintain core identity elements |

### Social Media Presence Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platforms` | array of strings | No | Social media platforms where the artist is present |
| `posting_style` | string (enum) | No | Style of social media posts |
| `engagement_strategy` | string (enum) | No | How actively the artist engages |

## Validation Rules

The schema enforces the following validation rules:

- **Required Fields**: All required fields must be present in the artist profile
- **String Length**: Minimum and maximum length constraints for string fields
- **Numeric Ranges**: Minimum and maximum values for numeric fields
- **Array Size**: Minimum number of items for array fields
- **Enumerated Values**: Restricted values for certain fields
- **Pattern Matching**: Regex patterns for fields like artist_id
- **Nested Validation**: Validation of nested objects and arrays

## Default Values

The Artist Manager module provides intelligent default values for missing fields:

- **Subgenres**: Based on the primary genre
- **Personality Traits**: Based on the genre
- **Target Audience**: Based on the genre
- **Style Description**: Generated based on the genre
- **Voice Type**: Generated based on the genre
- **Visual Identity Prompt**: Generated based on the genre
- **Release Strategy**: Default values for release frequency and video ratio
- **LLM Assignments**: Default LLM assignments for different tasks
- **Evolution Settings**: Default settings for artist evolution behavior
- **Social Media Presence**: Default platforms and posting style

## Schema Evolution

The schema is designed to be backward compatible while allowing for future extensions. When the schema is updated:

1. New optional fields can be added without breaking existing profiles
2. Required fields cannot be removed without a migration strategy
3. Field types cannot be changed without a conversion strategy
4. Default values ensure that existing profiles remain valid

## Integration with Other Modules

The artist profile schema is designed to integrate with:

- **Artist Builder**: For creating new artist profiles
- **Content Generator**: For generating content based on artist profiles
- **Trend Analyzer**: For evolving artist profiles based on trends
- **Performance Tracker**: For tracking artist performance metrics
