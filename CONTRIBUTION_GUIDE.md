# 📜 Contribution Guide for Artist Creator Platform

Welcome to the Artist Creator Project!  
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
