# AI Artist Platform - Production Ready v1.2 (Enhancement Pass)

## Project Description

The AI Artist Platform is a comprehensive system designed to autonomously generate, manage, and evolve AI-powered virtual music artists. It creates unique artist identities, orchestrates content creation (music, visuals), analyzes performance, and adapts based on data-driven insights and feedback, aiming to explore the potential of autonomous creative systems in the music industry.

## System Architecture (Phase 10 - v1.2)

The system employs a modular architecture focused on a continuous evolution loop. This version (v1.2) incorporates several enhancements focused on self-improvement and robustness:

*   **Multi-Provider LLM Support:** Utilizes `llm_orchestrator` for interaction with DeepSeek, Gemini, Grok, Mistral, Anthropic, OpenAI (optional) with retry, fallback, and auto-discovery.
*   **API Integration:** Consistent use of environment variables (`.env`) for API keys (Suno, Pexels, LLMs, Telegram).
*   **Persistent Memory:** Artist profiles and performance history are now stored in a SQLite database (`data/artists.db`) managed by `services/artist_db_service.py`, replacing the previous JSON file storage.
*   **Enhanced Lifecycle Control:** The `batch_runner` now uses the database service to manage artist creation (probabilistic), selection (least recently run), and retirement (based on consecutive rejections).
*   **LLM Auto-Reflection:** The `batch_runner` prompts the LLM via the orchestrator to reflect on each generated piece, assessing alignment and suggesting improvements. Reflections are stored in the run status file.
*   **Basic Video Editing:** A new `services/video_editing_service.py` module provides functionality to add text overlays (e.g., artist name) to videos using MoviePy (requires FFmpeg).
*   **Trend Analysis (Initial):** A new `services/trend_analysis_service.py` module uses the Twitter API (via Datasource) to fetch social media data for basic trend scoring. Designed for future integration with other sources like Chartmetric.
*   **A/B Testing Framework:** The `batch_runner` includes a configurable framework to test variations in generation parameters (e.g., prompt prefixes). Test details are logged in the run status file for analysis.
*   **Feedback Loop:** Automated batch processing via `batch_runner` sends previews to Telegram (requires `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`) and processes approval/rejection feedback, updating the artist's performance in the database.
*   **Release Packaging:** `release_chain` prepares approved content runs.
*   **Security:** Hardcoded credentials removed, consistent use of `.env` and `.gitignore` for sensitive data.
*   **CI/CD:** GitHub Actions for code formatting checks.
*   **Frontend Foundation:** Basic Flask-based UI foundation in `frontend/` for future admin panel.

For a detailed breakdown, refer to:
*   `/docs/system_state/architecture.md` (High-level overview - *Needs update for v1.2*)
*   `/docs/system_state/llm_support.md`
*   `/docs/system_state/api_key_mapping.md`
*   `/docs/modules/` (Documentation for new services - *To be added*)

```mermaid
graph TD
    subgraph Configuration
        Env[".env File (API Keys, Settings)"]
    end

    subgraph Core Logic
        BatchRunner["Batch Runner (Automation, Lifecycle, A/B Test, Reflection, Telegram)"]
        Orchestrator["LLM Orchestrator (Multi-Provider, Fallback)"]
        ArtistDB["Artist DB Service (SQLite)"]
        VideoEdit["Video Editing Service"]
        TrendSvc["Trend Analysis Service (Twitter)"]
        ReleaseChain["Release Chain (Packaging)"]
        Frontend["Frontend UI (Flask - Basic)"]
        % Metrics["Metrics & Feedback (Implicit in DB/Logs)"] - Simplified
    end

    subgraph External Services
        LLM_APIs["LLM APIs (DeepSeek, Gemini, ...)"]
        Suno["Suno API (Music Gen)"]
        Pexels["Pexels API (Video Assets)"]
        TwitterAPI["Twitter API (Trends)"]
        Telegram["Telegram Bot API (Notifications, Feedback)"]
    end

    subgraph Data
        SQLiteDB["data/artists.db (Profiles, History)"]
        Output["Output Directory (Logs, Releases, Status)"]
    end

    Env --> Orchestrator
    Env --> BatchRunner
    Env --> Suno
    Env --> Pexels
    Env --> TwitterAPI
    Env --> Telegram
    Env --> Frontend
    Env --> ArtistDB
    Env --> VideoEdit
    Env --> TrendSvc

    BatchRunner -- Uses --> Orchestrator
    BatchRunner -- Uses --> ArtistDB
    BatchRunner -- Uses --> VideoEdit
    BatchRunner -- Uses --> TrendSvc
    BatchRunner -- Uses --> Suno
    BatchRunner -- Uses --> Pexels
    BatchRunner -- Sends Previews/Receives Feedback --> Telegram
    BatchRunner -- Creates Releases --> ReleaseChain

    Orchestrator -- API Calls --> LLM_APIs
    LLM_APIs -- Responses --> Orchestrator

    TrendSvc -- API Calls --> TwitterAPI
    TwitterAPI -- Responses --> TrendSvc

    ArtistDB -- Reads/Writes --> SQLiteDB

    ReleaseChain -- Saves --> Output
    BatchRunner -- Saves Status --> Output
```

