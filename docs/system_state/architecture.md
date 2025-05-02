# System State: Architecture Overview (Phase 8 Final)

This document provides a high-level overview of the AI Artist Platform's architecture as of the end of Phase 8.

## Core Philosophy

The system is designed around principles of modularity, scalability, and self-evolution. Each component aims to perform a specific function within the artist creation, management, and content generation pipeline, while allowing for adaptation and improvement based on feedback and performance data.

## Key Modules and Flow

1.  **Input & Configuration:**
    *   Uses `.env` for managing sensitive credentials (API keys) and core settings.
    *   Potentially uses YAML/JSON for specific artist profile inputs (handled by `artist_builder/builder/input_handler.py`).

2.  **Artist Builder (`artist_builder/`):**
    *   **Profile Builder (`builder/profile_builder.py`):** Orchestrates the creation of a new artist profile based on input parameters or trends.
    *   **LLM Pipeline (`builder/llm_pipeline.py`):** Manages the sequence of LLM calls required for profile generation, utilizing the `LLMOrchestrator`.
    *   **Schema (`schema/`):** Defines the structure (`artist_profile_schema.py`) and validation rules for artist profiles using Pydantic.
    *   **Trend Analysis (`trend_analyzer/`):** Gathers and processes market/music trends to inform artist creation (partially implemented).
    *   **Storage Manager (`builder/storage_manager.py`):** Handles saving artist profiles and related assets.
    *   **Error Handler (`builder/error_handler.py`):** Manages errors during the build process.

3.  **LLM Orchestrator (`llm_orchestrator/`):**
    *   Manages interactions with multiple LLM providers (DeepSeek, Gemini, Grok, Mistral, OpenAI).
    *   Handles API key loading, client initialization, request retries, and inter-provider fallback.
    *   Includes placeholder logic for future intelligent model routing based on task type.
    *   See `docs/system_state/llm_support.md` for details.

4.  **API Clients (`api_clients/`):**
    *   Provides standardized interfaces for interacting with external APIs (Suno, Pexels, etc.).
    *   See `docs/system_state/api_key_mapping.md` for details.

5.  **Artist Flow / Content Generation (`artist_flow/` & `scripts/`):
    *   **Prompt Generators (`artist_flow/generators/`):** Creates prompts for music (Suno), images/videos based on the artist profile.
    *   **Asset Fetching (`scripts/video_gen/fetch_assets.py`):** Uses API clients (e.g., Pexels) to retrieve stock footage.
    *   **Music Generation:** Interacts with Suno API via `suno_client.py`.
    *   **Video Generation:** Placeholder/Basic implementation using FFmpeg (`scripts/video_gen/ffmpeg_controller.py`).

6.  **Artist Evolution (`artist_evolution/`):**
    *   **Evolution Service (`artist_evolution_service.py`):** Manages the adaptation and progression of artists over time based on feedback and performance.
    *   **Style Adaptor (`style_adaptor.py`):** Modifies artist parameters based on evolution logic.

7.  **Batch Runner (`batch_runner/`):**
    *   Automates the process of generating content batches for artists.
    *   Integrates with Telegram for sending previews and potentially receiving approval.

8.  **Release Chain (`release_chain/`):**
    *   Manages the packaging and metadata tracking of generated content intended for release.
    *   Saves release artifacts and logs.

9.  **Metrics & Feedback (`metrics/`):**
    *   **Metrics Logger (`metrics_logger.py`):** Logs performance metrics and operational data.
    *   **Telegram Feedback (`telegram_feedback_log.py`):** Captures feedback provided via Telegram.

10. **Database (`database/`):**
    *   Defines SQL schema for storing artist profiles, performance data, trends, etc. (Requires setup and integration).
    *   Includes a basic `connection_manager.py`.

11. **Utilities (`utils/`):**
    *   Contains helper functions like the retry decorator (`retry_decorator.py`) and health checker (`health_checker.py`).

## Existing Detailed Diagrams

For more detailed visual representations, please refer to the diagrams within the `/docs/architecture/` directory, specifically:

*   `system_overview.md`
*   `llm_orchestration_flow.md`
*   `artist_generation_pipeline.md` (May need updates based on latest builder implementation)
*   `data_flow.md` (Conceptual)

These diagrams provide visual context for the module interactions and data flow within the system, although some might require updates to perfectly reflect the final Phase 8 state.
