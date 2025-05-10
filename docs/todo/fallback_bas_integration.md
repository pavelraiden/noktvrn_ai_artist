# DevTodo: Fallback BAS Integration for Suno

**ID:** fallback_bas_integration

**Status:** Draft

**Description:**
This document outlines the requirements for integrating a Browser Automation Studio (BAS) based fallback mechanism for the Suno music generation service within the AI Artist System. This fallback is intended to be triggered when the primary Suno API integration fails (e.g., due to API key issues, timeouts, or unexpected API responses) for beat, vocal, or lyric generation tasks.

**Requirements:**

1.  **Trigger Condition:** The BAS fallback should activate automatically when the `SunoClient` encounters persistent or critical errors preventing successful generation via the API.
2.  **BAS Agent Functionality:**
    *   Simulate user interactions with the Suno web UI to perform the requested generation task (beat, vocal, lyrics).
    *   Handle potential UI changes or variations gracefully.
    *   Extract and save the generated output (audio files, lyrics text) to the expected locations within the project structure, mimicking the output of the API client.
    *   Generate detailed logs of its operations, including successes, failures, and any encountered issues.
    *   Notify the system (e.g., the error-handling LLM or monitoring service) about the fallback activation and its outcome.
    *   Potentially trigger retry mechanisms or recovery workflows if the BAS process also fails.
3.  **Integration:**
    *   The fallback mechanism should be integrated modularly into the existing music generation pipeline (likely within or called by `SunoClient` or the orchestrator).
    *   Placeholder functions or classes should be added to the codebase (`suno_client.py` and potentially related modules) to facilitate this future integration.
    *   Clear TODO comments (`# TODO [fallback_bas_integration]: ...`) should mark the specific sections where the BAS fallback logic needs to be implemented.
4.  **Configuration:** Allow configuration of BAS agent parameters (e.g., path to BAS executable, script name) via environment variables or configuration files.

**Next Steps:**

*   Develop the BAS script(s) for Suno UI interaction.
*   Implement the placeholder functions/classes and integration points in the Python codebase.
*   Develop the logic for triggering the fallback and handling its results (output files, logs, notifications).
*   Thoroughly test the fallback mechanism under various failure scenarios.

