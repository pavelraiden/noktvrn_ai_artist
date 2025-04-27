# 📜 Contribution Guide for AI Artist Creation and Management System

Welcome to the AI Artist Creation and Management System project!  
This guide describes the mandatory rules for contributing to the project to maintain high quality, scalability, and modularity.

---

## 🛡 General Principles

- **Full Project Awareness**  
  Always check the full project structure and state before starting or completing any task.
  
- **Integration and Consistency**  
  Every new module, file, or function must integrate smoothly with the existing system.

- **Improvement Mindset**  
  Actively refactor or improve parts of the system if you notice optimization opportunities, conflicts, or outdated patterns.

- **Push Policy**  
  Push every meaningful change to GitHub after:
  - Checking project consistency
  - Verifying modular structure
  - Confirming no conflicts
  
- **Modular and Scalable Design**  
  Code must be modular, scalable, clean, and ready for future expansions without major rewrites.

- **Self-Learning Enhancement**  
  Every contribution must aim to improve the system's ability to self-learn, self-adapt, and self-optimize over time based on performance data and feedback.

---

## 📂 Project Structure Overview

| Folder | Purpose |
|--------|---------|
| `artist_builder/` | Artist prompt creation, validation, profile assembly |
| `artist_flow/` | Artist creation workflow and asset management |
| `artists/` | Generated artist data and assets |
| `llm_orchestrator/` | Session management, logging, LLM orchestration |
| `scripts/` | Utility scripts for content and video generation |
| `templates/` | Template files for generation |
| `video_gen_config/` | Video generation configuration |

---

## 🧩 Adding New Modules or Features

When adding new modules or features to the system, follow these guidelines:

1. **Module Placement**
   - Place new modules in the appropriate top-level directory based on functionality
   - Create new top-level directories only when functionality doesn't fit existing categories
   - Follow the established naming conventions for directories and files

2. **Module Structure**
   - Each module should have a clear, single responsibility
   - Include a `README.md` file explaining the module's purpose and usage
   - Implement proper error handling and logging
   - Add appropriate unit and integration tests

3. **Integration Requirements**
   - Define clear interfaces for interaction with other modules
   - Use dependency injection where appropriate to maintain loose coupling
   - Document all public APIs and integration points
   - Ensure backward compatibility with existing modules

4. **Approval Process**
   - Create a detailed proposal for significant new modules
   - Include justification, architecture design, and integration plan
   - Submit for review before implementation begins
   - Address all feedback before merging

---

## 📝 Coding Conventions

### Naming Conventions

- **Files and Directories**
  - Use snake_case for Python files and directories: `artist_profile_generator.py`
  - Use descriptive names that clearly indicate purpose

- **Classes**
  - Use PascalCase for class names: `ArtistProfileGenerator`
  - Class names should be nouns or noun phrases

- **Functions and Methods**
  - Use snake_case for function and method names: `generate_artist_profile()`
  - Function names should be verbs or verb phrases
  - Boolean functions should start with `is_`, `has_`, or similar: `is_valid_profile()`

- **Variables**
  - Use snake_case for variable names: `artist_profile`
  - Use descriptive names that clearly indicate purpose
  - Avoid single-letter variables except in short loops

- **Constants**
  - Use UPPER_SNAKE_CASE for constants: `DEFAULT_GENRE_COUNT`

### Docstring Format

All modules, classes, and functions must include docstrings following this format:

```python
"""
Brief description of the function/class.

Detailed description explaining the purpose, behavior,
and any important information.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

Returns:
    type: Description of return value.

Raises:
    ExceptionType: When and why this exception is raised.

Example:
    >>> example_usage()
    expected_result
"""
```

### Code Style

- Follow PEP 8 style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters
- Use type hints for function parameters and return values
- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Use Black for code formatting
- Use isort for import sorting

---

## 🤖 LLM Integration Guidelines

When adding or modifying LLM models in the system:

1. **Model Selection Criteria**
   - Document the specific capabilities required for the task
   - Justify the selection of a particular model over alternatives
   - Consider performance, cost, and latency requirements

2. **Integration Process**
   - Create an adapter class that implements the `LLMInterface`
   - Implement all required methods from the interface
   - Add appropriate error handling and retry logic
   - Include proper logging of all interactions

3. **Testing Requirements**
   - Create unit tests with mocked responses
   - Implement integration tests with actual API calls (using test credentials)
   - Benchmark performance, latency, and cost
   - Test edge cases and error handling

