# AI Artist Creation and Management System

## What is this project?

The AI Artist Creation and Management System is a comprehensive platform for generating, managing, and evolving AI-powered virtual music artists. The system creates complete artist identities with unique personalities, musical styles, and visual aesthetics, then manages their content creation and evolution based on trend analysis and audience feedback.

This platform enables the automated creation and management of virtual artists who can produce music, videos, and social media content while evolving their style and behavior over time based on performance metrics and industry trends.

## Core System Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │     │                     │
│  Artist Creation    │────▶│  Content Planning   │────▶│  Content Generation │
│                     │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         ▲                            ▲                            │
         │                            │                            │
         │                            │                            ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │     │                     │
│  Behavior Evolution │◀────│  Feedback Analysis  │◀────│  Content Publishing │
│                     │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Key Components:

1. **Artist Profile Creation**
   - Generates complete artist identities with personality, style, and visual aesthetics
   - Creates coherent backstories and musical direction
   - Establishes target audience and market positioning

2. **Trend Analysis**
   - Monitors music industry trends across genres and platforms
   - Analyzes successful artist behaviors and content strategies
   - Identifies emerging opportunities and audience preferences

3. **Content Planning**
   - Schedules releases based on optimal timing and market conditions
   - Plans content themes and narrative arcs for artist development
   - Coordinates cross-platform content strategy

4. **Behavior Evolution**
   - Adapts artist personas based on performance metrics
   - Evolves musical style while maintaining core identity
   - Implements gradual, organic growth in artist capabilities

5. **Release Scheduling**
   - Manages timing of music, video, and social content releases
   - Coordinates promotional activities across platforms
   - Optimizes release cadence based on audience engagement

6. **Video Teaser Generation**
   - Creates visual content aligned with artist identity
   - Generates promotional videos for music releases
   - Maintains consistent visual aesthetic across content

7. **Distribution to Streaming Platforms**
   - Prepares content for distribution to music platforms
   - Manages metadata and publishing information
   - Tracks performance across distribution channels

