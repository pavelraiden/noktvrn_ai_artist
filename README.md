# AI Artist Platform - Production Ready v1.3 (Finalizer Pass)

## Project Description

The AI Artist Platform is a comprehensive system designed to autonomously generate, manage, and evolve AI-powered virtual music artists. It creates unique artist identities, orchestrates content creation (music, visuals), analyzes performance, and adapts based on data-driven insights and feedback, aiming to explore the potential of autonomous creative systems in the music industry.

## System Architecture (Phase 11 - v1.3)

The system employs a modular architecture focused on a continuous evolution loop. This version (v1.3) incorporates several enhancements focused on production readiness, robustness, and control:

*   **Multi-Provider LLM Support:** Utilizes `llm_orchestrator` for interaction with DeepSeek, Gemini, Grok, Mistral, Anthropic, OpenAI (optional) with retry, **enhanced fallback logic (sequential attempts through ranked models, Telegram notifications)**, and auto-discovery.
*   **API Integration:** Consistent use of environment variables (`.env`) for API keys (Suno, Pexels, LLMs, Telegram).
*   **Persistent Memory:** Artist profiles, performance history, and **error reports** are stored in a SQLite database (`data/artists.db`) managed by `services/artist_db_service.py`.
*   **Enhanced Lifecycle Control:** The `batch_runner` uses the database service to manage artist creation (probabilistic), selection (least recently run), and retirement (based on consecutive rejections).
*   **LLM Auto-Reflection:** The `batch_runner` prompts the LLM via the orchestrator to reflect on each generated piece, assessing alignment and suggesting improvements. Reflections are stored in the run status file.
*   **Basic Video Editing:** A `services/video_editing_service.py` module provides functionality to add text overlays to videos using MoviePy (requires FFmpeg).
*   **Trend Analysis (Initial):** A `services/trend_analysis_service.py` module uses the Twitter API (via Datasource) for basic trend scoring.
*   **A/B Testing Framework:** The `batch_runner` includes a configurable framework to test variations in generation parameters.
*   **Telegram Integration:** Automated batch processing via `batch_runner` sends previews to Telegram (requires `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`) and processes approval/rejection feedback. **(Note: Control Panel Interface was skipped due to technical issues)**.
*   **Error Analysis & Auto-Fixing:** A dedicated `services/error_analysis_service.py` monitors logs (`logs/batch_runner.log`), uses LLMs (`llm_orchestrator`) to analyze errors, suggests fixes (including diff patches), logs reports to the database (`error_reports` table), and can optionally attempt auto-patching via `git apply`. Notifies via Telegram.
*   **Error Reporting Dashboard:** A Streamlit application (`dashboard/error_dashboard.py`) provides a web interface to view, filter, and inspect error reports stored in the database.
*   **Autopilot/Manual Control:** Artists have an `autopilot_enabled` flag in the database. The `batch_runner` checks this flag; if true, runs are automatically approved (`autopilot_approved` status) and proceed to the release chain; otherwise, manual approval via Telegram is required. A helper script (`scripts/toggle_autopilot.py`) allows easy toggling.
*   **Release Packaging:** `release_chain` prepares approved content runs.
*   **Security:** Hardcoded credentials removed, consistent use of `.env` and `.gitignore` for sensitive data.
*   **CI/CD:** GitHub Actions for code formatting checks.
*   **Frontend Foundation:** Basic Flask-based UI foundation in `frontend/` for future admin panel.
*   **Code Structure Audit:** Removed deprecated modules (`artist_builder`, `analytics`, `database`, `artist_evolution`) and validated core component imports.

For a detailed breakdown, refer to:
*   `/docs/system_state/architecture.md` (High-level overview - *Needs update for v1.3*)
*   `/docs/system_state/llm_support.md`
*   `/docs/system_state/api_key_mapping.md`
*   `/docs/modules/` (Documentation for services)