4. **Configuration Management**
   - Store model-specific configuration in environment variables
   - Document all required configuration variables
   - Provide sensible defaults where appropriate
   - Include example configuration in `.env.example`

5. **Fallback Mechanisms**
   - Implement fallback strategies for API failures
   - Consider degraded operation modes
   - Document failure scenarios and recovery procedures

---

## 🔄 Artist Behavior Evolution Process

The system evolves artist behavior based on success metrics through the following process:

1. **Data Collection**
   - Track engagement metrics across all platforms
   - Collect audience demographic and preference data
   - Monitor industry trends and competitor performance
   - Store all data in the performance database

2. **Analysis Phase**
   - Run periodic analysis jobs (daily/weekly)
   - Identify patterns in successful content
   - Detect audience preference shifts
   - Compare performance against baseline and targets

3. **Strategy Formulation**
   - Generate adaptation recommendations
   - Prioritize changes based on expected impact
   - Create A/B testing plans for major changes
   - Document proposed evolution strategy

4. **Implementation**
   - Apply subtle changes to artist profile parameters
   - Adjust content generation prompts
   - Modify release scheduling patterns
   - Update visual and audio style guidelines

5. **Validation**
   - Monitor performance after changes
   - Compare against previous baseline
   - Revert unsuccessful changes
   - Document successful adaptations

6. **Feedback Loop**
   - Feed results back into the learning system
   - Update success prediction models
   - Refine evolution strategies
   - Document learnings for future reference

---

## 📊 Trend Analyzer Expansion

To expand the trend analyzer to incorporate new data sources:

1. **Data Source Evaluation**
   - Assess data quality, reliability, and relevance
   - Determine update frequency and freshness
   - Evaluate cost and technical requirements
   - Document justification for adding the source

2. **Integration Process**
   - Create a new data connector class in `trend_analyzer/connectors/`
   - Implement the `DataSourceConnector` interface
   - Add appropriate data transformation and normalization
   - Include error handling and retry logic

3. **Data Processing Pipeline**
   - Update ETL processes to incorporate new data
   - Modify aggregation and analysis algorithms
   - Ensure backward compatibility with existing reports
   - Optimize for performance and resource usage

4. **Validation Requirements**
   - Verify data accuracy against source
   - Test integration with existing trend analysis
   - Benchmark performance impact
   - Validate insights against industry knowledge

5. **Documentation**
   - Update data dictionary with new fields
   - Document connector configuration
   - Add usage examples for new data in analysis
   - Include troubleshooting information

---

## 🧹 Quality Standards

- Maintain clear separation of concerns.
- Use clean and descriptive naming.
- Avoid redundant code or duplicate logic.
- Follow best practices for error handling.
- Ensure reusability where appropriate.
- Implement comprehensive logging for performance analysis.
- Include metrics collection for self-optimization.

---

## 🔄 GitHub Sync and Update Rules

- Always **pull** the latest project state before starting work.
- After finishing a task:
  - **Check project consistency**.
  - **Fix integrations** if needed.
  - **Push** the updated project immediately.
  - **Write clear commit messages** (e.g., "Added prompt validator for artist creation flow").

---

## 🧠 Self-Learning Principles

All contributions must adhere to these self-learning principles:

- **Data-Driven Improvement**  
  Implement mechanisms to collect, analyze, and learn from performance data.

- **Feedback Loop Integration**  
  Every module should include or connect to feedback loops that enable continuous improvement.

- **Adaptation Mechanisms**  
  Design components to adapt their behavior based on historical performance and changing conditions.

- **Performance Metrics**  
  Include clear metrics for measuring success and identifying areas for improvement.

- **Learning Persistence**  
  Ensure learning outcomes are properly stored and applied to future operations.

- **Incremental Optimization**  
  Support gradual refinement of processes based on accumulated knowledge.

---

## 🛠 Special Reminder for AI Agents

If you are an AI agent contributing to the project:

- **Always review the full project tree before coding**.
- **Adapt to changes** dynamically.
- **Never create isolated or disconnected modules**.
- **Proactively improve** the project when opportunities arise.
- **Maintain production-level standards at all times**.
- **Enhance self-learning capabilities** with each contribution.
- **Document learning mechanisms** thoroughly.

---

## 🔍 Module Integration Requirements

When integrating modules:

- Ensure clear interfaces between components.
- Document all integration points.
- Implement comprehensive error handling at boundaries.
- Include tests that verify correct integration.
- Design for backward compatibility.
- Consider how the integration supports self-learning goals.

---

✅ By contributing to this project, you confirm you have read and agree to follow these rules.

---
