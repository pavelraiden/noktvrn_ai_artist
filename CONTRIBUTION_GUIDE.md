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

---

## 📂 Project Structure Overview

| Folder | Purpose |
|--------|---------|
| `artist_builder/` | Artist prompt creation, validation, profile assembly |
| `llm_orchestrator/` | Session management, logging, LLM orchestration |
| `validators/` | Quality checks, feedback loops |
| `composer/` | Final artist profile construction |
| `review/` | Reviews and feedback on generated data |

---

## 🧹 Quality Standards

- Maintain clear separation of concerns.
- Use clean and descriptive naming.
- Avoid redundant code or duplicate logic.
- Follow best practices for error handling.
- Ensure reusability where appropriate.

---

## 🔄 GitHub Sync and Update Rules

- Always **pull** the latest project state before starting work.
- After finishing a task:
  - **Check project consistency**.
  - **Fix integrations** if needed.
  - **Push** the updated project immediately.
  - **Write clear commit messages** (e.g., "Added prompt validator for artist creation flow").

---

## 🛠 Special Reminder for AI Agents

If you are an AI agent contributing to the project:

- **Always review the full project tree before coding**.
- **Adapt to changes** dynamically.
- **Never create isolated or disconnected modules**.
- **Proactively improve** the project when opportunities arise.
- **Maintain production-level standards at all times**.

---

✅ By contributing to this project, you confirm you have read and agree to follow these rules.

---
