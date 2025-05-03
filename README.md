# AI Artist Platform - Production Ready v1.5 (Pipeline Enhancements)

## Project Description

The AI Artist Platform is a comprehensive system designed to autonomously generate, manage, and evolve AI-powered virtual music artists. It creates unique artist identities, orchestrates content creation (music, visuals, voice), analyzes performance, and adapts based on data-driven insights and feedback, aiming to explore the potential of autonomous creative systems in the music industry.

## System Architecture (Phase 12 - v1.5)

The system employs a modular architecture focused on a continuous evolution loop. This version (v1.5) incorporates significant pipeline enhancements for improved content quality and robustness:

*   **Multi-Provider LLM Support:** Utilizes `llm_orchestrator` for interaction with DeepSeek, Gemini, Grok, Mistral, Anthropic, OpenAI (optional) with retry, enhanced fallback logic, and auto-discovery.
*   **API Integration:** Consistent use of environment variables (`.env`) for API keys (Music APIs, Video APIs, LLMs, Voice APIs, Telegram).
*   **Persistent Memory:** Artist profiles, performance history, and error reports are stored in a SQLite database (`data/artists.db`) managed by `services/artist_db_service.py`.
*   **Full Artist Lifecycle Management:** `services/artist_lifecycle_manager.py` manages artist states (`Candidate`, `Active`, `Evolving`, `Paused`, `Retired`) based on performance metrics.
*   **LLM Auto-Reflection:** The `batch_runner` prompts the LLM via the orchestrator to reflect on each generated piece.
*   **Enhanced Content Pipeline:**
    *   **Voice Synthesis (`VoiceService`):** Generates unique artist voice samples using ElevenLabs API (with mock fallback) upon artist creation.
    *   **Music Generation (`BeatService`):** Orchestrates music generation using primary (e.g., aimlapi.com) and alternative (e.g., Replicate MusicGen - mocked) APIs with fallback logic.
    *   **Audio Analysis (`AudioAnalyzer`):** Extracts tempo (BPM) and duration from generated music using Librosa.
    *   **Beat-Aligned Lyrics (`LyricsService`):** Generates lyrics using LLM, incorporating tempo and duration information from `AudioAnalyzer` into the prompt.
    *   **Audio Post-Processing (`ProductionService`):** Applies "humanization" effects like normalization and subtle noise overlay to generated audio using Pydub.
    *   **Video Selection:** Selects background videos using Pexels/Pixabay APIs.
*   **Basic Video Editing:** `services/video_editing_service.py` adds text overlays.
*   **Trend Analysis (Initial):** `services/trend_analysis_service.py` uses Twitter API for basic trend scoring.
*   **A/B Testing Framework:** Configurable framework in `batch_runner`.
*   **Telegram Integration:** Automated batch processing via `batch_runner` sends previews and processes approval/rejection feedback.
*   **Error Analysis & Auto-Fixing:** `services/error_analysis_service.py` monitors logs, uses LLMs for analysis/fix suggestions, logs reports to DB, optionally attempts auto-patching, and notifies via Telegram.
*   **Error Reporting Dashboard:** Streamlit app (`dashboard/error_dashboard.py`) to view error reports.
*   **Autopilot/Manual Control:** DB flag (`autopilot_enabled`) controls manual vs. automatic approval in `batch_runner`. Helper script (`scripts/toggle_autopilot.py`) available.
*   **Release Packaging:** `release_chain` prepares approved content runs.
*   **Security:** Hardcoded credentials removed, consistent use of `.env` and `.gitignore`.
*   **CI/CD:** GitHub Actions for code formatting checks.
*   **Frontend Foundation:** Basic Flask-based UI foundation in `frontend/`.

For a detailed breakdown, refer to:
*   `/ARTIST_FLOW.md` (Updated flow including new pipeline steps)
*   `/docs/artist_profile.md` (Details on profile structure and lifecycle states)
*   `/docs/development/dev_diary.md` (Chronological development log)
*   `/docs/architecture/` (Architecture diagrams and descriptions)
*   `/docs/modules/` (Documentation for specific services)

