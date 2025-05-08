# AI Artist Platform - Contribution Guide

This guide outlines the standards and practices for contributing to the AI Artist Platform, ensuring consistency, quality, and maintainability.

## 1. Core Principles

*   **Self-Learning Focus:** Every contribution must aim to improve the AI Artist System's ability to self-learn, self-adapt, and self-optimize over time based on performance data and feedback.
*   **Production Readiness:** Prioritize scalability, robustness, monitoring, testing, and security in all development efforts.
*   **Documentation Discipline:** Maintain accurate, up-to-date documentation alongside code changes.
*   **Modular Design:** Utilize the `services/` directory for self-contained, reusable logic components (e.g., database interaction, external API clients, specific processing tasks).

## 2. Documentation Update Cadence

Maintaining synchronized documentation is crucial. Update the following documents as described:

*   **`README.md` (Main Project):**
    *   **When:** After significant architectural changes, addition/removal of core modules (especially in `services/`), changes to setup/installation, or updates to the overall system overview.
    *   **Content:** High-level project description, core features, architecture overview, setup instructions, module list (including status: active/stale/mock), entry points, LLM system overview, artist lifecycle.
*   **`docs/project_context.md`:**
    *   **When:** At the beginning of a new major phase or task block, or when the overall project goals, scope, or key decisions change.
    *   **Content:** Project background, goals, scope, key decisions, architectural principles, AI agent behavior expectations (linking to `behavioral_rules.md`), phase summaries.
*   **`docs/dev_diary.md`:**
    *   **When:** Continuously throughout a task block. Add entries *after* completing significant steps or encountering important issues/learnings.
    *   **Content:** Chronological log of development activities, decisions made, problems encountered, solutions implemented, links to relevant code/commits, verification steps, audit logs, self-repair logs.
*   **Module Documentation (`docs/modules/`):**
    *   **When:** When creating a new service in the `services/` directory or significantly modifying an existing one (changing its purpose, core functions, inputs/outputs, or dependencies).
    *   **Content:** Detailed description of the service's purpose, key functions/classes, usage examples, dependencies, configuration requirements.
*   **`/docs/` Subdirectories (e.g., `architecture/`, `llm/`, `system_state/`):**
    *   **When:** When implementing or changing specific architectural patterns, LLM prompts/flows, deployment strategies, system state summaries, etc.
    *   **Content:** Detailed design documents, flow diagrams, API specifications, specific guides (e.g., `setup_guide.md`, `behavioral_rules.md`), state summaries (`api_key_mapping.md`, `llm_support.md`). Update relevant documents when the corresponding system aspect changes.

## 3. Configuration and Secrets Management

Proper configuration and handling of secrets (API keys, tokens, passwords) are critical for security and deployment flexibility.

*   **Environment Variables:** All configuration values that differ between environments (development, staging, production) or contain sensitive information **must** be managed using environment variables.
*   **`.env` Files:** Environment variables should be loaded from `.env` files located in the project root (`noktvrn_ai_artist/.env`). Component-specific `.env` files are discouraged to centralize configuration.
*   **`.env.example` File:** A corresponding `.env.example` file **must** exist in the repository root. This file serves as a template, listing all required environment variables with placeholder values (e.g., `YOUR_API_KEY`) or default non-sensitive values.
*   **`.gitignore`:** Ensure that `.env` files (containing real secrets) are listed in the root `.gitignore` file to prevent accidental commits.
*   **Loading Variables:** Use libraries like `python-dotenv` to load variables from the root `.env` file into the application environment at runtime.
*   **Accessing Variables:** Access configuration values within the code using `os.getenv("VARIABLE_NAME", "default_value")`.
*   **Documentation:** The purpose and usage of each environment variable should be documented within the `.env.example` file and potentially in relevant module documentation or `docs/system_state/api_key_mapping.md`.

**Never commit `.env` files or hardcode secrets directly into the source code.**

## 4. LLM Integration and Usage

### 4.1 Multi-Provider Orchestration (`llm_orchestrator.py`)

The system utilizes a central `LLMOrchestrator` to manage interactions with multiple LLM providers (DeepSeek, Gemini, Grok, Mistral, OpenAI, Anthropic). This approach provides flexibility and resilience.

*   **Initialization:** The orchestrator is configured with a primary model and a list of fallback models (e.g., primary `deepseek-chat`, fallbacks `["gemini-1.5-flash", "mistral-large-latest"]`).
*   **Provider Support:** It dynamically loads API keys from `.env` and initializes clients for configured and available providers.
*   **Refer to:** `docs/system_state/llm_support.md` for a detailed list of supported providers and current orchestration logic.

### 4.2 Fallback System

The `LLMOrchestrator` implements a robust fallback mechanism:

1.  **Intra-Provider Retries:** Each call to a specific provider includes automatic retries with exponential backoff for transient errors (e.g., rate limits, temporary server issues).
2.  **Inter-Provider Fallback:** If a request to the primary model fails (after exhausting internal retries), the orchestrator automatically attempts the *same* request with the next model specified in the `fallback_models` list.
3.  **Sequential Attempts:** This process continues sequentially through the fallback list until a request succeeds or all configured providers have been attempted.
4.  **Error Logging:** Failures at each step are logged, providing visibility into provider issues.

When contributing code that uses the `LLMOrchestrator`, rely on this built-in resilience rather than implementing custom retry/fallback logic for LLM calls.

### 4.3 Intelligent Routing (Future)

A placeholder exists for intelligent model routing (`generate_text_intelligently`), aiming to select the optimal model based on task type, cost, or performance. Currently, it defaults to the standard primary/fallback sequence. Contributions enhancing this logic are welcome but require careful design and benchmarking.

### 4.4 LLM Prompt Design Guidelines

Effective prompting is crucial for consistent and high-quality LLM outputs.

*   **Clarity and Specificity:** Be explicit about the desired task, output format, constraints, and context. Avoid ambiguity.
*   **Role Definition:** Clearly define the AI's role or persona (e.g., "You are a music critic specializing in electronic genres...").
*   **Context is Key:** Provide sufficient background information, relevant data snippets, and few-shot examples where appropriate.
*   **Structured Output:** Request structured formats like JSON or Markdown when needed. Specify the exact schema or fields required.
    *   *Example (JSON):* "Output your response as a JSON object with the following keys: 'artist_name', 'genre_tags' (list of strings), 'bio' (string)."
*   **Constraints and Guardrails:** Include instructions to avoid undesirable content, stay within length limits, or focus on specific aspects.
*   **Model-Specific Tuning:** While the orchestrator abstracts providers, be mindful that optimal prompt structure can vary slightly between models (e.g., Gemini vs. Mistral). Test prompts against the intended primary and fallback models.
*   **Iterative Refinement:** Prompt engineering is iterative. Test prompts, analyze outputs, and refine the instructions. Log significant prompt changes in `dev_diary.md` or relevant module documentation.
*   **Centralization:** Avoid hardcoding complex prompts directly in application logic. Consider using template files or a dedicated prompt management system/directory (e.g., `/docs/prompts/`) for reusable or complex prompts.

## 5. Naming Conventions

*   **Files/Directories:** Use `snake_case` (e.g., `video_selector.py`, `api_clients/`, `services/`).
*   **Python Variables/Functions:** Use `snake_case` (e.g., `artist_id`, `calculate_score`).
*   **Python Classes:** Use `PascalCase` (e.g., `ArtistProfile`, `PexelsClient`, `ArtistDBService`).
*   **Constants:** Use `UPPER_SNAKE_CASE` (e.g., `API_TIMEOUT = 30`).
*   **Commit Messages:** Follow Conventional Commits format (e.g., `feat: add stock video tracking`, `fix: correct database index syntax`, `docs: update main README`). Use imperative mood (e.g., "add" not "added"). Include issue tracker references if applicable.

## 6. Definition of Done (DoD)

A task or feature is considered "Done" only when all the following criteria are met:

1.  **Logic Implemented:** Core functionality is implemented according to requirements.
2.  **Tests Passed:** Unit tests and relevant integration tests are written and pass successfully.
3.  **Documentation Updated:** All relevant documentation files (as per Section 2) are created or updated to reflect the changes accurately.
4.  **Code Reviewed:** (If applicable in workflow) Code has been reviewed and approved.
5.  **Dependencies Met:** Any external dependencies (libraries, APIs) are correctly integrated and configured.
6.  **Repository Link:** (For agent context) The final state of the relevant code/documentation is accessible and potentially linked in the `dev_diary.md` or final report.

Adhering to this DoD ensures that contributions are complete, verifiable, and maintainable.

## 7. Git Workflow: Commit & Push After Each Task

**Mandatory Requirement:** To ensure the repository always reflects the latest stable state of the project and to facilitate continuous integration and collaboration, a Git commit and push to the `main` branch is **required** at the successful completion of *every* assigned task.

**Process:**

1.  **Complete Task:** Ensure the assigned task is fully completed, tested (where applicable), and meets all requirements.
2.  **Stage Changes:** Use `git add .` (or selectively add files) to stage all new and modified files relevant to the completed task. Ensure `.gitignore` is up-to-date to exclude unnecessary files.
3.  **Commit Changes:** Create a clear, concise commit message summarizing the task completed. Use conventional commit message formats (e.g., `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`).
4.  **Push Changes:** Push the commit to the `origin/main` branch using `git push origin main`.
5.  **Log in Dev Diary:** Add an entry to `docs/development/dev_diary.md` summarizing the task and explicitly stating that the changes have been pushed to GitHub.

**No task is considered complete until the corresponding changes are successfully pushed to the GitHub repository.**

