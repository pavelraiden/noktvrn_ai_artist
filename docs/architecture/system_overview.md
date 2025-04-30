# System Overview

## Introduction
The AI Artist Creation and Management System is a comprehensive platform designed to generate, manage, and evolve AI-powered virtual music artists. The system creates unique artist profiles with distinct personalities, musical styles, and visual identities, then manages their content creation, analyzes performance, and adapts based on data-driven insights.

## Core Architecture
The system follows a modular architecture with several key components designed to run within containers.

### 1. Artist Builder
Responsible for creating and evolving artist profiles. It handles:
- Profile generation and evolution using LLM-based pipelines (`ProfileEvolutionManager`)
- Schema validation and enforcement
- Storage and retrieval of artist profiles from the PostgreSQL database
- Management of artist evolution state
- Integration with self-learning, trend analysis, and strategic planning components
- Adaptation of content generation prompts (`PromptAdaptationPipeline`)

### 2. Artist Flow
Manages the operational lifecycle of artists, including:
- Content planning and scheduling
- Coordination of track generation (using Suno API via API Clients)
- Coordination of video content creation (using Pexels/Pixabay via API Clients)
- Social media presence management (future scope)
- Performance data collection coordination
*(Note: Role may be refined or merged in future refactoring.)*

### 3. LLM Orchestrator
Provides a unified interface for interacting with language models (currently OpenAI):
- Manages API connections to LLM providers (configured via environment variables).
- Handles specific generation tasks like evolving descriptions (`evolve_description`) and adapting prompts (`adapt_prompt`) based on provided context and instructions.
- Provides fallback mechanisms and error handling.
- Tracks token usage and performance metrics (future scope).

### 4. Audio Analysis System
Provides comprehensive audio analysis capabilities:
- Extraction of musical features (BPM, key, tempo, mood, energy, etc.) from generated tracks using Librosa.
- Storage of features in the PostgreSQL `tracks` table.
- Analysis of features for self-learning and style consistency.

### 5. Trend & Market Analysis System
Focuses on understanding the market and competitive landscape:
- **Competitor Analysis**: (`CompetitorTrendAnalyzer`) Analyzes competitor artists and tracks within specific genres using data from the database (populated via music platform APIs). Uses LLM to summarize strategies and identify market gaps.
- **Country Trend Analysis**: Analyzes genre trends, audience preferences, and performance metrics within specific countries using data from the database (populated via music platform APIs like Spotify Charts).
- **Self-Learning Analysis**: (`SelfLearningAnalyzer`) Analyzes the performance of the artist's own tracks (`performance_metrics` and `tracks` data) to identify success factors.
- Stores analysis results (competitor, country, self-learning) in the PostgreSQL database (`competitor_analysis`, `trend_analysis` tables).

### 6. Data Management
Handles all interactions with the PostgreSQL database:
- **Connection Management**: (`DatabaseConnectionManager`) Provides pooled connections to the database using `psycopg2`.
- **Schema Management**: Defines and manages database table structures (artist_profiles, tracks, performance_metrics, country_profiles, trend_analysis, competitor_analysis, evolution_plans) via SQL schema files and **Alembic** for migrations.
- **Data Access Layer**: Implemented within individual modules (e.g., `ProfileEvolutionManager`, `CompetitorTrendAnalyzer`) to handle CRUD operations for various system components.

### 7. API Clients
Provides standardized clients for interacting with external APIs:
- **Spotify Client**: Fetches chart data, artist/track info, and audio features.
- **(Future)** Apple Music Client.
- **(Existing)** Suno API, Pexels API, Pixabay API integrations (currently in `scripts/`, potential refactor target to move into `api_clients/`).

### 8. API Service (`api/main.py`)
Provides an interface (currently minimal) for interacting with the system, built using FastAPI. Exposes endpoints for potential future UI or external integrations. Includes instrumentation for Prometheus metrics.

### 9. Data Pipelines (`data_pipelines/`)
Responsible for orchestrating the collection, transformation, and loading (ETL) of data from external sources (like Spotify charts) into the PostgreSQL database.

## Data Flow & Evolution Loop
The system operates in a continuous feedback loop:
1.  **Content Generation**: Artist Flow coordinates content creation using Artist Builder profiles and LLM Orchestrator (with adapted prompts from `PromptAdaptationPipeline`).
2.  **Performance Data Collection**: Metrics (streams, engagement) are collected (source TBD - potentially via APIs or manual input initially) and stored in the PostgreSQL `performance_metrics` table.
3.  **Self-Learning Analysis**: `SelfLearningAnalyzer` processes `performance_metrics` and `tracks` data to identify success correlations, storing results in `trend_analysis`.
4.  **Market Data Collection**: API Clients (e.g., Spotify Client via `data_pipelines`) fetch chart data, competitor info, etc., populating `country_profiles` and `tracks` tables.
5.  **Market Analysis**: `CompetitorTrendAnalyzer` and country trend logic process external and internal data from the database, storing results in `competitor_analysis` and `trend_analysis`. LLM is used for summarization and gap identification.
6.  **Strategic Planning**: `ArtistEvolutionManager` and `CountryStrategyManager` synthesize insights from `trend_analysis`, `competitor_analysis`, and `country_profiles` to create `evolution_plans` (stored in DB).
7.  **Implementation**: `ProfileEvolutionManager` uses LLM to update `artist_profiles` (persona description) based on `evolution_plans` and enhanced context (performance, trends, history fetched from DB). `PromptAdaptationPipeline` uses LLM to adjust content generation prompts based on `evolution_plans` and context.
8.  The loop repeats with the generation of new, adapted content.

## Deployment Architecture & Technology Stack

- **Core Language**: Python 3.10+
- **API Framework**: FastAPI
- **Database**: PostgreSQL
- **DB Access**: psycopg2-binary
- **DB Migrations**: Alembic
- **AI APIs**: OpenAI (via `openai` library), Suno.ai
- **Data APIs**: Spotify API (via `spotipy`), Pexels API, Pixabay API, (Future: Apple Music API)
- **Audio Analysis**: Librosa, NumPy
- **Containerization**: Docker (`Dockerfile`, `docker-compose.yml` for local development)
- **CI/CD**: GitHub Actions (linting, testing, placeholder for image building/scanning)
- **Monitoring**: Prometheus (via `prometheus-fastapi-instrumentator`), Grafana
- **Logging**: Structured JSON logging (via `python-json-logger`)
- **Performance Testing**: Locust
- **Security Scanning**: Trivy (integrated into CI/CD - planned)
- **Deployment Scripts**: Bash scripts (`scripts/deployment/`) for build, migration, start.

## Scalability Considerations
The system is designed with scalability in mind:
- Modular architecture allows individual components (API, workers) to be scaled independently within containers.
- PostgreSQL offers robust scaling options (replication, partitioning), especially when using managed services.
- Connection pooling manages database resources efficiently.
- Asynchronous processing (`asyncio`) used for I/O-bound tasks (API calls, DB operations).
- Load balancing can be introduced in front of the API service instances in production.
- Caching mechanisms for frequently accessed data can be added.

## Security Model
- Environment-based configuration for sensitive credentials (API keys, DB passwords) via `.env` files (local) or secure secret management systems (production).
- Secure API key management within clients and orchestrator.
- Input validation and sanitization.
- Audit logging for critical operations.
- Standard PostgreSQL security features.
- Docker images built using non-root users.
- Automated vulnerability scanning (Trivy) planned for CI/CD.

Refer to the `/docs/deployment/` directory for detailed setup, configuration, troubleshooting, and production environment guides.