## Directory Structure (Phase 10 - v1.2)

```
noktvrn_ai_artist/
├── .env                  # Local environment variables (DO NOT COMMIT)
├── .env.example          # Environment variables template
├── .github/              # GitHub Actions workflows (CI checks)
├── .gitignore
├── api_clients/          # Clients for external APIs (Suno, Pexels, Base)
├── analytics/            # Performance data handling (DB service, Stock Tracker)
├── artist_evolution/     # Artist profile evolution logic, style adaptation (Partially integrated into Batch Runner/DB)
├── batch_runner/         # Automated generation cycle runner (Lifecycle, Reflection, A/B Test)
├── data/                 # Data storage directory
│   └── artists.db        # SQLite database for artist profiles and history
├── docs/                 # Documentation (Architecture, Development, System State, etc.)
│   ├── architecture/
│   ├── deployment/
│   ├── development/
│   ├── modules/          # Docs for specific services (Video Editing, Trend Analysis, DB)
│   └── system_state/     # Current state docs (API Keys, LLM Support, Arch)
├── frontend/             # Basic Flask frontend UI foundation
│   ├── src/
│   ├── templates/
│   ├── requirements.txt
│   └── README.md
├── llm_orchestrator/     # Multi-provider LLM interaction handler
├── logs/                 # Log file output directory (if configured)
├── metrics/              # Metrics logging and feedback analysis (Partially integrated into DB)
├── output/               # Default dir for generated outputs (run status, releases, etc.)
├── release_chain/        # Logic for packaging approved runs into releases
├── release_uploader/     # Logic for preparing releases for upload/deployment (Placeholder)
├── requirements.txt      # Python dependencies for core system
├── scripts/              # Utility & operational scripts
├── services/             # Shared services
│   ├── artist_db_service.py # Manages SQLite artist database
│   ├── telegram_service.py  # Handles Telegram interactions
│   ├── trend_analysis_service.py # Analyzes trends (currently Twitter)
│   └── video_editing_service.py # Adds overlays to videos
├── tests/                # Unit and integration tests
├── utils/                # Common utilities (retry decorator, health checker)
├── video_processing/     # Audio analysis and video selection logic
├── CONTRIBUTION_GUIDE.md # Contribution guidelines
└── README.md             # This file

# --- Potentially Stale/Overlapping Modules (Require Review/Refactoring) ---
# artist_builder/
# artist_creator/
# artist_manager/
# artist_flow/
# templates/ (Root level)
# video_gen_config/
# --------------------------------------------------------------

streamlit_app/            # Streamlit frontend application (Separate Deployment - Potentially Deprecated)
├── ...
```

## Setup and Usage

### Prerequisites

*   Python 3.11
*   Docker & Docker Compose (Recommended)
*   FFmpeg (Required for video editing, install system-wide)
*   API keys/credentials for: Suno.ai, Pexels, DeepSeek, Gemini, Grok, Mistral, Anthropic (optional), Telegram Bot.
*   A specific Telegram Chat ID where the bot will operate.
*   (Optional) Twitter API access via Datasource for trend analysis.

