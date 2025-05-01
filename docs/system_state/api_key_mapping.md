# System State: API Key Mapping

This document outlines the external API keys required by the AI Artist Platform and their usage within the system. Credentials are managed via the `.env` file in the project root (`/home/ubuntu/ai_artist_system_clone/.env`).

## Core Service Keys

*   **`SUNO_API_KEY`**
    *   **Service:** Suno AI
    *   **Usage:** Music generation (`api_clients/suno_client.py`). Used by the `artist_flow` and potentially `batch_runner`.
    *   **Status:** Implemented and Key Provided.

*   **`PEXELS_API_KEY`**
    *   **Service:** Pexels
    *   **Usage:** Stock video footage retrieval (`api_clients/pexels_client.py`). Used by `video_processing` or related video generation scripts.
    *   **Status:** Implemented and Key Provided.

*   **`PIXABAY_API_KEY`**
    *   **Service:** Pixabay
    *   **Usage:** Stock image/video retrieval (Implementation might be via a generic client or specific `pixabay_client.py` - currently uses Pexels client as primary).
    *   **Status:** Implemented (Placeholder/Secondary) and Key Provided.

*   **`LUMA_API_KEY`**
    *   **Service:** Luma AI (or alternative video generation)
    *   **Usage:** Video generation (`api_clients/luma_client.py`).
    *   **Status:** Implemented (Placeholder) - **Key Not Provided**.

## LLM Provider Keys

These keys are used by the `llm_orchestrator/orchestrator.py` module for various text generation, analysis, and adaptation tasks throughout the system (e.g., `artist_builder`, `prompt_adaptation`).

*   **`DEEPSEEK_API_KEY`**
    *   **Service:** DeepSeek API
    *   **Status:** Implemented and Key Provided.

*   **`GEMINI_API_KEY`**
    *   **Service:** Google Gemini API
    *   **Status:** Implemented and Key Provided.

*   **`GROK_API_KEY`**
    *   **Service:** Grok API (xAI)
    *   **Status:** Implemented and Key Provided.

*   **`MISTRAL_API_KEY`**
    *   **Service:** Mistral AI API
    *   **Status:** Implemented and Key Provided.

*   **`OPENAI_API_KEY`**
    *   **Service:** OpenAI API
    *   **Status:** Implemented (Optional) - Key Not Provided (Commented out in `.env`).

*   **`ANTHROPIC_API_KEY`** (Future)
    *   **Service:** Anthropic Claude API
    *   **Status:** Not Implemented - Requires library and orchestrator update.

## Integration Keys

*   **`TELEGRAM_BOT_TOKEN`**
    *   **Service:** Telegram Bot API
    *   **Usage:** Sending notifications/previews (`batch_runner`), receiving feedback (`streamlit_app/services/telegram_service.py`, `metrics/telegram_feedback_log.py`).
    *   **Status:** Implemented and Key Provided.

*   **`TELEGRAM_CHAT_ID`**
    *   **Service:** Telegram Bot API
    *   **Usage:** Specifies the target chat for bot messages.
    *   **Status:** Implemented (Placeholder) - **Value Not Provided** (Requires manual configuration in `.env`).

## Other Potential Keys (Not Currently Implemented/Required)

*   `DATABASE_URL`: For connecting to a PostgreSQL database (if used).
*   `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET`: For Spotify API integration (e.g., data pipelines, distribution).
*   `DISTROKID_USERNAME` / `DISTROKID_PASSWORD`: For potential automated distribution via DistroKid.