```mermaid
graph TD
    subgraph Configuration
        Env[".env File (API Keys, Settings, Lifecycle Thresholds)"]
    end

    subgraph Core Logic
        BatchRunner["Batch Runner (Automation, Lifecycle Trigger, A/B Test, Reflection, Autopilot Check, Pipeline Orchestration)"]
        LifecycleMgr["Artist Lifecycle Manager (State Mgt, Evolution, Retirement)"]
        Orchestrator["LLM Orchestrator (Multi-Provider, Enhanced Fallback)"]
        ArtistDB["Artist DB Service (SQLite - Artists, Errors, Autopilot Flag, Voice URL)"]
        BeatSvc["Beat Service (Music Gen Orchestration, Fallback)"]
        AudioAnalyzer["Audio Analyzer (Tempo/Duration Extraction)"]
        LyricsSvc["Lyrics Service (Beat-Aligned Generation)"]
        VoiceSvc["Voice Service (Voice Synthesis)"]
        ProdSvc["Production Service (Audio Humanization)"]
        VideoSelect["Video Selection Logic (in Batch Runner)"]
        VideoEdit["Video Editing Service (Overlays)"]
        TrendSvc["Trend Analysis Service (Twitter)"]
        TelegramSvc["Telegram Service (Notifications, Approval Feedback)"]
        ReleaseChain["Release Chain (Packaging)"]
        ErrorAnalyzer["Error Analysis Service (Log Monitor, LLM Analysis, Auto-Fix, DB Logging)"]
        ErrorDashboard["Error Dashboard (Streamlit UI)"]
        Frontend["Frontend UI (Flask - Basic)"]
    end

    subgraph External Services
        LLM_APIs["LLM APIs (DeepSeek, Gemini, ...)"]
        MusicAPIs["Music APIs (aimlapi, Replicate, ...)"]
        VideoAPIs["Video APIs (Pexels, Pixabay)"]
        VoiceAPI["Voice API (ElevenLabs)"]
        TwitterAPI["Twitter API (Trends)"]
        TelegramAPI["Telegram Bot API"]
        GitPlatform["Git Platform (Auto-Fixing)"]
    end

    subgraph Data
        SQLiteDB["data/artists.db (Profiles, History, Errors, Autopilot, Voice URL)"]
        Output["Output Directory (Releases, Status, Processed Audio)"]
        Logs["logs/ (Detailed Logs)"]
    end

    Env --> Orchestrator
    Env --> BatchRunner
    Env --> LifecycleMgr
    Env --> BeatSvc
    Env --> VoiceSvc
    Env --> ProdSvc
    Env --> VideoSelect
    Env --> TrendSvc
    Env --> TelegramSvc
    Env --> Frontend
    Env --> ArtistDB
    Env --> VideoEdit
    Env --> ErrorAnalyzer

    BatchRunner -- Triggers --> LifecycleMgr
    BatchRunner -- Uses --> ArtistDB
    BatchRunner -- Calls --> VoiceSvc # On artist creation
    BatchRunner -- Calls --> BeatSvc
    BatchRunner -- Calls --> LyricsSvc
    BatchRunner -- Calls --> VideoSelect
    BatchRunner -- Calls --> ProdSvc # Potentially
    BatchRunner -- Uses --> VideoEdit
    BatchRunner -- Uses --> TrendSvc
    BatchRunner -- Uses --> TelegramSvc
    BatchRunner -- Creates Releases --> ReleaseChain
    BatchRunner -- Logs Errors --> Logs

    BeatSvc -- Uses --> MusicAPIs
    BeatSvc -- Uses --> AudioAnalyzer
    LyricsSvc -- Uses --> Orchestrator
    VoiceSvc -- Uses --> VoiceAPI
    ProdSvc -- Processes Audio --> Output # Saves processed file

    LifecycleMgr -- Reads/Writes --> ArtistDB
    LifecycleMgr -- Uses --> Orchestrator

    Orchestrator -- API Calls --> LLM_APIs
    LLM_APIs -- Responses --> Orchestrator

    TrendSvc -- API Calls --> TwitterAPI
    TwitterAPI -- Responses --> TrendSvc

    TelegramSvc -- API Calls --> TelegramAPI
    TelegramAPI -- Updates/Commands --> TelegramSvc
    TelegramSvc -- Updates --> BatchRunner

    ArtistDB -- Reads/Writes --> SQLiteDB

    ReleaseChain -- Saves --> Output
    BatchRunner -- Saves Status --> Output

    ErrorAnalyzer -- Reads --> Logs
    ErrorAnalyzer -- Uses --> Orchestrator
    ErrorAnalyzer -- Interacts --> GitPlatform
    ErrorAnalyzer -- Notifies --> TelegramSvc
    ErrorAnalyzer -- Logs Reports --> ArtistDB

    ErrorDashboard -- Reads --> ArtistDB
```

## Directory Structure (Phase 12 - v1.5)

