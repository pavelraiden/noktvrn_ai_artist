# System State: LLM Support and Orchestration

This document details the Large Language Model (LLM) providers supported by the AI Artist Platform and the orchestration logic used to manage them.

## Supported LLM Providers

The system, via the `llm_orchestrator/orchestrator.py` module, currently supports the following LLM providers:

*   **DeepSeek:** Utilizes the OpenAI-compatible API endpoint (`https://api.deepseek.com/v1`). Requires `DEEPSEEK_API_KEY`.
*   **Google Gemini:** Uses the `google-generativeai` Python library. Requires `GEMINI_API_KEY`.
*   **Grok (xAI):** Utilizes the OpenAI-compatible API endpoint (`https://api.x.ai/v1`). Requires `GROK_API_KEY`.
*   **Mistral AI:** Uses the `mistralai` Python library. Requires `MISTRAL_API_KEY`.
*   **OpenAI:** Uses the `openai` Python library (optional, requires uncommenting and providing `OPENAI_API_KEY`).

Support for Anthropic Claude is planned but not yet implemented (requires the `anthropic` library and orchestrator updates).

## Orchestration Logic (`llm_orchestrator.py`)

The orchestrator is designed for flexibility and resilience:

1.  **Initialization:** The orchestrator is initialized with a `primary_model` identifier (e.g., `deepseek-chat`) and an optional list of `fallback_models` (e.g., `["gemini-1.5-flash", "mistral-large-latest"]`).
2.  **Provider Inference:** If the provider is not explicitly specified (e.g., `gemini:gemini-1.5-flash`), the orchestrator attempts to infer it based on common model name prefixes (e.g., `deepseek-`, `gemini-`, `grok-`, `mistral-`).
3.  **API Key Loading:** It dynamically loads the required API key for each configured provider from the `.env` file based on the provider type.
4.  **Client Initialization:** Initializes the appropriate Python client library (AsyncOpenAI, google.generativeai, MistralAsyncClient) for each valid and configured provider/model.
5.  **Retry Logic:** Implements automatic retries with exponential backoff for transient errors like rate limits or temporary API issues *within* each provider call.
6.  **Fallback Mechanism:** If the primary model fails (after exhausting its internal retries), the orchestrator automatically attempts the request with the next model in the `fallback_models` list, proceeding sequentially until a successful response is obtained or all options are exhausted.
7.  **Error Handling:** Includes specific handling for different error types (RateLimitError, APIError, ImportError, blocking errors) across providers.

## Intelligent Routing (Placeholder)

The orchestrator includes a placeholder method (`generate_text_intelligently`) for future implementation of intelligent model routing. The goal is to select the most appropriate (e.g., cost-effective, performant) LLM for a specific task type (e.g., creative writing, code generation, summarization) based on predefined rules or dynamic analysis.

**Current Status:** This feature is **not fully implemented**. The placeholder currently defaults to using the standard primary/fallback preference order.

## Role Assignments (Conceptual)

While the intelligent routing is not yet implemented, conceptually, different LLMs could be assigned or preferred for specific roles within the AI Artist generation pipeline based on their strengths:

*   **Profile Generation:** Models strong in creative writing and structured JSON output (e.g., DeepSeek, Mistral Large, Gemini Pro/Advanced).
*   **Lyric Writing:** Models with strong creative and poetic capabilities (e.g., Gemini Advanced, Claude 3 Opus - future, Mistral Large).
*   **Trend Analysis/Summarization:** Models efficient at processing and summarizing text (e.g., Gemini Flash, Mistral Small/Medium, Grok Llama-based models).
*   **Code Generation/Refactoring (Internal Tools):** Models specifically trained for code (e.g., DeepSeek Coder, CodeLlama - via Mistral API?, Gemini Advanced, GPT-4).
*   **Prompt Adaptation/Refinement:** General-purpose capable models (e.g., DeepSeek, Gemini Pro, Mistral Medium/Large).

The current implementation primarily relies on the configured primary/fallback order for all tasks, but the architecture allows for future specialization.
