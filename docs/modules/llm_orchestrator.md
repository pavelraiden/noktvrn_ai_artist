# Module: LLM Orchestrator

*   **File:** `noktvrn_ai_artist/llm_orchestrator/orchestrator.py` (and related files in the directory)

## Role

Conceptually designed to manage interactions with various Large Language Models (LLMs). It aims to abstract the complexities of different LLM APIs and orchestrate multi-step LLM workflows (like the Author-Helper-Validator pattern) for tasks such as artist profile generation, style adaptation, and potentially content analysis or reflection.

## Inputs

*   **Conceptual:**
    *   Task definition (e.g., "generate biography", "refine keywords", "validate concept").
    *   Input data (e.g., artist profile, performance metrics, draft content).
    *   Configuration (e.g., which LLM models to use for specific roles, safety guidelines).

## Outputs

*   **Conceptual:**
    *   Processed output from the LLM workflow (e.g., final biography text, validated keywords, analysis report).
    *   Logs or metadata about the orchestration process.

## Connections / Usage

*   Intended to be used by various higher-level services, particularly those involved in artist creation (e.g., `artist_builder` - currently stale/mock) and potentially artist evolution or content analysis.
*   Would interact with specific LLM client implementations (which are also currently placeholders or not implemented).
*   The conceptual flow is documented in `/docs/architecture/llm_orchestration_flow.md` and `/docs/architecture/diagrams.md`.

## Status

*   **Core (Conceptual):** A central piece of the envisioned AI capabilities.
*   **Mock Implementation:** The current code in the `llm_orchestrator` directory represents a placeholder or mock implementation. It does **not** make actual calls to LLMs.
*   **In Progress / Future:** Requires significant development to integrate actual LLM APIs, implement robust prompt management, context handling, safety features, and the multi-agent orchestration logic.
*   See `/docs/llm/README.md` for more details on the overall LLM integration status.
