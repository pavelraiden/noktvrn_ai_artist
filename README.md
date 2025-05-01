# AI Artist Creation and Management System

## Project Description

The AI Artist Creation and Management System is a comprehensive platform designed to generate, manage, and evolve AI-powered virtual music artists. The system creates complete artist identities, manages their content creation (music, visuals), analyzes performance and market trends, and autonomously adapts the artist's profile, style, and content strategy based on data-driven insights.

Our mission is to explore the potential of autonomous creative systems in the music industry, enabling the automated creation and evolution of virtual artists who produce authentic content while continuously adapting to audience feedback and market dynamics.

## System Architecture & Artist Lifecycle

The system follows a modular architecture centered around a continuous evolution loop, enhanced with resilience mechanisms and multi-provider LLM support:

1.  **Profile Management:** An artist profile (managed by `Artist Profile Manager` - currently placeholder) defines the artist's identity, genre, style, etc.
2.  **Content Generation:** Based on the profile and potentially adapted parameters (`Style Adaptor`), the `Content Generation Flow` orchestrates requests to `Generation Services`.
3.  **LLM Orchestration:** The `LLM Orchestrator` handles interactions with various LLMs (DeepSeek, Gemini, Grok, Mistral, OpenAI) for tasks like profile generation, adaptation, and evolution, using API keys configured via `.env`.
4.  **External APIs:** Services interact with external APIs (Suno for music, Luma for video, Pexels for stock footage) to generate/retrieve content assets. API interactions are wrapped with retry logic (`utils/retry_decorator`) and use keys from `.env`.
5.  **Video Selection:** The `Video Selector` chooses appropriate stock videos based on audio analysis.
6.  **Release & Storage:** Approved content URLs are stored in the `Database` (`approved_releases` table).
7.  **Performance Tracking:** Performance metrics (views, likes, streams, etc.) are collected (manually via `Analytics Dashboard` or potentially via future `Data Pipelines`) and stored in the `Database` (`content_performance` table).
8.  **Evolution Analysis:** The `Artist Evolution Service` analyzes performance data against the artist's profile.
9.  **Adaptation:** Based on the analysis and evolution rules, the `Style Adaptor` modifies generation parameters, and the `Artist Evolution Service` updates the artist profile (logging changes to `artist_progression_log`).
10. **Health Monitoring:** The `utils/health_checker` periodically checks the status of critical external dependencies (e.g., Telegram, APIs).
11. **Batch Automation:** The `Batch Runner` automates the cycle, incorporating health checks, retry logic, and using the `LLM Orchestrator` and API clients.
12. **Feedback Loop:** The `Batch Runner` sends previews via Telegram (using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from `.env`) and processes feedback via the `Streamlit App` and `Webhook Server`.
13. **Metrics & Logging:** Detailed run metrics and feedback summaries are generated (`metrics/`).
14. **Loop:** The updated profile influences future content generation, closing the loop.

```mermaid
graph TD
    A[Artist Profile Manager (Placeholder)] -- Profile --> B(Content Generation Flow);
    B -- Content Request & Params --> C{Generation Services};
    B -- LLM Task --> LLM_Orch[LLM Orchestrator];
    LLM_Orch -- LLM API Call --> LLM_APIs[LLM APIs (DeepSeek, Gemini, Grok, Mistral, OpenAI)];
    LLM_Orch -- Result --> B;
    C -- Suno Prompt --> D_Suno[Suno API];
    C -- Luma Prompt/Ref --> D_Luma[Luma API];
    C -- Video Keywords --> D_Pexels[Pexels API];
    D_Suno -- Generated Track URL --> E[Database - Approved Releases];
    D_Luma -- Generated Video URL --> E;
    D_Pexels -- Stock Video URLs --> F[Video Selector];
    F -- Selected Video URL --> E; 
    E -- Release Info --> G[Analytics Dashboard/Data Entry];
    G -- Manual Metrics --> H[Database - Content Performance];
    I[External APIs - YouTube/Spotify etc.] --> J[Data Pipelines - Future];
    J -- Automated Metrics --> H;
    H -- Performance Data --> K[Artist Evolution Service];
    A -- Artist Profile --> K;
    K -- Analysis & Rules --> L[Style Adaptor];
    L -- Adapted Params --> B;
    K -- Updated Profile --> A;
    K -- Log Entry --> M[Database - Artist Progression Log];
    N[Batch Runner] --> B;
    N -- Checks Health --> O[Health Checker];
    O -- Checks --> D_Suno;
    O -- Checks --> D_Luma;
    O -- Checks --> D_Pexels;
    O -- Checks --> P[Telegram Service];
    O -- Checks --> LLM_APIs;
    C -- Uses --> Q[Retry Decorator];
    N -- Uses --> Q;
    LLM_Orch -- Uses --> Q;
    N -- Send Preview --> P;
    P -- Receive Feedback --> N;
    N -- Log Metrics --> Metrics[Metrics Logger];
    N -- Trigger Release --> ReleaseChain[Release Chain];

    subgraph Core Modules
        A;
        B;
        F;
        K;
        L;
        N;
        LLM_Orch;
        Metrics;
        ReleaseChain;
    end

    subgraph Data & Integration
        C;
        D_Suno;
        D_Luma;
        D_Pexels;
        LLM_APIs;
        E;
        G;
        H;
        I;
        J;
        M;
        P;
    end

    subgraph Utilities
        O;
        Q;
    end
```