```mermaid
graph TD
    subgraph Configuration
        Env[".env File (API Keys, Settings)"]
    end

    subgraph Core Logic
        BatchRunner["Batch Runner (Automation, Lifecycle, A/B Test, Reflection, Autopilot Check)"]
        Orchestrator["LLM Orchestrator (Multi-Provider, Enhanced Fallback)"]
        ArtistDB["Artist DB Service (SQLite - Artists, Errors, Autopilot Flag)"]
        VideoEdit["Video Editing Service"]
        TrendSvc["Trend Analysis Service (Twitter)"]
        TelegramSvc["Telegram Service (Notifications, Approval Feedback)"]
        ReleaseChain["Release Chain (Packaging)"]
        ErrorAnalyzer["Error Analysis Service (Log Monitor, LLM Analysis, Auto-Fix, DB Logging)"]
        ErrorDashboard["Error Dashboard (Streamlit UI)"]
        Frontend["Frontend UI (Flask - Basic)"]
    end

    subgraph External Services
        LLM_APIs["LLM APIs (DeepSeek, Gemini, ...)"]
        Suno["Suno API (Music Gen)"]
        Pexels["Pexels API (Video Assets)"]
        TwitterAPI["Twitter API (Trends)"]
        TelegramAPI["Telegram Bot API"]
        GitPlatform["Git Platform (Auto-Fixing)"]
    end

    subgraph Data
        SQLiteDB["data/artists.db (Profiles, History, Errors, Autopilot)"]
        Output["Output Directory (Releases, Status)"]
        Logs["logs/ (Detailed Logs)"]
    end

    Env --> Orchestrator
    Env --> BatchRunner
    Env --> Suno
    Env --> Pexels
    Env --> TwitterAPI
    Env --> TelegramSvc
    Env --> Frontend
    Env --> ArtistDB
    Env --> VideoEdit
    Env --> TrendSvc
    Env --> ErrorAnalyzer

    BatchRunner -- Uses --> Orchestrator
    BatchRunner -- Uses --> ArtistDB
    BatchRunner -- Uses --> VideoEdit
    BatchRunner -- Uses --> TrendSvc
    BatchRunner -- Uses --> Suno
    BatchRunner -- Uses --> Pexels
    BatchRunner -- Uses --> TelegramSvc
    BatchRunner -- Creates Releases --> ReleaseChain
    BatchRunner -- Logs Errors --> Logs

    Orchestrator -- API Calls --> LLM_APIs
    LLM_APIs -- Responses --> Orchestrator

    TrendSvc -- API Calls --> TwitterAPI
    TwitterAPI -- Responses --> TrendSvc

    TelegramSvc -- API Calls --> TelegramAPI
    TelegramAPI -- Updates/Commands --> TelegramSvc
    TelegramSvc -- Updates --> BatchRunner # For approval feedback

    ArtistDB -- Reads/Writes --> SQLiteDB

    ReleaseChain -- Saves --> Output
    BatchRunner -- Saves Status --> Output

    ErrorAnalyzer -- Reads --> Logs
    ErrorAnalyzer -- Uses --> Orchestrator # For analysis/fixing
    ErrorAnalyzer -- Interacts --> GitPlatform # For patching
    ErrorAnalyzer -- Notifies --> TelegramSvc
    ErrorAnalyzer -- Logs Reports --> ArtistDB

    ErrorDashboard -- Reads --> ArtistDB
```

## Directory Structure (Phase 11 - v1.3)

```
noktvrn_ai_artist/
├── .env                  # Local environment variables (DO NOT COMMIT)
├── .env.example          # Environment variables template
├── .github/              # GitHub Actions workflows (CI checks)
├── .gitignore
├── api_clients/          # Clients for external APIs (Suno, Pexels, Base)
├── batch_runner/         # Automated generation cycle runner (Lifecycle, Reflection, A/B Test, Autopilot)
├── dashboard/            # Streamlit error reporting dashboard
│   └── error_dashboard.py
├── data/                 # Data storage directory
│   └── artists.db        # SQLite database for artist profiles, history, errors, autopilot status
├── docs/                 # Documentation (Architecture, Development, System State, etc.)
│   ├── architecture/
│   ├── deployment/
│   ├── development/
│   ├── modules/          # Docs for specific services (Video Editing, Trend Analysis, DB, Telegram, Error Analysis)
│   └── system_state/     # Current state docs (API Keys, LLM Support, Arch)
├── frontend/             # Basic Flask frontend UI foundation
│   ├── src/
│   ├── templates/
│   ├── requirements.txt
│   └── README.md
├── llm_orchestrator/     # Multi-provider LLM interaction handler (with enhanced fallback)
├── logs/                 # Log file output directory
├── metrics/              # Metrics logging and feedback analysis (Partially integrated into DB)
├── output/               # Default dir for generated outputs (run status, releases, etc.)
├── release_chain/        # Logic for packaging approved runs into releases
├── release_uploader/     # Logic for preparing releases for upload/deployment (Placeholder)
├── requirements.txt      # Python dependencies for core system (includes streamlit)
├── scripts/              # Utility & operational scripts
│   ├── boot_test.py
│   └── toggle_autopilot.py # Helper to toggle artist autopilot mode
├── services/             # Shared services
│   ├── artist_db_service.py # Manages SQLite database (artists, errors)
│   ├── error_analysis_service.py # Monitors logs, analyzes errors, attempts fixes
│   ├── telegram_service.py  # Handles Telegram interactions (Notifications, Approval Feedback)
│   ├── trend_analysis_service.py # Analyzes trends (currently Twitter)
│   └── video_editing_service.py # Adds overlays to videos
├── tests/                # Unit and integration tests
├── utils/                # Common utilities (retry decorator, health checker)
├── video_processing/     # Audio analysis and video selection logic
├── boot_test.py          # Script to test core component imports/initialization
├── CONTRIBUTION_GUIDE.md # Contribution guidelines
└── README.md             # This file
```

