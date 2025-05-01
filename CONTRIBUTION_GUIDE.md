# AI Artist Platform - Contribution Guide

This guide outlines the standards and practices for contributing to the AI Artist Platform, ensuring consistency, quality, and maintainability.

## 1. Core Principles

*   **Self-Learning Focus:** Every contribution must aim to improve the AI Artist System's ability to self-learn, self-adapt, and self-optimize over time based on performance data and feedback.
*   **Production Readiness:** Prioritize scalability, robustness, monitoring, testing, and security in all development efforts.
*   **Documentation Discipline:** Maintain accurate, up-to-date documentation alongside code changes.

## 2. Documentation Update Cadence

Maintaining synchronized documentation is crucial. Update the following documents as described:

*   **`README.md` (Main Project):**
    *   **When:** After significant architectural changes, addition/removal of core modules, changes to setup/installation, or updates to the overall system overview.
    *   **Content:** High-level project description, core features, architecture overview, setup instructions, module list (including status: active/stale/mock), entry points, LLM system overview, artist lifecycle.
*   **`docs/project_context.md`:**
    *   **When:** At the beginning of a new major phase or task block, or when the overall project goals, scope, or key decisions change.
    *   **Content:** Project background, goals, scope, key decisions, architectural principles, AI agent behavior expectations (linking to `behavioral_rules.md`), phase summaries.
*   **`docs/dev_diary.md`:**
    *   **When:** Continuously throughout a task block. Add entries *after* completing significant steps or encountering important issues/learnings.
    *   **Content:** Chronological log of development activities, decisions made, problems encountered, solutions implemented, links to relevant code/commits, verification steps, audit logs, self-repair logs.
*   **Module `README.md` (e.g., `api_clients/README.md`):**
    *   **When:** When creating a new module or significantly modifying an existing one (changing its purpose, core functions, inputs/outputs, or dependencies).
    *   **Content:** Module purpose, key components/files, core functionality, usage examples, dependencies, configuration.
*   **`/docs/` Subdirectories (e.g., `architecture/`, `modules/`, `llm/`):**
    *   **When:** When implementing or changing specific architectural patterns, module designs, LLM prompts/flows, deployment strategies, etc.
    *   **Content:** Detailed design documents, flow diagrams, API specifications, specific guides (e.g., `setup_guide.md`, `behavioral_rules.md`). Update relevant documents when the corresponding system aspect changes.

## 3. LLM Prompt Writing Rules

*(Note: Specific rules depend heavily on the chosen model and its version. These are general guidelines. Assume placeholders until specific models are finalized.)*

*   **Clarity and Specificity:** Be explicit about the desired output format, constraints, and context. Avoid ambiguity.
*   **Role Definition:** Clearly define the AI's role (e.g., "You are a creative music analyst...").
*   **Context Provision:** Provide sufficient background information, relevant data, and examples.
*   **Output Formatting:** Specify the desired output structure (e.g., JSON schema, Markdown sections, specific fields).
*   **Constraints and Guardrails:** Include instructions to avoid undesirable content, hallucinations, or biases. Define boundaries.
*   **Model-Specific Syntax:** Adapt syntax for specific models (once chosen):
    *   **GPT-4/Claude:** Use clear natural language, XML tags for structure/roles can be effective.
    *   **Grok:** May require more conversational or persona-driven prompts.
    *   **Qwen:** Refer to specific documentation for optimal prompting techniques.
*   **Iterative Refinement:** Test and refine prompts based on actual outputs. Log prompt versions and performance.
*   **Centralization (Future):** Aim to centralize core system prompts or templates in a dedicated `/docs/llm/prompts/` directory or configuration files, rather than hardcoding them deep within logic.

## 4. Naming Conventions

*   **Files/Directories:** Use `snake_case` (e.g., `video_selector.py`, `api_clients/`).
*   **Python Variables/Functions:** Use `snake_case` (e.g., `artist_id`, `calculate_score`).
*   **Python Classes:** Use `PascalCase` (e.g., `ArtistProfile`, `PexelsClient`).
*   **Constants:** Use `UPPER_SNAKE_CASE` (e.g., `API_TIMEOUT = 30`).
*   **Commit Messages:** Follow Conventional Commits format (e.g., `feat: add stock video tracking`, `fix: correct database index syntax`, `docs: update main README`). Use imperative mood (e.g., "add" not "added"). Include issue tracker references if applicable.

## 5. Definition of Done (DoD)

A task or feature is considered "Done" only when all the following criteria are met:

1.  **Logic Implemented:** Core functionality is implemented according to requirements.
2.  **Tests Passed:** Unit tests and relevant integration tests are written and pass successfully.
3.  **Documentation Updated:** All relevant documentation files (as per Section 2) are created or updated to reflect the changes accurately.
4.  **Code Reviewed:** (If applicable in workflow) Code has been reviewed and approved.
5.  **Dependencies Met:** Any external dependencies (libraries, APIs) are correctly integrated and configured (even if using placeholders initially).
6.  **Repository Link:** (For agent context) The final state of the relevant code/documentation is accessible and potentially linked in the `dev_diary.md` or final report.

Adhering to this DoD ensures that contributions are complete, verifiable, and maintainable.



## Git Workflow: Commit & Push After Each Task

**Mandatory Requirement:** To ensure the repository always reflects the latest stable state of the project and to facilitate continuous integration and collaboration, a Git commit and push to the `main` branch is **required** at the successful completion of *every* assigned task.

**Process:**

1.  **Complete Task:** Ensure the assigned task is fully completed, tested (where applicable), and meets all requirements.
2.  **Stage Changes:** Use `git add .` (or selectively add files) to stage all new and modified files relevant to the completed task. Ensure `.gitignore` is up-to-date to exclude unnecessary files.
3.  **Commit Changes:** Create a clear, concise commit message summarizing the task completed. Use conventional commit message formats (e.g., `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`).
4.  **Push Changes:** Push the commit to the `origin/main` branch using `git push origin main`.
5.  **Log in Dev Diary:** Add an entry to `docs/development/dev_diary.md` summarizing the task and explicitly stating that the changes have been pushed to GitHub.

**No task is considered complete until the corresponding changes are successfully pushed to the GitHub repository.**