**Core Components (Status as of 2025-05-01 - Production Ready v1):**

1.  **Artist Profile Manager (Placeholder/Stale)**: Manages artist profiles. Requires refactoring.
2.  **Content Generation Flow (Assumed Active)**: Orchestrates content creation.
3.  **Generation Services (Active)**: Interfaces with external APIs.
4.  **Video Selector (Active)**: Selects stock videos.
5.  **Database (PostgreSQL - Active)**: Central persistent storage.
6.  **Analytics Dashboard/Data Entry (Streamlit - Active)**: UI for metrics.
7.  **Database Services (Active)**: Modules for DB interaction.
8.  **Artist Evolution Service (Active)**: Analyzes performance, applies rules, logs changes.
9.  **Style Adaptor (Active)**: Translates profiles to generation parameters.
10. **API Clients (Active & Integrated)**: Standardized clients for external APIs (Suno, Luma*, Pexels) using production keys from `.env`. (*Luma key is placeholder*).
11. **LLM Orchestrator (Active & Integrated)**: Manages interactions with multiple LLMs (DeepSeek, Gemini, Grok, Mistral, OpenAI) using production keys from `.env`.
12. **Batch Runner (Active & Integrated)**: Automates the generation cycle, includes approval workflow via Telegram (requires `TELEGRAM_CHAT_ID` in `.env`), health checks, retries, and metrics logging.
13. **Release Chain (Active)**: Packages approved runs into releases.
14. **Release Uploader (Active - Placeholder Upload)**: Prepares releases for deployment.
15. **Utilities (`utils/` - Active)**:
    *   `retry_decorator.py`: Handles transient errors with retries.
    *   `health_checker.py`: Monitors external service health.
16. **Metrics & Feedback (`metrics/` - Active)**: Logs run metrics, generates summaries, processes Telegram feedback.
17. **Data Pipelines (Future)**: Planned for automated data fetching.
18. **Stale Modules (Require Review/Refactoring)**: `artist_builder/`, `artist_creator/`, `artist_manager/`, `artist_flow/`.

## Directory Structure (Reflecting Production Ready v1)

```
noktvrn_ai_artist/
├── api_clients/          # Clients for external APIs (Suno, Luma, Pexels, Base)
│   └── README.md
├── analytics/            # Performance data handling (DB service, Stock Tracker)
│   └── README.md
├── artist_evolution/     # Artist profile evolution logic, style adaptation, progression logging
│   └── README.md
├── batch_runner/         # Automated generation cycle runner
│   └── README.md
├── database/
│   ├── schema/           # SQL schema definitions
│   └── connection_manager.py # DB connection pooling
├── docs/                 # Documentation (Architecture, Development, Project State, LLM, Modules)
│   ├── architecture/
│   ├── deployment/
│   ├── development/
│   ├── llm/
│   ├── modules/
│   └── ...
├── llm_orchestrator/     # Multi-provider LLM interaction handler
│   └── orchestrator.py
├── metrics/              # Metrics logging and feedback analysis
│   ├── metrics_logger.py
│   └── telegram_feedback_log.py
├── output/               # Generated outputs (run status, releases, logs, metrics)
│   ├── deploy_ready/
│   ├── feedback_summary.md
│   ├── metrics_logs/
│   ├── release_log.md
│   ├── release_queue.json
│   ├── releases/
│   └── run_status/
├── release_chain/        # Logic for packaging approved runs into releases
│   └── README.md
├── release_uploader/     # Logic for preparing releases for upload/deployment
│   └── README.md
├── scripts/              # Utility & operational scripts
├── tests/                # Unit and integration tests
│   ├── api_clients/
│   ├── batch_runner/
│   ├── llm_orchestrator/
│   ├── metrics/
│   ├── release_chain/
│   └── utils/            # Tests for utilities (retry, health checker)
├── utils/                # Common utilities (retry decorator, health checker)
│   ├── health_checker.py
│   └── retry_decorator.py
├── video_processing/     # Audio analysis and video selection logic
│   └── README.md
├── .env                  # Local environment variables (DO NOT COMMIT)
├── .env.example          # Environment variables template
├── .github/              # GitHub Actions workflows
├── .gitignore
├── requirements.txt      # Python dependencies for backend
├── requirements_monitoring.txt # Dependencies for monitoring
├── Dockerfile            # Main application Dockerfile
├── docker-compose.yml    # Docker Compose configuration
├── logging_config.json   # Logging configuration
├── CONTRIBUTION_GUIDE.md # Contribution guidelines
└── README.md             # This file

# --- Potentially Stale/Overlapping Modules (Require Review) ---
# artist_builder/
# artist_creator/
# artist_manager/
# artist_flow/
# templates/
# video_gen_config/
# --------------------------------------------------------------

streamlit_app/            # Streamlit frontend application
├── analytics/            # Dashboard and Data Entry UI components
├── monitoring/           # Batch Runner monitoring dashboard
├── release_management/   # Release Chain dashboard
├── services/             # Services used by Streamlit (e.g., Telegram)
├── tests/                # Tests for Streamlit components/services
├── config/
├── .env                  # Environment variables for Streamlit (DO NOT COMMIT)
├── .env.example          # Streamlit environment variables template
├── app.py                # Main Streamlit application entry point
├── webhook_server.py     # Telegram webhook handler
└── README.md             # Streamlit app documentation
```

