# Architecture Diagrams

This file contains visual representations (using Mermaid.js syntax) of key architectural flows within the AI Artist Platform.

## 1. Artist Content Generation Pipeline

This diagram illustrates the process from triggering content creation to storing an approved release in the database. It involves music generation (Suno), video selection (Pexels), an approval workflow (Telegram), and database interaction.

```mermaid
graph TD
    A[Trigger (Manual/Scheduled/Evolution)] --> B{Generate Track};
    B -- Artist Profile/Params --> C[Suno API Client];
    C -- Track URL --> D{Generate/Select Video};
    D -- Track URL/Profile/Params --> E[Audio Analyzer];
    E -- Audio Features --> F[Video Selector];
    F -- Keywords/Source Prefs --> G[Pexels API Client];
    G -- Stock Video URLs --> F;
    F -- Selected Video URL --> H{Approval Workflow};
    H -- Track & Video URLs --> J[Telegram Service];
    J -- Approval Request --> K[Human Reviewer];
    K -- Approve/Reject --> L[Telegram Callback];
    L --> M[Webhook Server];
    M -- Approval Status & URLs --> N{Store Release};
    N -- Release Data --> O[Database Service];
    O -- Insert --> P[DB Table: approved_releases];
```

*Reference: See `/docs/architecture/artist_generation_pipeline.md` for detailed stage descriptions.*

## 2. Conceptual LLM Orchestration Flow (Multi-Agent)

This diagram shows the conceptual multi-agent approach for LLM tasks, combining content generation/refinement with potential analysis and reflection steps. Note that LLM integration is currently mocked.

```mermaid
graph TD
    subgraph Content Generation/Refinement
        direction LR
        AA[Input Request] --> AB(Author LLM);
        AB -- Draft --> AC(Helper LLM);
        AC -- Refined --> AD(Validator LLM);
        AD -- Feedback --> AC;
        AD -- Validated Output --> AE[System Component];
    end

    subgraph Analysis & Reflection (Conceptual)
        direction LR
        BA[Performance Data / System Logs] --> BB(Trend Analyzer LLM);
        BB -- Insights/Anomalies --> BC(Diary Reflector LLM);
        BC -- Formatted Log Entry --> BD[Dev Diary / Audit Log];
    end

    AE --> BA; # Validated output might feed into performance data
```

*Reference: See `/docs/architecture/llm_orchestration_flow.md` and `/docs/llm/README.md` for details on the LLM approach and status.*

