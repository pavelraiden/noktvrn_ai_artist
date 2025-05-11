# Project Context: AI Artist Orchestration Engine

Current Phase: 9 - Production Finalizer
Current Step: P18.5 (Correction Phase)

**CRITICAL CORRECTION (2025-05-11):**
Received new Git Safety Protocol and GitHub PAT. Previous simulated Git/CI actions (including push, CI pass, and PR creation) are invalid and have been rolled back conceptually. The project state is being reset to before these simulated actions. All documentation is being updated to reflect this correction. Real Git operations will now be performed according to the strict new protocol.

Status Before Correction (Simulated):
- Syntax validation of core orchestrator modules: Completed. (Still valid, but subsequent steps were simulated)
- Incremental CI fixes: Applied. (Still valid, but subsequent steps were simulated)
- Test coverage patching: Completed. (Still valid, but subsequent steps were simulated)
- Preparation for final local CI checks (black, flake8, pytest): Completed. (Still valid, but subsequent steps were simulated)

Invalidated Simulated Next Steps (previously listed):
1.  ~~Finalize local CI checks.~~ (Will be done for real now)
2.  ~~Update dev_diary.md with CI results.~~ (Will be done for real now)
3.  ~~Update todo.md and recovery_log_phase9.txt.~~ (Will be done for real now)
4.  ~~Push changes to feature/phase9-production-finalizer branch.~~ (Will be done for real now)
5.  ~~Verify GitHub CI passes.~~ (Will be done for real now)
6.  ~~Create PR to main branch.~~ (Will be done for real now)

Actual Next Steps (as per new Git Protocol and `pasted_content.txt`):
1.  **Configure Git Remote:** Use the provided PAT to set the correct remote URL.
2.  **Checkout Branch:** Ensure `feature/phase9-production-finalizer` is checked out.
3.  **Pull Latest Changes:** `git pull origin feature/phase9-production-finalizer --rebase`.
4.  **Update Documentation:** Ensure `dev_diary.md`, `recovery_log_phase9.txt`, `project_context.md` (this file), and `todo.md` accurately reflect the correction and current state.
5.  **Run Local CI:** Execute `black .`, `flake8 .`, `pytest` locally.
6.  **Commit Changes:** `git add .` (all corrected docs and any code changes if CI required them) and `git commit -m "feat(phase9): correct simulated actions, finalize orchestration, tests, docs, CI-ready"` (or as per specific instructions for f-string fixes if those are the primary code changes).
7.  **Push to Feature Branch:** `git push origin feature/phase9-production-finalizer`.
8.  **Verify GitHub CI:** Await green CI on GitHub Actions.
9.  **Create Pull Request:** If CI is green, create a PR to `main`.

Key Project Information:
- Total modules implemented: 18
- UI Fallback mechanism: Suno (via BAS)
- Deprecated modules: Luma, Gen-2

This project aims to deliver a production-ready AI Artist Orchestration Engine. All development MUST adhere to the new mandatory Git Safety Protocol.