```
noktvrn_ai_artist/
├── .env                  # Local environment variables (DO NOT COMMIT)
├── .env.example          # Environment variables template
├── .github/              # GitHub Actions workflows (CI checks)
├── .gitignore
├── api_clients/          # Clients for external APIs (Music, Video, Base)
│   └── alt_music_client.py # NEW: Mockable alternative music client
├── batch_runner/         # Automated generation cycle runner (Lifecycle Trigger, Reflection, A/B Test, Autopilot, Pipeline Orchestration)
├── dashboard/            # Streamlit error reporting dashboard
│   └── error_dashboard.py
├── data/                 # Data storage directory
│   └── artists.db        # SQLite database for artist profiles, history, errors, autopilot status, voice_url
├── docs/                 # Documentation (Architecture, Development, System State, etc.)
│   ├── architecture/
│   ├── deployment/
│   ├── development/
│   ├── modules/          # Docs for specific services
│   ├── system_state/
│   └── artist_profile.md # Artist profile structure and lifecycle states
├── frontend/             # Basic Flask frontend UI foundation
│   ├── src/
│   ├── templates/
│   ├── requirements.txt
│   └── README.md
├── llm_orchestrator/     # Multi-provider LLM interaction handler (with enhanced fallback)
├── logs/                 # Log file output directory
├── metrics/              # Metrics logging and feedback analysis (Partially integrated into DB)
├── output/               # Default dir for generated outputs (run status, releases, processed audio)
├── release_chain/        # Logic for packaging approved runs into releases
├── release_uploader/     # Logic for preparing releases for upload/deployment (Placeholder)
├── requirements.txt      # Python dependencies for core system (includes streamlit, librosa, pydub, elevenlabs, replicate)
├── scripts/              # Utility & operational scripts
│   ├── boot_test.py
│   └── toggle_autopilot.py # Helper to toggle artist autopilot mode
├── services/             # Shared services
│   ├── artist_db_service.py # Manages SQLite database (artists, errors, voice_url)
│   ├── artist_lifecycle_manager.py # Manages artist lifecycle (creation, evolution, retirement)
│   ├── beat_service.py      # NEW: Orchestrates music generation and analysis
│   ├── error_analysis_service.py # Monitors logs, analyzes errors, attempts fixes
│   ├── lyrics_service.py    # NEW: Generates beat-aligned lyrics
│   ├── production_service.py # NEW: Applies audio post-processing (humanization)
│   ├── telegram_service.py  # Handles Telegram interactions (Notifications, Approval Feedback)
│   ├── trend_analysis_service.py # Analyzes trends (currently Twitter)
│   ├── video_editing_service.py # Adds overlays to videos
│   └── voice_service.py     # NEW: Generates artist voice samples
├── tests/                # Unit and integration tests
│   ├── api_clients/
│   └── services/
├── utils/                # Common utilities (retry decorator, health checker)
├── video_processing/     # Audio analysis and video selection logic
│   └── audio_analyzer.py  # NEW: Extracts tempo/duration using librosa
├── ARTIST_FLOW.md        # UPDATED: High-level artist lifecycle flow
├── boot_test.py          # Script to test core component imports/initialization
├── CONTRIBUTION_GUIDE.md # Contribution guidelines
└── README.md             # This file
```

## Setup and Usage

### Prerequisites

*   Python 3.11
*   Docker & Docker Compose (Recommended)
*   FFmpeg (Required for audio processing with pydub/librosa, install system-wide)
*   Git (Required for error auto-fixing)
*   API keys/credentials for: Music APIs (aimlapi, Replicate - optional), Video APIs (Pexels, Pixabay), LLMs (DeepSeek, Gemini, etc.), ElevenLabs (optional), Telegram Bot.
*   A specific Telegram Chat ID where the bot will operate.
*   (Optional) Twitter API access via Datasource for trend analysis.

### Environment Setup

1.  **Clone:** `git clone https://github.com/pavelraiden/noktvrn_ai_artist.git`
2.  **Navigate:** `cd noktvrn_ai_artist`
3.  **Configure `.env`:**
    *   Copy `.env.example` to `.env`.
    *   Fill in **all** required credentials (API keys, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OUTPUT_BASE_DIR`). Include `REPLICATE_API_TOKEN` and `ELEVENLABS_API_KEY` if using the live services (otherwise mocks will be used).
    *   Configure optional features like `AB_TESTING_ENABLED`, `AUTO_FIX_ENABLED`.
    *   Configure **Lifecycle Thresholds** (e.g., `PERFORMANCE_EVALUATION_PERIOD_DAYS`, `PAUSE_APPROVAL_RATE_THRESHOLD`, `RETIREMENT_CONSECUTIVE_REJECTIONS`). See `.env.example` for details.
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

## Project Status (Phase 12 - Pipeline Enhancements v1.5)

*   **Status:** Production Finalizer Pass - Pipeline Enhancements Implemented.
*   **Key Features Added/Enhanced in v1.5:**
    *   **Voice Synthesis:** Added `VoiceService` using ElevenLabs (mockable) for artist voice generation.
    *   **Music Gen Fallback:** Implemented `BeatService` with fallback logic (primary -> alternative/mock).
    *   **Audio Analysis:** Added `AudioAnalyzer` using Librosa for tempo/duration extraction.
    *   **Beat-Aligned Lyrics:** Updated `LyricsService` to use tempo/duration in prompts.
    *   **Audio Humanization:** Added `ProductionService` using Pydub for normalization and noise overlay.
    *   **Database Schema:** Added `voice_url` column to artists table.
    *   **Documentation:** Updated `ARTIST_FLOW.md` and `README.md`.
*   **Known Issues/Placeholders:**
    *   **API Keys:** Requires `REPLICATE_API_TOKEN` and `ELEVENLABS_API_KEY` for full functionality (currently uses mocks).
    *   **aimlapi.com Issues:** Primary music generation API (aimlapi.com) was previously unreliable; `BeatService` now includes fallback but primary path needs testing.
    *   **Integration:** `ProductionService` output (processed audio) is not yet fully integrated into the final video/release chain.
    *   Video Editing / Trend Analysis services need deeper integration.
    *   Comprehensive unit/integration tests for new services are needed.
*   **Next Steps:** Commit documentation updates. Perform full end-to-end validation of the enhanced pipeline (using mocks where necessary). Prepare production readiness report.

For a detailed history, see `docs/development/dev_diary.md`.