## Setup and Usage

### Prerequisites

*   Python 3.11
*   Docker & Docker Compose (Recommended)
*   FFmpeg (Required for video editing, install system-wide)
*   Git (Required for error auto-fixing)
*   API keys/credentials for: Suno.ai, Pexels, DeepSeek, Gemini, Grok, Mistral, Anthropic (optional), Telegram Bot.
*   A specific Telegram Chat ID where the bot will operate.
*   (Optional) Twitter API access via Datasource for trend analysis.

### Environment Setup

1.  **Clone:** `git clone https://github.com/pavelraiden/noktvrn_ai_artist.git`
2.  **Navigate:** `cd noktvrn_ai_artist`
3.  **Configure `.env`:**
    *   Copy `.env.example` to `.env`.
    *   Fill in **all** required credentials (API keys, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OUTPUT_BASE_DIR`).
    *   Configure optional features like `AB_TESTING_ENABLED`, `AUTO_FIX_ENABLED`.
4.  **Install Dependencies (if not using Docker):**
    ```bash
    # Ensure Python 3.11 is available
    python3.11 -m venv venv
    source venv/bin/activate # or venv\Scripts\activate on Windows
    python3.11 -m pip install -r requirements.txt
    python3.11 -m pip install -r frontend/requirements.txt # If using frontend
    # Ensure ffmpeg is installed and in your system PATH
    sudo apt update && sudo apt install -y ffmpeg git # Example for Debian/Ubuntu
    ```

### Running the System

**Option 1: Docker Compose (Recommended)**

1.  Ensure Docker and Docker Compose are installed and running.
2.  Ensure `.env` is correctly populated.
3.  From the project root directory, run:
    ```bash
    docker-compose up --build -d
    ```
4.  This typically starts the main application components (Batch Runner, Error Analysis Service, potentially others defined in `docker-compose.yml`).
5.  Monitor logs: `docker-compose logs -f`

**Option 2: Manual Execution**

1.  Ensure dependencies are installed for Python 3.11 and the virtual environment is active.
2.  Ensure `.env` is correctly populated.
3.  Run components in separate terminals if needed:
    *   **Batch Runner:** `python3.11 batch_runner/artist_batch_runner.py`
    *   **Error Analysis Service:** `python3.11 services/error_analysis_service.py`
    *   **Error Dashboard:** `streamlit run dashboard/error_dashboard.py`

### Using Helper Scripts

*   **Toggle Autopilot:**
    ```bash
    ./scripts/toggle_autopilot.py <artist_id> <on|off>
    # Example: ./scripts/toggle_autopilot.py 1 on
    ```

## Contribution Guide

Contributions are welcome! Please read our [Contribution Guide](CONTRIBUTION_GUIDE.md) for details on code standards, development workflow, testing, documentation, and the core principle of building a self-evolving system.

## Project Status (Phase 11 - Finalizer Pass v1.3)

*   **Status:** Production Finalizer Pass nearing completion. Focus on robustness, control, and documentation.
*   **Key Features Added/Enhanced in v1.3:**
    *   **Code Structure Audit:** Removed deprecated modules, validated core imports.
    *   **LLM Fallback Logic:** Enhanced robustness in `llm_orchestrator` with sequential attempts and notifications.
    *   **Error Analysis System:** Implemented log monitoring, LLM-based analysis, fix suggestion (diff format), DB logging, optional auto-patching (`git apply`), and Telegram notifications.
    *   **Error Reporting Dashboard:** Added Streamlit UI (`dashboard/error_dashboard.py`) for viewing and filtering error reports.
    *   **Autopilot/Manual Control:** Implemented DB flag (`autopilot_enabled`) checked by `batch_runner` to bypass or require manual Telegram approval. Added helper script (`scripts/toggle_autopilot.py`).
*   **Skipped Features:**
    *   Telegram Control Panel Interface (Skipped due to technical issues).
*   **Known Issues/Placeholders:**
    *   Chartmetric API integration pending access verification.
    *   Suno API endpoint (`/generate`) may still have external issues.
    *   Intelligent LLM routing is basic.
    *   Several older modules (`metrics`, `video_processing`, `release_uploader`) need review/refactoring.
    *   Frontend UI is a basic placeholder.
    *   Video Editing / Trend Analysis services need integration into the main generation flow.
    *   Comprehensive unit/integration tests for new services are needed.
*   **Next Steps:** Validate environment variables and replace dummy tokens. Run final system boot test. Create final production report. Commit and push changes. Update remaining documentation (`CONTRIBUTION_GUIDE.md`, `dev_diary.md`, detailed module docs). Final testing and audit report.

For a detailed history, see `docs/development/dev_diary.md`.