### Environment Setup

1.  **Clone:** `git clone https://github.com/pavelraiden/noktvrn_ai_artist.git`
2.  **Navigate:** `cd noktvrn_ai_artist`
3.  **Configure `.env`:**
    *   Copy `noktvrn_ai_artist/.env.example` to `noktvrn_ai_artist/.env`.
    *   Fill in **all** required credentials (API keys, `TELEGRAM_CHAT_ID`, `OUTPUT_BASE_DIR`).
    *   Configure optional features like `AB_TESTING_ENABLED`.
4.  **Install Dependencies (if not using Docker):**
    ```bash
    # Ensure Python 3.11 is available
    python3.11 -m venv venv
    source venv/bin/activate # or venv\Scripts\activate on Windows
    python3.11 -m pip install -r requirements.txt
    python3.11 -m pip install -r frontend/requirements.txt # If using frontend
    # Ensure ffmpeg is installed and in your system PATH
    sudo apt update && sudo apt install -y ffmpeg # Example for Debian/Ubuntu
    ```

### Running the System

**Option 1: Docker Compose (Recommended)**

1.  Ensure Docker and Docker Compose are installed and running.
2.  Ensure `noktvrn_ai_artist/.env` is correctly populated.
3.  From the `noktvrn_ai_artist` directory, run:
    ```bash
    docker-compose up --build -d
    ```
4.  This typically starts the main application components (Batch Runner, potentially others defined in `docker-compose.yml`).
5.  Monitor logs: `docker-compose logs -f`

**Option 2: Manual Execution (Example: Batch Runner)**

1.  Ensure dependencies are installed for Python 3.11 and the virtual environment is active.
2.  Ensure `noktvrn_ai_artist/.env` is correctly populated.
3.  Run a specific component, e.g., the batch runner:
    ```bash
    python3.11 batch_runner/artist_batch_runner.py
    ```

## Contribution Guide

Contributions are welcome! Please read our [Contribution Guide](CONTRIBUTION_GUIDE.md) for details on code standards, development workflow, testing, documentation, and the core principle of building a self-evolving system.

## Project Status (Phase 10 - Enhancement Pass v1.2)

*   **Status:** Enhancement Pass completed. Includes significant improvements to self-adaptation, data persistence, and experimentation capabilities.
*   **Key Features Added/Enhanced in v1.2:**
    *   **Persistent Memory:** SQLite database (`data/artists.db`) for artist profiles and history.
    *   **Enhanced Lifecycle Control:** DB-driven artist creation, selection, and retirement logic in Batch Runner.
    *   **LLM Auto-Reflection:** Batch Runner generates and stores LLM reflections on generated content.
    *   **Video Editing Service:** Basic text overlay capability (`services/video_editing_service.py`).
    *   **Trend Analysis Service:** Initial implementation using Twitter API (`services/trend_analysis_service.py`).
    *   **A/B Testing Framework:** Configurable testing of parameter variations in Batch Runner.
    *   **Security Audit:** Removed hardcoded keys, standardized environment variable usage.
*   **Known Issues/Placeholders:**
    *   Chartmetric API integration pending access verification.
    *   Suno API endpoint (`/generate`) may still have external issues.
    *   Intelligent LLM routing is basic.
    *   Several older modules (`artist_builder`, etc.) need review/refactoring.
    *   `Release Uploader` performs dummy uploads.
    *   Frontend UI is a basic placeholder.
    *   Video Editing / Trend Analysis services need integration into the main generation flow.
    *   Comprehensive unit/integration tests for new services are needed.
*   **Next Steps:** Integrate new services (Video Editing, Trend Analysis) into the Batch Runner flow, add unit tests, update detailed documentation (`/docs/modules/`, `/docs/system_state/architecture.md`), perform integration testing, prepare for production deployment/monitoring.

For a detailed history, see `docs/development/dev_diary.md`.

