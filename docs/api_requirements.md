# AI Artist Platform - API Key Requirements (v1.4)

This document outlines the external API keys and credentials required to run the AI Artist Platform, particularly focusing on services implemented or analyzed in v1.4.

## Core Dependencies

These keys are essential for the main functionality and should be configured in the `.env` file.

1.  **LLM APIs (Multiple):**
    *   **Purpose:** Used by the `LLMOrchestrator` for various generation tasks (reflections, potential future content generation) and by the `ErrorAnalysisService` for analyzing errors and suggesting fixes.
    *   **Keys Required:** API keys for the configured LLM providers (e.g., `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`). The specific keys depend on the models listed in `LLM_MODELS`.
    *   **Source:** Obtainable from the respective LLM provider websites (DeepSeek, Google AI Studio, etc.).
    *   **Scope:** General API access for text generation.
    *   **Configuration:** Set the corresponding variables in the `.env` file.

2.  **Telegram Bot API:**
    *   **Purpose:** Used by the `TelegramService` to send notifications (e.g., LLM fallback events, error alerts) and manage the manual approval workflow (sending previews, handling button callbacks via an external webhook).
    *   **Keys Required:**
        *   `TELEGRAM_BOT_TOKEN`: The authentication token for your Telegram bot.
        *   `TELEGRAM_CHAT_ID`: The ID of the chat where the bot should send messages and previews.
    *   **Source:** Obtainable from Telegram by talking to the BotFather.
    *   **Scope:** Sending messages, handling inline keyboards.
    *   **Configuration:** Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the `.env` file.

## Service-Specific Dependencies

1.  **Trend Analysis Service (`services/trend_analysis_service.py`):**
    *   **Purpose:** Fetches social media trends to potentially inform artist evolution or content generation.
    *   **API Used:** `Twitter/search_twitter` via the internal `data_api.ApiClient`.
    *   **Keys Required:** **None directly in this project's `.env` file.** The service relies on the `data_api` environment being correctly configured with the necessary Twitter API credentials. This platform manages the interaction.
    *   **Source:** N/A for this project's configuration.
    *   **Scope:** Twitter search API access (handled by `data_api`).
    *   **Configuration:** Ensure the environment where the `data_api` runs has the appropriate Twitter credentials.

## Future / Potential Dependencies

1.  **Artist Performance Tracking (`services/artist_lifecycle_manager.py`):**
    *   **Purpose:** The lifecycle manager currently uses placeholder logic for performance evaluation. Future enhancements might involve fetching real performance data (views, likes, engagement).
    *   **Potential APIs:** YouTube Data API, Spotify API, etc.
    *   **Keys Required:** **None currently.** If implemented, API keys for the chosen platforms would be needed.
    *   **Status:** Not required for v1.4.

## Security Note

*   **Never commit your `.env` file or API keys directly into the Git repository.** Use the `.env.example` file as a template and keep your actual `.env` file local or managed through secure deployment secrets.
