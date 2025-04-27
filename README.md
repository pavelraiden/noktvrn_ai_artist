# AI Artist Creation and Management System

## Overview
The AI Artist Creation and Management System is a comprehensive platform for generating, validating, and managing AI-powered music artists. The system creates artist profiles, generates music tracks, produces content plans, and manages the entire lifecycle of AI artists.

## Key Features
- Artist identity and profile generation
- Track prompt generation and music creation
- Content planning and scheduling
- Trend analysis and adaptation
- Behavior management for artist personas
- Telegram preview system for content distribution
- Self-learning and optimization capabilities

## Architecture
The system follows a modular architecture with clear separation of concerns:

```
noktvrn_ai_artist/
├── artist_builder/       # Artist prompt creation, validation, profile assembly
│   ├── composer/         # Final artist profile construction
│   ├── integration/      # Integration with other modules
│   ├── prompts/          # Artist prompt design and generation
│   ├── tests/            # Unit and integration tests
│   └── validators/       # Quality checks and feedback loops
├── artist_flow/          # Artist creation workflow and asset management
│   ├── creator/          # Artist passport and identity creation
│   ├── generators/       # Various prompt generators (artist, track, video)
│   └── mocks/            # Mock implementations for testing
├── artists/              # Generated artist data and assets
├── llm_orchestrator/     # LLM session management and orchestration
│   └── tests/            # Orchestrator tests
├── scripts/              # Utility scripts for content and video generation
│   └── content/          # Content plan generation
├── templates/            # Template files for generation
└── video_gen_config/     # Video generation configuration
```

## Modules

### Artist Builder
Responsible for creating and validating artist profiles. See [artist_builder/README.md](./artist_builder/README.md) for detailed documentation.

### Artist Flow
Manages the workflow of artist creation, including asset management and prompt generation for various content types.

### LLM Orchestrator
Handles the orchestration of Large Language Models, managing sessions, and logging review history.

### Scripts
Utility scripts for content plan generation, asset fetching, and video generation.

## Self-Learning Principles
This system is designed with self-learning, self-adaptation, and self-optimization at its core:

1. **Self-Learning**: The system continuously learns from feedback and performance data to improve artist generation quality.

2. **Self-Adaptation**: Artists adapt their style and content based on trend analysis and audience engagement.

3. **Self-Optimization**: The system optimizes prompt generation and content creation processes based on historical performance.

## Getting Started

### Prerequisites
- Python 3.8+
- Required Python packages (see requirements.txt)
- Access to LLM APIs

### Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure environment variables

### Usage
Refer to individual module documentation for specific usage instructions.

## Contributing
Please read [CONTRIBUTION_GUIDE.md](./CONTRIBUTION_GUIDE.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is proprietary and confidential.