## Setup and Usage

### Prerequisites

- Python 3.10+
- PostgreSQL 13+ (Database server)
- Docker & Docker Compose (Recommended)
- FFmpeg (for audio/video processing)
- API keys/credentials for: Suno.ai, Pexels, DeepSeek, Gemini, Grok, Mistral, Telegram Bot. (Luma key optional/placeholder).
- A specific Telegram Chat ID where the bot will operate.

### Environment Setup

1.  Clone the repository.
2.  Create and activate a Python virtual environment (if not using Docker).
3.  Install dependencies:
    ```bash
    pip install -r noktvrn_ai_artist/requirements.txt
    pip install -r streamlit_app/requirements.txt 
    # Ensure ffmpeg is installed system-wide
    ```
4.  Set up PostgreSQL database.
5.  Configure environment variables:
    *   Copy `noktvrn_ai_artist/.env.example` to `noktvrn_ai_artist/.env`.
    *   Copy `streamlit_app/.env.example` to `streamlit_app/.env`.
    *   Fill in **all** required credentials in both `.env` files (DB details, API keys, **`TELEGRAM_CHAT_ID`**).
6.  Apply database schemas (ensure correct order: `approved_releases`, `content_performance`, `artist_progression_log`):
    ```bash
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f noktvrn_ai_artist/database/schema/<schema_file>.sql
    # Repeat for all schema files
    ```

### Running the System (Docker Compose Recommended)

1.  Ensure Docker and Docker Compose are installed.
2.  Ensure `.env` files are correctly populated.
3.  Build and start the services:
    ```bash
    docker-compose up --build -d
    ```
4.  Access the Streamlit UI (typically `http://localhost:8501`).
5.  The Telegram webhook server also starts (ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct in `streamlit_app/.env`).
6.  Monitor logs: `docker-compose logs -f`

## AI Agent Behavior

This system is developed with the assistance of an AI agent. The agent's expected behavior, responsibilities, and interaction protocols are defined in the [LLM Behavioral Contract](docs/architecture/behavioral_rules.md).

## Contribution Guide

Contributions are welcome! Please read our [Contribution Guide](CONTRIBUTION_GUIDE.md) for details on code standards, development workflow, testing, documentation, and the core principle of building a self-evolving system.

## Project Status & Next Steps

- **Status:** Production Ready v1 (Integration Complete).
- **Key Changes:** Integrated real API credentials, implemented multi-provider LLM orchestrator, enhanced resilience, metrics, and feedback mechanisms.
- **Known Issues/Placeholders:**
    *   `LUMA_API_KEY` remains a placeholder in `.env` (key not provided).
    *   `TELEGRAM_CHAT_ID` must be manually configured in `.env` files.
    *   Several older modules (`artist_builder`, etc.) are potentially stale and need review/refactoring.
    *   `Release Uploader` performs dummy uploads; real platform integration needed.
    *   `Data Pipelines` for automated metric collection are not yet implemented.
- **Next Step:** System is ready for initial production testing and operation. Further development can focus on replacing remaining placeholders, refining LLM logic, implementing data pipelines, and integrating real release uploads.

For a detailed overview of the project history and specific task blocks, see `docs/development/dev_diary.md`.

