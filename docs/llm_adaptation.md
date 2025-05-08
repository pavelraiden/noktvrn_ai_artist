# LLM Adaptation Mechanism

## Overview

The AI Artist Platform incorporates a mechanism designed to facilitate adaptation to the evolving landscape of Large Language Models (LLMs). This allows the system to potentially discover and utilize new models as they become available from supported providers, enhancing its capabilities and resilience over time.

## Components

1.  **LLM Registry (`llm_orchestrator/llm_registry.py`):**
    *   A central Python dictionary (`LLM_REGISTRY`) that lists known LLM providers (e.g., "openai", "gemini", "anthropic") and the models they offer (e.g., "gpt-4o-mini", "gemini-1.5-pro-latest", "claude-3-haiku-20240307").
    *   This registry serves as the primary source of truth for models the system *could* potentially use.
    *   It is currently maintained manually within the codebase but could be extended to load from external configuration files or even query provider APIs in the future.

2.  **LLM Orchestrator (`llm_orchestrator/orchestrator.py`):**
    *   **Provider Configuration (`PROVIDER_CONFIG`):** Defines how the orchestrator interacts with each *provider*, including API key environment variables, base URLs (if applicable), client classes, and required libraries.
    *   **Auto-Discovery Logic (within `__init__`):**
        *   When the orchestrator is initialized (with `enable_auto_discovery=True`), it first processes the explicitly defined `primary_model` and `fallback_models`.
        *   It then iterates through the `LLM_REGISTRY`.
        *   For each model listed in the registry, it checks:
            *   Is the provider supported (present in `PROVIDER_CONFIG`)?
            *   Is the required library for the provider installed?
            *   Is the necessary API key available in the environment variables?
            *   Has this specific provider/model combination already been added (either as primary, fallback, or previously discovered)?
        *   If all checks pass and the model hasn't been added yet, the orchestrator attempts to initialize an instance for that model and adds it to the *end* of the `model_preference` list (the fallback sequence).
    *   **Fallback Mechanism:** The orchestrator iterates through the `model_preference` list (primary, then fallbacks, then discovered models) when attempting to generate text. If a model fails (after retries), it moves to the next one in the sequence.

## How it Works

1.  **Initialization:** When the system starts (e.g., the `Batch Runner` initializes an `LLMOrchestrator`), the orchestrator loads the primary and fallback models specified in its configuration.
2.  **Discovery:** It then consults the `LLM_REGISTRY`. If a model like "claude-3-haiku-20240307" is listed under "anthropic" and the Anthropic library is installed and the `ANTHROPIC_API_KEY` is set, the orchestrator will attempt to initialize a client for it and add `("anthropic", "claude-3-haiku-20240307")` to its internal preference list, *after* any explicitly defined primary/fallback models.
3.  **Usage (Fallback Testing):** During normal operation, if the primary model (e.g., "deepseek-chat") and explicit fallbacks (e.g., "gemini-1.5-pro") fail due to API errors or rate limits, the orchestrator will eventually attempt to use the discovered models (like "claude-3-haiku") that were added to the end of the preference list.

## Benefits

*   **Resilience:** Provides additional fallback options if primary/preferred models become unavailable or perform poorly.
*   **Adaptability:** Allows the system to leverage newer models without requiring immediate code changes to the core orchestrator logic, provided the provider interaction pattern is compatible (e.g., OpenAI-compatible APIs, or specific handlers exist).
*   **Experimentation:** Newly discovered models are automatically placed in lower-priority (fallback) roles, allowing them to be tested in production without disrupting core workflows reliant on primary models.

## Limitations & Future Enhancements

*   **Manual Registry:** The `LLM_REGISTRY` currently requires manual updates.
*   **Provider Compatibility:** Auto-discovery only works for providers already defined in `PROVIDER_CONFIG` with compatible client libraries and API structures.
*   **No Automatic Testing:** The system doesn't *proactively* test newly discovered models; they are only used when higher-priority models fail.
*   **No Performance Feedback:** The current mechanism doesn't automatically re-prioritize models based on performance or cost.

Future enhancements could include:
*   Loading the registry from a configuration file.
*   Adding a mechanism to periodically query provider APIs for new models (if APIs support this).
*   Implementing a dedicated testing routine for newly discovered models.
*   Integrating performance and cost data to dynamically adjust the `model_preference` order.

