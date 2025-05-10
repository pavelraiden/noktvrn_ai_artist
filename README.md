# LLM Integration Documentation

This directory houses documentation related to the integration and orchestration of Large Language Models (LLMs) within the AI Artist Platform.

## Current Status (As of 2025-04-30 Audit & Patch)

*   **Implementation:** The core LLM components, including the orchestrator (`llm_orchestrator/orchestrator.py`) and specific prompt logic for tasks like artist profile generation, are currently in a **mock or placeholder state**. No actual LLM API calls are made.
*   **Models & Specialties (Conceptual):** The system is designed with a multi-agent approach in mind (see `docs/architecture/llm_orchestration_flow.md`), conceptually involving roles like:
    *   **Author/Generator:** Intended for initial content creation (e.g., biography drafts, lyric ideas). Could potentially use models strong in creative generation (e.g., GPT-4, Claude 3 Opus).
    *   **Helper/Refiner:** Intended for refining drafts based on constraints or style guides. Could use models adept at instruction following and editing (e.g., GPT-4, Claude 3 Sonnet).
    *   **Validator/Critic:** Intended for evaluating outputs against criteria, safety, and schema. Could use models strong in analytical reasoning and rule adherence (e.g., GPT-4, Claude 3 Haiku).
    *   *(Note: Specific model choices are not finalized and depend on future implementation and testing.)*
*   **Usage Pattern:** The primary conceptual pattern is a sequential pipeline (Author -> Helper -> Validator) where the output of one stage feeds into the next. This is simulated in mock implementations like `artist_builder/builder/llm_pipeline.py`.
*   **Prompt Chaining:** Conceptually, context (initial request, artist profile, previous LLM outputs) would be passed along the chain. Specific prompt templates and context management strategies are yet to be implemented.
*   **Hallucination Control:** No specific hallucination control logic is implemented due to the mock status. Planned strategies might include strict validation criteria, grounding prompts with factual data, and potentially using the Validator LLM role to check for inconsistencies.
*   **Fallback & Switching:** No fallback or model switching logic is currently implemented. Future implementation might involve retries, switching to alternative models upon failure, or using simpler rule-based logic as a fallback.
*   **Prompts:** No concrete system prompts are stored or used. Placeholder logic exists in mock implementations.

## Planned Contents

*   `prompts/`: Directory for storing and versioning core system prompts (once implemented).
*   `orchestrator_design.md`: Detailed design of the LLM orchestrator (currently covered conceptually in `docs/architecture/llm_orchestration_flow.md`).
*   `safety_protocols.md`: Document outlining content safety filters and guardrails (to be developed).
*   `model_selection.md`: Rationale for chosen LLM models (once finalized and implemented).

See also: `docs/architecture/placeholders_to_replace.md` for a list of known placeholders related to LLM integration.
