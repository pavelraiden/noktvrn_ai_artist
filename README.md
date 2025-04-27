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

## System Architecture
The system follows a modular architecture with clear separation of concerns:

![System Architecture](https://mermaid.ink/img/pako:eNqVVMtu2zAQ_BWCpxbIH9hADj20QA89FD0UvdCUtUYtRQqkZMco_O9dUnIcO3aKwhdxd2Z2OLvkK1eqQZ7xVbdQGrQPaI3QDR5sK6XBe9wgfEJdCYUwx1Yb1JYcYIGNkPAEtWgFwmfRrLHBBjSCNQiVsOh0C1_QgFUKjNWwQwu6hVIoC1ZpVLCFUhkBX0GJGmEpLDxgLVRbgxGtgkbXsAMjLCyxEQq-o5FCwQKVqOEeKtSyBdVqaLQxYMFIBQvdoLLwqJWAH6JBWMEDGl3BHVrRKKhFLRvYCYsGdgKhEhLu0VZCwwKkqOAWS9GgBKNbDVJbC0ZLBQtRo7TwXUsJP7FGWMIdGlXBLRpRK6hEJRvYCgMGtgKgFApu0ZRCwRyEKOEGC1GjAK0aBVJZA1pJBXNRobBwp6WEe6wRFnCDRpZwg1pUCkpRygY2QoOBjQDIhYQbNIWQMIe5KOAaC1GhAKUaCVIaA0pKBXNRorBwq6WEH1ghzOEajSjgGpUoFRSikA2shQYDawGQCQnXaHIhYQ4zkcM3zEWJApSsJUhhDCgpFcxEgcLCtZYSfmKFMINrNDKHa1QilzAXuWxgJTQYWAmATEi4QpMJCTOYihy-Yi5yFKBkLUEKY0BJqWAmchQWrrSU8AsrhCu4QiMzuEIlMgkzkckGlkKDgaUAyISEKzSZkDCFqcjgC-YiQwFKVhKkMAaUlAqmIkNh4VJLCb-xQriESzQyhUvUIpUwE6lsYCE0GFgIgExIuESTCQlTmIgUPmMuUhSgZClBCmNASalgIlIUFs61lPAHK4RzuEQjErhELRIJU5HIBmZCg4GZAMiEhAs0mZAwhYlI4BPmIkEBShYSpDAGlJQKJiJBYeFMSwl_sUI4gws0IoYL1CKWMBWxbGAqNBiYCoBMSDhHkwkJU5iIGD5iLmIUoGQuQQpjQEmpYCJiFBZOtZTwDyuEU7hAI2ZwgVrMJEzFTDYwERoMTARAJiSco8mEhClMxAw-YC5mKECJmQQpjAElpYKJmKGwcKKlhP9YIZzAORoxgXPUYiJhKiaygbHQYGAsADIh4QxNJiRM4URM4B3mYoIClBhLkMIYUFIqOBFjFBaOtZTwHyuEYzhDI8ZwhloUEqaikA2MhAYDIwGQCQmnaHIhYQpHYgRvMRcjFKDESIIUxoCSUsGRGKGwcKSlhP9YIRzBKRoxglPUYiRhKkaygaHQYGAoAHIh4QRNLiRM4UgM4Q3mYogClBhKkMIYUFIqOBRDFBYOtZTwHyuEQzhBI4ZwglrMJUzFXDYwEBoMDARALiQco8mFhCkciCG8wlwMUYASAwlSGANKSgUHYojCwoGWEv5jhXAAx2jEAI5Ri4GEqRjIBvpCg4G-AMiFhCM0uZAwhb7ow0vMRR8FKNGXIIUxoKRU0Bd9FBb2tZTwHyuEfThCI_pwBLXoS5iKvmygJzQY6AmAXEg4RJMLCVPoiR68wFz0UIASPQlSGANKSgU90UNhYU9LCf-xQtiDQzSiB4eoxUDCVAxkA32hwUBfAORCwgGaXEiYQl_04TnmYogClOhLkMIYUFIq6Is-Cgu7Wkr4jxXCLhygET04QC0GEqZiIBvoCw0G-gIgFxL20eRCwhT6YgBPMRcDFKBEX4IUxoCSUkFfDFBY2NFSwn-sEHbgHRrRgXeoxUDCVAxkA32hwUBfAORCwh6aXEiYQl8M4DHmYoAClOhLkMIYUFIq6IsBCgvbWkr4jxXCNrxFI7bhLWoxkDAVA9lAX2gw0BcAuZCwhSYXEqbQFwN4hLkYoAAl-hKkMAaUlAr6YoDCwpaWEv5jhbAFb9CILXiDWgwkTMVANtAXGgz0BUAuJGyiyYWEKfTFAB5iLgYoQIm-BCmMASWlgr4YoLCwoaWE_1ghbMA-GrEB-6jFQMJUDGQDfaHBQF8A5ELCBppcSJhCXwzgAeZigAKU6EuQwhhQUiroiwEKC-taSviPFcI6vEYj1uE1ajGQMBUD2UBfaDDQFwC5kLCGJhcSptAXA7iPuRigACX6EqQwBpSUCvpigMLCqpYS_mOFsAqv0IhVeIVaDCRMxUA20BcaDPQFQC4krKLJhYQp9MUA7mEuBihAib4EKYwBJaWCvhigsLCipYT_WCGswEs0YgVeohYDCVMxkA30hQYDfQGQCwkraHIhYQp9MYC7mIsBClCiL0EKY0BJqaAvBigsLGsp4T9WCMvwAo1YhheoxUDCVAxkA32hwUBfAORCwjKaXEiYQl8M4A7mYoAClOhLkMIYUFIq6IsBCgtLWkr4jxXCEjxHI5bgOWoxkDAVA9lAX2gw0BcAuZCwhCYXEqbQFwO4jbkYoAAl-hKkMAaUlAr6YoDCwqKWEv5jhbAIT9GIRXiKWgwkTMVANtAXGgz0BUAuJCyiyYWEKfTFAG5hLgYoQIm-BCmMASWlgr4YoLCwoKWE_1ghLMBjNGIBHqMWAwlTMZAN9IUGA30BkAsJC2hyIWEKfTGAm5iLAQpQoi9BCmNASamgLwYoLMxrKeE_VgjzcIRGzMMRajGQMBUD2UBfaDDQFwC5kDCPJhcSptAXA7iBuRigACX6EqQwBpSUCvpigMLCnJYS_mOFMAeHaMQcHKIWAwlTMZAN9IUGA30BkAsJc2hyIWEKfTGAa5iLAQpQoi9BCmNASamgLwYoLMxqKeE_VgizMEMjZmGGWgwkTMVANtAXGgz0BUAuJMyiyYWEKfTFAK5iLgYoQIm-BCmMASWlgr4YoLAwraWE_1ghTMMBGjENB6jFQMJUDGQDfaHBQF8A5ELCNJpcSJhCXwzgCuZigAKU6EuQwhhQUiroiwEKC1NaSviPFcIU7KMRUzBFLQYSpmIgG-gLDQb6AiAXEqbQ5ELCFPpiAJcwFwMUoERfghTGgJJSQV8MUFiY1FLCf6wQJmEPjZiEPdRiIGEqBrKBvtBgoC8AciFhEk0uJEyhLwZwAXMxQAFK9CVIYQwoKRX0xQCFhQktJfzHCmEC3qERE_AOtRhImIqBbKAvNBjoC4BcSJhAkwsJU-iLAZzDXAxQgBJ9CVIYg_9KSgV9MUBhYVxLCf-xQhiHt2jEOLxFLQYSpmIgG-gLDQb6AiAXEsbR5ELCFPpiAGcwFwMUoERfghTGgJJSQV8MUFgY01LCf6wQxuANGjEGb1CLgYSpGMgG-kKDgb4AyIWEMTS5kDCFvhjAKczFAAUo0ZcghTGgpFTQFwMUFka1lPAfK4RReI1GjMJr1GIgYSoGsoG-0GCgLwByIWEUTS4kTKEvBnACczFAAUr0JUhhDCgpFfTFAIWFES0l_McKYQReohEj8BK1GEiYioFsoC80GOgLgFxIGEGTCwlT6IsBHMNcDFCAEn0JUhgDSkoFfTFAYWFYSwn_sUIYhhdoxDA8Ry0GEqZiIBvoCw0G-gIgFxKG0eRCwhT6YgCHMBcDFKBEX4IUxoCSUkFfDFBYGNJSwn-sEIbgGRoxBM9Qi4GEqRjIBvpCg4G-AMiFhCE0uZAwhb4YwAHMxQAFKNGXIIUxoKRU0BcDFBYGtZTwHyuEQXiKRgzCU9RiIGEqBrKBvtBgoC8AciFhEE0uJEyhLwawD3MxQAFK9CVIYQwoKRX0xQCFhQEtJfzHCmEAnqARAwBQi4GEqRjIBvpCg4G-AMiFhAE0uZAwhb4YwB7MxQAFKNGXIIUxoKRU0BcDFBb6Wkr4jxVCH-6jEX24j1oMJEzFQDbQFxoM9AVALiT00eRCwhT6YgC7MBcDFKBEX4IUxoCSUkFfDFBY6Gkp4T9WCD24h0b04B5qMZAwFQPZQF9oMNAXALmQ0EOTCwlT6IsB7MBcDFCAEn0JUhgDSkoFfTFAYaGrpYT_WCF04S4a0YW7qMVAwlQMZAN9ocFAXwDkQkIXTS4kTKEvBrANczFAAUr0JUhhDCgpFfTFAIWFjpYS_mOF0IHbaEQHbqMWAwlTMZAN9IUGA30BkAsJHTS5kDCFvhjAFszFAAUo0ZcghTGgpFTQFwMUFtpaSviPFUIbbqERbbiF2v9_AwAA__-Ov5Ib)

```
noktvrn_ai_artist/
├── artist_builder/       # Artist prompt creation, validation, profile assembly
│   ├── composer/         # Final artist profile construction
│   ├── integration/      # Integration with other modules
│   ├── prompts/          # Artist prompt design and generation
│   ├── schema/           # Artist profile schema definition and validation
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

## Artist Lifecycle
The system manages the complete lifecycle of AI artists as shown in the flowchart below:

![Artist Lifecycle](https://mermaid.ink/img/pako:eNqVVMtu2zAQ_BWCpxbIH9hADj20QA89FD0UvdCUtUYtRQqkZMco_O9dUnIcO3aKwhdxd2Z2OLvkK1eqQZ7xVbdQGrQPaI3QDR5sK6XBe9wgfEJdCYUwx1Yb1JYcYIGNkPAEtWgFwmfRrLHBBjSCNQiVsOh0C1_QgFUKjNWwQwu6hVIoC1ZpVLCFUhkBX0GJGmEpLDxgLVRbgxGtgkbXsAMjLCyxEQq-o5FCwQKVqOEeKtSyBdVqaLQxYMFIBQvdoLLwqJWAH6JBWMEDGl3BHVrRKKhFLRvYCYsGdgKhEhLu0VZCwwKkqOAWS9GgBKNbDVJbC0ZLBQtRo7TwXUsJP7FGWMIdGlXBLRpRK6hEJRvYCgMGtgKgFApu0ZRCwRyEKOEGC1GjAK0aBVJZA1pJBXNRobBwp6WEe6wRFnCDRpZwg1pUCkpRygY2QoOBjQDIhYQbNIWQMIe5KOAaC1GhAKUaCVIaA0pKBXNRorBwq6WEH1ghzOEajSjgGpUoFRSikA2shQYDawGQCQnXaHIhYQ4zkcM3zEWJApSsJUhhDCgpFcxEgcLCtZYSfmKFMINrNDKHa1QilzAXuWxgJTQYWAmATEi4QpMJCTOYihy-Yi5yFKBkLUEKY0BJqWAmchQWrrSU8AsrhCu4QiMzuEIlMgkzkckGlkKDgaUAyISEKzSZkDCFqcjgC-YiQwFKVhKkMAaUlAqmIkNh4VJLCb-xQriESzQyhUvUIpUwE6lsYCE0GFgIgExIuESTCQlTmIgUPmMuUhSgZClBCmNASalgIlIUFs61lPAHK4RzuEQjErhELRIJU5HIBmZCg4GZAMiEhAs0mZAwhYlI4BPmIkEBShYSpDAGlJQKJiJBYeFMSwl_sUI4gws0IoYL1CKWMBWxbGAqNBiYCoBMSDhHkwkJU5iIGD5iLmIUoGQuQQpjQEmpYCJiFBZOtZTwDyuEU7hAI2ZwgVrMJEzFTDYwERoMTARAJiSco8mEhClMxAw-YC5mKECJmQQpjAElpYKJmKGwcKKlhP9YIZzAORoxgXPUYiJhKiaygbHQYGAsADIh4QxNJiRM4URM4B3mYoIClBhLkMIYUFIqOBFjFBaOtZTwHyuEYzhDI8ZwhloUEqaikA2MhAYDIwGQCQmnaHIhYQpHYgRvMRcjFKDESIIUxoCSUsGRGKGwcKSlhP9YIRzBKRoxglPUYiRhKkaygaHQYGAoAHIh4QRNLiRM4UgM4Q3mYogClBhKkMIYUFIqOBRDFBYOtZTwHyuEQzhBI4ZwglrMJUzFXDYwEBoMDARALiQco8mFhCkciCG8wlwMUYASAwlSGANKSgUHYojCwoGWEv5jhXAAx2jEAI5Ri4GEqRjIBvpCg4G-AMiFhCM0uZAwhb7ow0vMRR8FKNGXIIUxoKRU0Bd9FBb2tZTwHyuEfThCI_pwBLXoS5iKvmygJzQY6AmAXEg4RJMLCVPoiR68wFz0UIASPQlSGANKSgU90UNhYU9LCf-xQtiDQzSiB4eoxUDCVAxkA32hwUBfAORCwgGaXEiYQl_04TnmYogClOhLkMIYUFIq6Is-Cgu7Wkr4jxXCLhygET04QC0GEqZiIBvoCw0G-gIgFxL20eRCwhT6YgBPMRcDFKBEX4IUxoCSUkFfDFBY2NFSwn-sEHbgHRrRgXeoxUDCVAxkA32hwUBfAORCwh6aXEiYQl8M4DHmYoAClOhLkMIYUFIq6IsBCgvbWkr4jxXCNrxFI7bhLWoxkDAVA9lAX2gw0BcAuZCwhSYXEqbQFwN4hLkYoAAl-hKkMAaUlAr6YoDCwpaWEv5jhbAFb9CILXiDWgwkTMVANtAXGgz0BUAuJGyiyYWEKfTFAB5iLgYoQIm-BCmMASWlgr4YoLCwoaWE_1ghbMA-GrEB-6jFQMJUDGQDfaHBQF8A5ELCBppcSJhCXwzgAeZigAKU6EuQwhhQUiroiwEKC-taSviPFcI6vEYj1uE1ajGQMBUD2UBfaDDQFwC5kLCGJhcSptAXA7iPuRigACX6EqQwBpSUCvpigMLCqpYS_mOFsAqv0IhVeIVaDCRMxUA20BcaDPQFQC4krKLJhYQp9MUA7mEuBihAib4EKYwBJaWCvhigsLCipYT_WCGswEs0YgVeohYDCVMxkA30hQYDfQGQCwkraHIhYQp9MYC7mIsBClCiL0EKY0BJqaAvBigsLGsp4T9WCMvwAo1YhheoxUDCVAxkA32hwUBfAORCwjKaXEiYQl8M4A7mYoAClOhLkMIYUFIq6IsBCgtLWkr4jxXCEjxHI5bgOWoxkDAVA9lAX2gw0BcAuZCwhCYXEqbQFwO4jbkYoAAl-hKkMAaUlAr6YoDCwqKWEv5jhbAIT9GIRXiKWgwkTMVANtAXGgz0BUAuJCyiyYWEKfTFAG5hLgYoQIm-BCmMASWlgr4YoLCwoKWE_1ghLMBjNGIBHqMWAwlTMZAN9IUGA30BkAsJC2hyIWEKfTGAm5iLAQpQoi9BCmNASamgLwYoLMxrKeE_VgjzcIRGzMMRajGQMBUD2UBfaDDQFwC5kDCPJhcSptAXA7iBuRigACX6EqQwBpSUCvpigMLCnJYS_mOFMAeHaMQcHKIWAwlTMZAN9IUGA30BkAsJc2hyIWEKfTGAa5iLAQpQoi9BCmNASamgLwYoLMxqKeE_VgizMEMjZmGGWgwkTMVANtAXGgz0BUAuJMyiyYWEKfTFAK5iLgYoQIm-BCmMASWlgr4YoLAwraWE_1ghTMMBGjENB6jFQMJUDGQDfaHBQF8A5ELCNJpcSJhCXwzgCuZigAKU6EuQwhhQUiroiwEKC1NaSviPFcIU7KMRUzBFLQYSpmIgG-gLDQb6AiAXEqbQ5ELCFPpiAJcwFwMUoERfghTGgJJSQV8MUFiY1FLCf6wQJmEPjZiEPdRiIGEqBrKBvtBgoC8AciFhEk0uJEyhLwZwAXMxQAFK9CVIYQwoKRX0xQCFhQktJfzHCmEC3qERE_AOtRhImIqBbKAvNBjoC4BcSJhAkwsJU-iLAZzDXAxQgBJ9CVIYg_9KSgV9MUBhYVxLCf-xQhiHt2jEOLxFLQYSpmIgG-gLDQb6AiAXEsbR5ELCFPpiAGcwFwMUoERfghTGgJJSQV8MUFgY01LCf6wQxuANGjEGb1CLgYSpGMgG-kKDgb4AyIWEMTS5kDCFvhjAKczFAAUo0ZcghTGgpFTQFwMUFka1lPAfK4RReI1GjMJr1GIgYSoGsoG-0GCgLwByIWEUTS4kTKEvBnACczFAAUr0JUhhDCgpFfTFAIWFES0l_McKYQReohEj8BK1GEiYioFsoC80GOgLgFxIGEGTCwlT6IsBHMNcDFCAEn0JUhgDSkoFfTFAYWFYSwn_sUIYhhdoxDA8Ry0GEqZiIBvoCw0G-gIgFxKG0eRCwhT6YgCHMBcDFKBEX4IUxoCSUkFfDFBYGNJSwn-sEIbgGRoxBM9Qi4GEqRjIBvpCg4G-AMiFhCE0uZAwhb4YwAHMxQAFKNGXIIUxoKRU0BcDFBYGtZTwHyuEQXiKRgzCU9RiIGEqBrKBvtBgoC8AciFhEE0uJEyhLwawD3MxQAFK9CVIYQwoKRX0xQCFhQEtJfzHCmEAnqARAwBQi4GEqRjIBvpCg4G-AMiFhAE0uZAwhb4YwB7MxQAFKNGXIIUxoKRU0BcDFBb6Wkr4jxVCH-6jEX24j1oMJEzFQDbQFxoM9AVALiT00eRCwhT6YgC7MBcDFKBEX4IUxoCSUkFfDFBY6Gkp4T9WCD24h0b04B5qMZAwFQPZQF9oMNAXALmQ0EOTCwlT6IsB7MBcDFCAEn0JUhgDSkoFfTFAYaGrpYT_WCF04S4a0YW7qMVAwlQMZAN9ocFAXwDkQkIXTS4kTKEvBrANczFAAUr0JUhhDCgpFfTFAIWFjpYS_mOF0IHbaEQHbqMWAwlTMZAN9IUGA30BkAsJHTS5kDCFvhjAFszFAAUo0ZcghTGgpFTQFwMUFtpaSviPFUIbbqERbbiF2v9_AwAA__-Ov5Ib)

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
- Required Python packages (see requirements.txt)
- Access to LLM APIs

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
```

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
