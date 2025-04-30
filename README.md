# AI Artist Creation and Management System

## Project Description

The AI Artist Creation and Management System is a comprehensive platform designed to generate, manage, and evolve AI-powered virtual music artists. The system creates complete artist identities, manages their content creation (music, visuals), analyzes performance and market trends, and autonomously adapts the artist's profile, style, and content strategy based on data-driven insights.

Our mission is to explore the potential of autonomous creative systems in the music industry, enabling the automated creation and evolution of virtual artists who produce authentic content while continuously adapting to audience feedback and market dynamics.

## System Architecture & Artist Lifecycle

The system follows a modular architecture centered around a continuous evolution loop:

1.  **Profile Management:** An artist profile (managed by `Artist Profile Manager` - currently placeholder) defines the artist's identity, genre, style, etc.
2.  **Content Generation:** Based on the profile and potentially adapted parameters (`Style Adaptor`), the `Content Generation Flow` orchestrates requests to `Generation Services`.
3.  **External APIs:** Services interact with external APIs (Suno for music, Luma for video, Pexels for stock footage) to generate/retrieve content assets.
4.  **Video Selection:** The `Video Selector` chooses appropriate stock videos based on audio analysis.
5.  **Release & Storage:** Approved content URLs are stored in the `Database` (`approved_releases` table).
6.  **Performance Tracking:** Performance metrics (views, likes, streams, etc.) are collected (manually via `Analytics Dashboard` or potentially via future `Data Pipelines`) and stored in the `Database` (`content_performance` table).
7.  **Evolution Analysis:** The `Artist Evolution Service` analyzes performance data against the artist's profile.
8.  **Adaptation:** Based on the analysis and evolution rules, the `Style Adaptor` modifies generation parameters, and the `Artist Evolution Service` updates the artist profile (logging changes to `artist_progression_log`).
9.  **Loop:** The updated profile influences future content generation, closing the loop.

```mermaid
graph TD
    A[Artist Profile Manager (Placeholder)] -- Profile --> B(Content Generation Flow);
    B -- Content Request & Params --> C{Generation Services};
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

    subgraph Core Modules
        A;
        B;
        F;
        K;
        L;
    end

    subgraph Data & Integration
        C;
        D_Suno;
        D_Luma;
        D_Pexels;
        E;
        G;
        H;
        I;
        J;
        M;
    end
```

**Core Components (Status as of 2025-04-30 Audit):**

1.  **Artist Profile Manager (Placeholder/Stale)**: Manages artist profiles. Likely superseded by evolution logic and direct DB interaction but requires refactoring/clarification.
2.  **Content Generation Flow (Assumed Active)**: Orchestrates content creation.
3.  **Generation Services (Active)**: Interfaces with external APIs.
4.  **Video Selector (Active)**: Selects stock videos.
5.  **Database (PostgreSQL - Active)**: Central persistent storage.
6.  **Analytics Dashboard/Data Entry (Streamlit - Active)**: UI for metrics.
7.  **Database Services (Active)**: Modules for DB interaction.
8.  **Artist Evolution Service (Active)**: Analyzes performance, applies rules, logs changes.
9.  **Style Adaptor (Active)**: Translates profiles to generation parameters.
10. **API Clients (Active)**: Standardized clients for external APIs.
11. **Data Pipelines (Future)**: Planned for automated data fetching.
12. **LLM Integration (Mock/Placeholder)**: Components related to LLM-driven profile generation or parameter adaptation (e.g., `llm_pipeline.py`) are currently mock implementations. See `docs/llm/README.md` and `docs/architecture/placeholders_to_replace.md`.
13. **Stale Modules (Require Review/Refactoring)**: `artist_builder/`, `artist_creator/`, `artist_manager/`, `artist_flow/` contain potentially overlapping or outdated logic from earlier phases.

## Directory Structure (Reflecting Audit Findings)

```
noktvrn_ai_artist/
├── api_clients/          # Clients for external APIs (Suno, Luma, Pexels, Base)
│   └── README.md
├── analytics/            # Performance data handling (DB service, Stock Tracker)
│   └── README.md
├── artist_evolution/     # Artist profile evolution logic, style adaptation, progression logging
│   └── README.md
├── database/
│   ├── schema/           # SQL schema definitions
│   └── connection_manager.py # DB connection pooling
├── video_processing/     # Audio analysis and video selection logic
│   └── README.md
├── docs/                 # Documentation (Architecture, Development, Project State, LLM)
│   ├── architecture/
│   ├── deployment/
│   ├── development/
│   ├── llm/              # LLM integration docs (currently reflects mock status)
│   ├── modules/
│   └── ...
├── scripts/              # Utility & operational scripts
├── tests/                # Unit and integration tests (coverage varies)
├── .env.example          # Environment variables template
├── .github/              # GitHub Actions workflows
├── requirements.txt      # Python dependencies for backend
├── requirements_monitoring.txt # Dependencies for monitoring
├── Dockerfile            # Main application Dockerfile
├── docker-compose.yml    # Docker Compose configuration
├── logging_config.json   # Logging configuration
├── CONTRIBUTION_GUIDE.md # Contribution guidelines (NEW)
└── README.md             # This file

# --- Potentially Stale/Overlapping Modules (Require Review) ---
# artist_builder/
# artist_creator/
# artist_manager/
# artist_flow/
# templates/
# video_gen_config/
# llm_orchestrator/ (Appears missing/mock)
# --------------------------------------------------------------

streamlit_app/            # Streamlit frontend application
├── analytics/            # Dashboard and Data Entry UI components
├── services/             # Services used by Streamlit
├── tests/                # Tests for Streamlit components/services
├── config/
├── .env                  # Environment variables for Streamlit
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
- API keys/credentials for: Suno.ai, Luma Labs, Pexels, Telegram Bot, (Optional: OpenAI or other LLM if mocks replaced).

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
5.  Configure environment variables in a `.env` file at the project root (use `.env.example` as a template). Include DB credentials, API keys, and Telegram details.
6.  Apply database schemas (ensure correct order: `approved_releases`, `content_performance`, `artist_progression_log`):
    ```bash
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f noktvrn_ai_artist/database/schema/<schema_file>.sql
    # Repeat for all schema files
    ```

### Running the System (Docker Compose Recommended)

1.  Ensure Docker and Docker Compose are installed.
2.  Build and start the services:
    ```bash
    docker-compose up --build -d
    ```
3.  Access the Streamlit UI (typically `http://localhost:8501`).
4.  The Telegram webhook server also starts (configuration required via `.env`).
5.  Monitor logs: `docker-compose logs -f`