![System Architecture](https://mermaid.ink/img/pako:eNqVVMtu2zAQ_BWCpxbIH9hADj20QA89FD0UvdCUtUYtRQqkZMco_O9dUnIcO3aKwhdxd2Z2OLvkK1eqQZ7xVbdQGrQPaI3QDR5sK6XBe9wgfEJdCYUwx1Yb1JYcYIGNkPAEtWgFwmfRrLHBBjSCNQiVsOh0C1_QgFUKjNWwQwu6hVIoC1ZpVLCFUhkBX0GJGmEpLDxgLVRbgxGtgkbXsAMjLCyxEQq-o5FCwQKVqOEeKtSyBdVqaLQxYMFIBQvdoLLwqJWAH6JBWMEDGl3BHVrRKKhFLRvYCYsGdgKhEhLu0VZCwwKkqOAWS9GgBKNbDVJbC0ZLBQtRo7TwXUsJP7FGWMIdGlXBLRpRK6hEJRvYCgMGtgKgFApu0ZRCwRyEKOEGC1GjAK0aBVJZA1pJBXNRobBwp6WEe6wRFnCDRpZwg1pUCkpRygY2QoOBjQDIhYQbNIWQMIe5KOAaC1GhAKUaCVIaA0pKBXNRorBwq6WEH1ghzOEajSjgGpUoFRSikA2shQYDawGQCQnXaHIhYQ4zkcM3zEWJApSsJUhhDCgpFcxEgcLCtZYSfmKFMINrNDKHa1QilzAXuWxgJTQYWAmATEi4QpMJCTOYihy-Yi5yFKBkLUEKY0BJqWAmchQWrrSU8AsrhCu4QiMzuEIlMgkzkckGlkKDgaUAyISEKzSZkDCFqcjgC-YiQwFKVhKkMAaUlAqmIkNh4VJLCb-xQriESzQyhUvUIpUwE6lsYCE0GFgIgExIuESTCQlTmIgUPmMuUhSgZClBCmNASalgIlIUFs61lPAHK4RzuEQjErhELRIJU5HIBmZCg4GZAMiEhAs0mZAwhYlI4BPmIkEBShYSpDAGlJQKJiJBYeFMSwl_sUI4gws0IoYL1CKWMBWxbGAqNBiYCoBMSDhHkwkJU5iIGD5iLmIUoGQuQQpjQEmpYCJiFBZOtZTwDyuEU7hAI2ZwgVrMJEzFTDYwERoMTARAJiSco8mEhClMxAw-YC5mKECJmQQpjAElpYKJmKGwcKKlhP9YIZzAORoxgXPUYiJhKiaygbHQYGAsADIh4QxNJiRM4URM4B3mYoIClBhLkMIYUFIqOBFjFBaOtZTwHyuEYzhDI8ZwhloUEqaikA2MhAYDIwGQCQmnaHIhYQpHYgRvMRcjFKDESIIUxoCSUsGRGKGwcKSlhP9YIRzBKRoxglPUYiRhKkaygaHQYGAoAHIh4QRNLiRM4UgM4Q3mYogClBhKkMIYUFIqOBRDFBYOtZTwHyuEQzhBI4ZwglrMJUzFXDYwEBoMDARALiQco8mFhCkciCG8wlwMUYASAwlSGANKSgUHYojCwoGWEv5jhXAAx2jEAI5Ri4GEqRjIBvpCg4G-AMiFhCM0uZAwhb7ow0vMRR8FKNGXIIUxoKRU0Bd9FBb2tZTwHyuEfThCI_pwBLXoS5iKvmygJzQY6AmAXEg4RJMLCVPoiR68wFz0UIASPQlSGANKSgU90UNhYU9LCf-xQtiDQzSiB4eoxUDCVAxkA32hwUBfAORCwgGaXEiYQl_04TnmYogClOhLkMIYUFIq6Is-Cgu7Wkr4jxXCLhygET04QC0GEqZiIBvoCw0G-gIgFxL20eRCwhT6YgBPMRcDFKBEX4IUxoCSUkFfDFBY2NFSwn-sEHbgHRrRgXeoxUDCVAxkA32hwUBfAORCwh6aXEiYQl8M4DHmYoAClOhLkMIYUFIq6IsBCgvbWkr4jxXCNrxFI7bhLWoxkDAVA9lAX2gw0BcAuZCwhSYXEqbQFwN4hLkYoAAl-hKkMAaUlAr6YoDCwpaWEv5jhbAFb9CILXiDWgwkTMVANtAXGgz0BUAuJGyiyYWEKfTFAB5iLgYoQIm-BCmMASWlgr4YoLCwoaWE_1ghbMA-GrEB-6jFQMJUDGQDfaHBQF8A5ELCBppcSJhCXwzgAeZigAKU6EuQwhhQUiroiwEKC-taSviPFcI6vEYj1uE1ajGQMBUD2UBfaDDQFwC5kLCGJhcSptAXA7iPuRigACX6EqQwBpSUCvpigMLCqpYS_mOFsAqv0IhVeIVaDCRMxUA20BcaDPQFQC4krKLJhYQp9MUA7mEuBihAib4EKYwBJaWCvhigsLCipYT_WCGswEs0YgVeohYDCVMxkA30hQYDfQGQCwkraHIhYQp9MYC7mIsBClCiL0EKY0BJqaAvBigsLGsp4T9WCMvwAo1YhheoxUDCVAxkA32hwUBfAORCwjKaXEiYQl8M4A7mYoAClOhLkMIYUFIq6IsBCgtLWkr4jxXCEjxHI5bgOWoxkDAVA9lAX2gw0BcAuZCwhCYXEqbQFwO4jbkYoAAl-hKkMAaUlAr6YoDCwqKWEv5jhbAIT9GIRXiKWgwkTMVANtAXGgz0BUAuJCyiyYWEKfTFAG5hLgYoQIm-BCmMASWlgr4YoLCwoKWE_1ghLMBjNGIBHqMWAwlTMZAN9IUGA30BkAsJC2hyIWEKfTGAm5iLAQpQoi9BCmNASamgLwYoLMxrKeE_VgjzcIRGzMMRajGQMBUD2UBfaDDQFwC5kDCPJhcSptAXA7iBuRigACX6EqQwBpSUCvpigMLCnJYS_mOFMAeHaMQcHKIWAwlTMZAN9IUGA30BkAsJc2hyIWEKfTGAa5iLAQpQoi9BCmNASamgLwYoLMxqKeE_VgizMEMjZmGGWgwkTMVANtAXGgz0BUAuJMyiyYWEKfTFAK5iLgYoQIm-BCmMASWlgr4YoLAwraWE_1ghTMMBGjENB6jFQMJUDGQDfaHBQF8A5ELCNJpcSJhCXwzgCuZigAKU6EuQwhhQUiroiwEKC1NaSviPFcIU7KMRUzBFLQYSpmIgG-gLDQb6AiAXEqbQ5ELCFPpiAJcwFwMUoERfghTGgJJSQV8MUFiY1FLCf6wQJmEPjZiEPdRiIGEqBrKBvtBgoC8AciFhEk0uJEyhLwZwAXMxQAFK9CVIYQwoKRX0xQCFhQktJfzHCmEC3qERE_AOtRhImIqBbKAvNBjoC4BcSJhAkwsJU-iLAZzDXAxQgBJ9CVIYg_9KSgV9MUBhYVxLCf-xQhiHt2jEOLxFLQYSpmIgG-gLDQb6AiAXEsbR5ELCFPpiAGcwFwMUoERfghTGgJJSQV8MUFgY01LCf6wQxuANGjEGb1CLgYSpGMgG-kKDgb4AyIWEMTS5kDCFvhjAKczFAAUo0ZcghTGgpFTQFwMUFka1lPAfK4RReI1GjMJr1GIgYSoGsoG-0GCgLwByIWEUTS4kTKEvBnACczFAAUr0JUhhDCgpFfTFAIWFES0l_McKYQReohEj8BK1GEiYioFsoC80GOgLgFxIGEGTCwlT6IsBHMNcDFCAEn0JUhgDSkoFfTFAYWFYSwn_sUIYhhdoxDA8Ry0GEqZiIBvoCw0G-gIgFxKG0eRCwhT6YgCHMBcDFKBEX4IUxoCSUkFfDFBYGNJSwn-sEIbgGRoxBM9Qi4GEqRjIBvpCg4G-AMiFhCE0uZAwhb4YwAHMxQAFKNGXIIUxoKRU0BcDFBYGtZTwHyuEQXiKRgzCU9RiIGEqBrKBvtBgoC8AciFhEE0uJEyhLwawD3MxQAFK9CVIYQwoKRX0xQCFhQEtJfzHCmEAnqARAwBQi4GEqRjIBvpCg4G-AMiFhAE0uZAwhb4YwB7MxQAFKNGXIIUxoKRU0BcDFBb6Wkr4jxVCH-6jEX24j1oMJEzFQDbQFxoM9AVALiT00eRCwhT6YgC7MBcDFKBEX4IUxoCSUkFfDFBY6Gkp4T9WCD24h0b04B5qMZAwFQPZQF9oMNAXALmQ0EOTCwlT6IsB7MBcDFCAEn0JUhgDSkoFfTFAYaGrpYT_WCF04S4a0YW7qMVAwlQMZAN9ocFAXwDkQkIXTS4kTKEvBrANczFAAUr0JUhhDCgpFfTFAIWFjpYS_mOF0IHbaEQHbqMWAwlTMZAN9IUGA30BkAsJHTS5kDCFvhjAFszFAAUo0ZcghTGgpFTQFwMUFtpaSviPFUIbbqERbbiF2v9_AwAA__-Ov5Ib)

## Technologies Used

The AI Artist Creation and Management System leverages several key technologies:

- **FastAPI**: Backend API framework for high-performance endpoints
- **PostgreSQL**: Database for storing artist profiles, content plans, and performance metrics
- **Redis**: Caching and message queue for system coordination
- **Suno.ai API**: AI music generation service
- **Leonardo.ai**: AI image and video generation
- **OpenAI API**: Large language models for content creation and decision making
- **AWS S3**: Storage for generated assets and content
- **Docker**: Containerization for consistent deployment
- **Kubernetes**: Orchestration for scaling and managing services
- **Prometheus/Grafana**: Monitoring and metrics visualization
- **ELK Stack**: Logging and analysis

## Modules

### Artist Builder
Responsible for creating and validating artist profiles. The module includes:
- **Composer**: Creates and assembles artist profiles
- **Integration**: Handles integration with other modules
- **Prompts**: Designs prompts for artist creation
- **Schema**: Defines and validates artist profile structure
- **Tests**: Contains test cases for artist creation
- **Validators**: Validates prompts and checks feedback loops

### Artist Flow
Manages the workflow of artist creation, including asset management and prompt generation for various content types:
- **Creator**: Generates artist passports and identities
- **Generators**: Creates prompts for artists, tracks, and videos
- **Mocks**: Contains mock implementations for testing

### LLM Orchestrator
Handles the orchestration of Large Language Models, managing sessions, and logging review history:
- **LLM Interface**: Defines interfaces for LLM interactions
- **Orchestrator**: Manages LLM request orchestration
- **Session Manager**: Handles LLM session state
- **Review Logger**: Logs and analyzes LLM interactions

### Scripts
Utility scripts for content plan generation, asset fetching, and video generation:
- **Content**: Generates content plans and schedules
- **Fetch Assets**: Retrieves assets from external sources
- **Video Generator**: Creates video content

## Self-Learning Principles
This system is designed with self-learning, self-adaptation, and self-optimization at its core:

1. **Self-Learning**: The system continuously learns from feedback and performance data to improve artist generation quality.
2. **Self-Adaptation**: Artists adapt their style and content based on trend analysis and audience engagement.
3. **Self-Optimization**: The system optimizes prompt generation and content creation processes based on historical performance.

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 13+
- Redis 6+
- Docker and Docker Compose
- API keys for OpenAI, Suno.ai, and Leonardo.ai
- AWS S3 credentials (or compatible storage service)

### Environment Setup
The system requires several environment variables to be configured:

```
# Core settings
DEFAULT_CALENDAR_LENGTH=30
DEFAULT_LANG=en

# Artist generation database paths
ARTIST_GENRE_DB_PATH=/path/to/genre/database
ARTIST_VISUAL_DB_PATH=/path/to/visual/database

# Track generation database paths
TRACK_GENRE_DB_PATH=/path/to/track/genre/database
TRACK_MOOD_DB_PATH=/path/to/track/mood/database
TRACK_TEMPO_DB_PATH=/path/to/track/tempo/database

# Video generation database paths
VIDEO_STYLE_DB_PATH=/path/to/video/style/database
VIDEO_FOOTAGE_DB_PATH=/path/to/video/footage/database
VIDEO_EFFECTS_DB_PATH=/path/to/video/effects/database
VIDEO_TRENDS_DB_PATH=/path/to/video/trends/database

# External API keys
PIXABAY_KEY=your_pixabay_api_key
PEXELS_KEY=your_pexels_api_key
OPENAI_API_KEY=your_openai_api_key
SUNO_API_KEY=your_suno_api_key
LEONARDO_API_KEY=your_leonardo_api_key

# Database configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_artist_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# AWS S3 configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
S3_BUCKET_NAME=ai-artist-assets
```

### Installation

#### Local Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-artist-system.git
   cd ai-artist-system
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Copy environment variables
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your configuration

6. Initialize the database
   ```bash
   python scripts/init_db.py
   ```

7. Run the development server
   ```bash
   uvicorn app.main:app --reload
   ```

#### Docker Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-artist-system.git
   cd ai-artist-system
   ```

2. Copy environment variables
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your configuration

3. Build and start the containers
   ```bash
   docker-compose up -d
   ```

4. Access the API at http://localhost:8000

### Usage

#### Creating a New Artist

1. Generate an artist profile
   ```bash
   python -m scripts.create_artist --prompt "A mysterious electronic music producer with dark, atmospheric soundscapes and minimal public presence"
   ```

2. View generated artist profile
   ```bash
   python -m scripts.view_artist --id <artist_id>
   ```

3. Generate content for the artist
   ```bash
   python -m scripts.generate_content --artist_id <artist_id> --content_type track
   ```

4. Create a content plan
   ```bash
   python -m scripts.create_content_plan --artist_id <artist_id> --duration 90
   ```

#### API Endpoints

The system provides a RESTful API for integration with other services:

- `POST /api/artists`: Create a new artist
- `GET /api/artists/{artist_id}`: Get artist details
- `POST /api/artists/{artist_id}/content`: Generate content for an artist
- `GET /api/artists/{artist_id}/content`: List artist content
- `POST /api/artists/{artist_id}/plan`: Create a content plan
- `GET /api/artists/{artist_id}/plan`: Get artist content plan
- `POST /api/artists/{artist_id}/evolve`: Trigger artist evolution

## Production Readiness
The system is designed to be production-ready with:
- Scalability for multiple artists
- Flexible LLM integration
- External API support
- Comprehensive error handling
- Logging and monitoring

For a detailed production readiness assessment, see the [Production Readiness Assessment](./docs/production_readiness.md).

## Contributing
Please read [CONTRIBUTION_GUIDE.md](./CONTRIBUTION_GUIDE.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is proprietary and confidential.
