# Module Interfaces

## Overview
This document defines the interfaces between major modules in the AI Artist Creation and Management System, specifying how they interact and exchange data.

## Artist Builder → Artist Flow

### Interface: `ArtistProfileProvider`
- **Purpose**: Provides validated artist profiles to the Artist Flow module
- **Methods**:
  - `get_artist_profile(artist_id: str) → Dict`: Retrieves a specific artist profile
  - `list_artist_profiles() → List[Dict]`: Lists all available artist profiles
  - `update_artist_profile(artist_id: str, updates: Dict) → Dict`: Updates an existing profile
- **Data Format**: JSON-serializable dictionary conforming to ArtistProfile schema
- **Error Handling**: Raises `ProfileNotFoundError`, `ValidationError`, or `StorageError`

### Interface: `CreationReportProvider`
- **Purpose**: Provides creation reports for artist profiles
- **Methods**:
  - `get_creation_report(artist_id: str) → Dict`: Retrieves the creation report for an artist
  - `list_creation_reports() → List[Dict]`: Lists all available creation reports
- **Data Format**: JSON-serializable dictionary with creation metadata
- **Error Handling**: Raises `ReportNotFoundError` or `StorageError`

## Artist Flow → LLM Orchestrator

### Interface: `ContentGenerator`
- **Purpose**: Generates content based on artist profiles
- **Methods**:
  - `generate_track_prompt(artist_id: str, params: Dict) → str`: Creates a prompt for track generation
  - `generate_video_prompt(artist_id: str, track_id: str, params: Dict) → str`: Creates a prompt for video generation
  - `generate_social_post(artist_id: str, content_type: str, params: Dict) → str`: Creates social media content
- **Data Format**: String prompts formatted for specific LLM providers
- **Error Handling**: Raises `PromptGenerationError` or `ArtistNotFoundError`

### Interface: `LLMProvider`
- **Purpose**: Provides access to language models
- **Methods**:
  - `generate_completion(prompt: str, params: Dict) → str`: Generates text completion
  - `generate_chat_completion(messages: List[Dict], params: Dict) → str`: Generates chat completion
  - `estimate_token_usage(prompt: str) → int`: Estimates token usage for a prompt
- **Data Format**: Raw text or structured JSON responses
- **Error Handling**: Raises `LLMConnectionError`, `TokenLimitError`, or `ContentFilterError`

## Artist Flow → Storage Manager

### Interface: `AssetManager`
- **Purpose**: Manages artist assets and content
- **Methods**:
  - `store_track(artist_id: str, track_data: Dict, audio_file: bytes) → str`: Stores a generated track
  - `store_video(artist_id: str, track_id: str, video_data: Dict, video_file: bytes) → str`: Stores a generated video
  - `store_image(artist_id: str, image_type: str, image_data: Dict, image_file: bytes) → str`: Stores an image
  - `get_asset(asset_id: str) → bytes`: Retrieves a specific asset
- **Data Format**: Binary data with JSON metadata
- **Error Handling**: Raises `StorageError` or `AssetNotFoundError`

## Trend Analyzer → Artist Flow

### Interface: `TrendProvider`
- **Purpose**: Provides trend analysis for content adaptation
- **Methods**:
  - `get_current_trends(genre: str) → List[Dict]`: Gets current trends for a genre
  - `analyze_performance(artist_id: str) → Dict`: Analyzes artist performance
  - `recommend_adaptations(artist_id: str) → List[Dict]`: Recommends profile adaptations
- **Data Format**: JSON-serializable dictionaries with trend data
- **Error Handling**: Raises `AnalysisError` or `InsufficientDataError`

## System-Wide Interfaces

### Interface: `LoggingProvider`
- **Purpose**: Provides logging capabilities to all modules
- **Methods**:
  - `log_info(module: str, message: str, context: Dict = None) → None`: Logs informational messages
  - `log_warning(module: str, message: str, context: Dict = None) → None`: Logs warnings
  - `log_error(module: str, message: str, error: Exception, context: Dict = None) → str`: Logs errors
  - `get_logs(module: str, level: str, start_time: datetime, end_time: datetime) → List[Dict]`: Retrieves logs
- **Data Format**: Structured log entries with timestamp, level, module, message, and context
- **Error Handling**: Guaranteed to not throw exceptions

### Interface: `ConfigProvider`
- **Purpose**: Provides configuration to all modules
- **Methods**:
  - `get_config(module: str, key: str) → Any`: Gets a configuration value
  - `set_config(module: str, key: str, value: Any) → None`: Sets a configuration value
  - `get_module_config(module: str) → Dict`: Gets all configuration for a module
- **Data Format**: Various types depending on configuration (strings, numbers, booleans, lists, dictionaries)
- **Error Handling**: Raises `ConfigNotFoundError` or `InvalidConfigError`

## Implementation Notes

1. All interfaces should be implemented as abstract base classes with concrete implementations
2. Error types should be defined in a central error module
3. Data validation should occur at interface boundaries
4. All methods should be properly documented with docstrings
5. Logging should be implemented for all interface method calls
6. Performance metrics should be collected for interface method calls