## AI Agent Behavior

This system is developed with the assistance of an AI agent. The agent's expected behavior, responsibilities, and interaction protocols are defined in the [LLM Behavioral Contract](docs/architecture/behavioral_rules.md).

## Contribution Guide

Contributions are welcome! Please read our [Contribution Guide](CONTRIBUTION_GUIDE.md) for details on code standards, development workflow, testing, documentation, and the core principle of building a self-evolving system.

## Project Status & Next Steps

- **Phases 1-5 & Production Phase (Initial):** Complete.
- **Current Task:** System-Wide Self-Repair & Documentation Finalization (In Progress).
- **Next Step:** Update `behavioral_rules.md` (Step 008 of current task).

For a detailed overview of the project history and specific task blocks, see `docs/development/dev_diary.md` (or individual phase reports).

---

For more detailed information on specific modules, please refer to their respective `README.md` files (if available and up-to-date).



## Phase 6: Artist Batch Runner

This system automates the process of generating artist content (tracks and videos), sending previews for approval via Telegram, and managing the status of generated content.

### Overview

The core script is `batch_runner/artist_batch_runner.py`. It performs the following steps in a cycle:

1.  **Selects** an artist profile (currently placeholder logic).
2.  **Adapts** parameters based on the profile (currently placeholder logic).
3.  **Generates** a track using the Suno client (currently placeholder logic).
4.  **Selects/Generates** a video using Pexels/Luma (currently placeholder logic).
5.  **Creates** a status file in `output/run_status/` for the run.
6.  **Sends** a preview (track/video URLs) to a configured Telegram chat using `services/telegram_service.py`, including Approve/Reject buttons linked to the run ID.
7.  **Waits** (polls) for the status file to be updated by an external webhook server.
8.  **Processes** the result: If approved, logs confirmation and triggers a placeholder release logic. If rejected or timed out, logs the outcome.

### Setup & Configuration

1.  **Dependencies:** Ensure all project dependencies are installed (refer to the main project setup).
2.  **Webhook Server:** A separate webhook server (like `streamlit_app/webhook_server.py`) **must** be running and publicly accessible to receive callbacks from Telegram. This server is responsible for updating the corresponding `run_{run_id}.json` file in `output/run_status/` with the status "approved" or "rejected" based on the button clicked in Telegram.
3.  **Configuration (`.env`):**
    *   Copy `batch_runner/.env.example` to `batch_runner/.env`.
    *   Configure `MAX_APPROVAL_WAIT_TIME` and `POLL_INTERVAL` as needed.
    *   Ensure the necessary API keys and Telegram settings (especially `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) are configured either in `batch_runner/.env` or the main project `.env` file (loaded by `services/telegram_service.py` and potentially other clients).
4.  **Logging:** Logs are written to `logs/batch_runner.log`.

### Running the Batch Runner

*   **Single Cycle (Manual/Cron):** The script is designed to run one full generation cycle and then exit. This is suitable for scheduling via cron.
    ```bash
    cd /path/to/ai_artist_system/noktvrn_ai_artist/batch_runner
    python3 artist_batch_runner.py
    ```
    *Example Cron Job (runs every 30 minutes):*
    ```cron
    */30 * * * * /usr/bin/python3 /path/to/ai_artist_system/noktvrn_ai_artist/batch_runner/artist_batch_runner.py >> /path/to/ai_artist_system/logs/cron.log 2>&1
    ```
*   **Continuous Mode (Manual):** To run continuously with a delay between cycles, you would need to modify the `if __name__ == "__main__":` block in `artist_batch_runner.py` to include a `while True` loop and a `time.sleep()` call.

### Monitoring

A Streamlit dashboard is available to monitor the status of batch runs:

```bash
cd /path/to/ai_artist_system/streamlit_app
streamlit run monitoring/batch_monitor.py
```
This dashboard reads the JSON files from the `output/run_status/` directory.

### Current Status (Placeholders)

*   Artist selection, parameter adaptation, track generation, and video selection currently use **placeholder functions**. These need to be integrated with the actual service modules (`artist_evolution_service`, `style_adaptor`, `suno_client`, `video_selector`, etc.).
*   The release logic (`trigger_release_logic`) is a stub.
*   Error handling for external API calls within the placeholder functions is basic.

