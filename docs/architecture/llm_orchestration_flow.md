# LLM Orchestration Flow

This document outlines the conceptual flow for how Large Language Models (LLMs) are intended to be orchestrated within the AI Artist Platform, particularly for tasks like artist profile generation, style adaptation, and potentially content analysis.

**Note:** As of the last system audit (2025-04-30), the LLM components are primarily **mock implementations**. This document describes the *intended* design pattern.

*See `/docs/architecture/diagrams.md` for a visual representation of this flow.*

## Conceptual Flow: Multi-Agent Collaboration (e.g., Author-Helper-Validator)

The intended orchestration pattern involves a collaborative multi-agent approach, where different LLM instances (or a single LLM prompted with different roles) work together to produce and refine outputs. A common pattern envisioned is:

1.  **Author/Generator:**
    *   **Role:** Responsible for the initial generation of content or data based on input parameters and high-level goals.
    *   **Example:** Generating an initial artist biography, suggesting initial musical style keywords, or drafting initial video concepts based on track analysis.
    *   **Input:** Task description, artist profile data, performance metrics, style parameters.
    *   **Output:** Draft content or structured data.

2.  **Helper/Refiner:**
    *   **Role:** Takes the draft output from the Author and refines it based on specific constraints, stylistic guidelines, or additional context.
    *   **Example:** Enhancing the biography for better flow and consistency, refining style keywords to be more specific, adding detail to video concepts.
    *   **Input:** Author's output, specific refinement rules, style guides, target audience information.
    *   **Output:** Refined content or structured data.

3.  **Validator/Critic:**
    *   **Role:** Evaluates the refined output against predefined criteria, quality standards, safety guidelines, and task requirements.
    *   **Example:** Checking the biography for factual consistency (if applicable), ensuring style keywords align with the genre, verifying video concepts meet platform guidelines and don't contain problematic themes.
    *   **Input:** Helper's output, validation criteria, safety rules, schema definitions.
    *   **Output:** Validation status (Pass/Fail), feedback for revision, or the final approved output.

## Simplified Diagram

*(This diagram is also available in `/docs/architecture/diagrams.md`)*

```mermaid
graph TD
    A[Input Request (e.g., Generate Profile)] --> B(Author LLM);
    B -- Draft Output --> C(Helper LLM);
    C -- Refined Output --> D(Validator LLM);
    D -- Validation Feedback --> C; subgraph Revision Loop
    direction TB
    C;
    D;
    end
    D -- Final Output --> E[System Component (e.g., Profile Manager)];
```

## Implementation Status

*   Currently, modules like `artist_builder/builder/llm_pipeline.py` contain mock logic that simulates parts of this flow but does not involve actual multi-stage LLM calls.
*   The specific LLMs for each role (Author, Helper, Validator) have not been finalized.
*   The detailed prompt chaining and context passing between these stages need to be implemented.

Refer to `/docs/llm/README.md` for more details on the overall LLM integration status and planned components.

