# AI Artist Platform - Final Production Sync & Structural Evolution Todo

This checklist outlines the tasks required for the final production synchronization and structural evolution of the AI Artist Platform, aiming for Production v1.0 readiness.

## 1. Full Structure Review

- [x] Recursively check EVERY folder and subfolder in `/home/ubuntu/ai_artist_system_clone`.
- [x] For each directory:
    - [ ] Read `README.md`, `docs/*.md`, or `.txt` files.
    - [ ] Verify content matches actual code in the folder.
    - [ ] Write missing documentation (READMEs, etc.).
    - [ ] Identify and handle unused/outdated code (archive or delete).
    - [ ] Rename unclear files/folders for clarity.

## 2. Documentation Rebuild

- [ ] Rewrite `docs/project_context.md` to reflect active modules and roles (Phase 1–8.3), using clear formatting (sections, lists, tables).
- [ ] Update `docs/development/dev_diary.md` with a log entry for this phase (mentioning review of past 13 chat cycles).
- [ ] Rewrite or create missing `README.md` in each core directory (e.g., `api_clients`, `artist_evolution`, `batch_runner`, `database`, `llm_orchestrator`, `release_chain`, `scripts`, `video_processing`).
- [ ] Add a visual table to `CONTRIBUTION_GUIDE.md` detailing LLM roles, logging, and fallback/rotation mechanisms.

## 3. Remove Luma + Insert Real API Keys

- [x] Remove all references to Luma API from the codebase (e.g., `api_clients/luma_client.py`, any import statements, related logic).
- [x] Update `.env` with the provided production API keys:
    - [ ] SUNO: `6434df466fc04e16bc1b56eb763bfe6e`
    - [ ] PEXELS: `vvQucvzlZ6vLo6RDbrCahvI4gdsW8mgWTVGXyFvPtiI8YAarPK2LFtcm`
    - [ ] PIXABAY: `49941633-74bb08eeab74756d08e7ba75a`
    - [ ] DEEPSEEK: `sk-efc74f32e9a04b68a785d28c6466f385`
    - [ ] GEMINI: `AIzaSyDwkubOj3JEl4P8BK_f-HDoebzO-LCokXI`
    - [ ] GROK: `xai-dc9ri9l823T1BbpwZYCJEuV46KBEhXW1cJGEmEMFzc4hz5nbOjl66QhjFGDqoE856rqpIp5ENhxxbhpW`
    - [ ] MISTRAL: `hOIujZigJdrr4qKEOrm0rYX8Ddej39ww`
    - [ ] TELEGRAM_BOT_TOKEN: `7806913313:AAGO_SUlQCVDQLlW7_lLcUb2gDW2MCIFASY`
    - [ ] TELEGRAM_CHAT_ID: `446260424`
- [x] Update `.env.example` to reflect the required keys (use placeholder values like `YOUR_SUNO_API_KEY`).
- [x] Ensure relevant files (e.g., API clients, orchestrator) correctly load and use these keys from the environment.

## 4. LLM System Checkup

- [ ] Review LLM role logic (author, helper, validator, diarist, etc.) in `llm_orchestrator` and related modules.
- [ ] Verify each role writes logs appropriately (e.g., to `artist_diary` or specific log files).
- [ ] Ensure consistent style/voice handling when switching between LLMs (e.g., DeepSeek, Gemini, Grok, Mistral, OpenAI).
- [ ] Confirm compatibility of roles with different LLM provider APIs.

## 5. Trend, Video, Social Flow Validation

- [ ] Review trend fetching and analysis logic (e.g., `data_pipelines/spotify_charts_pipeline.py`).
- [x] Validate lyrics/video creation logic alignment with trends.
- [ ] Validate stock video cutting and filtering logic (e.g., `scripts/video_gen/ffmpeg_controller.py`, `video_processing`).
- [ ] Validate video/music/emotion matching logic.
- [ ] Create/Update `docs/video_flow.md` documenting the video generation process.
- [ ] Create/Update `docs/trend_flow.md` documenting the trend analysis process.

## 6. Auto LLM API Evolution

- [x] Design mechanism to detect new LLM models (e.g., check provider APIs or a central registry).
- [x] Implement `llm_registry.py` (or similar) to store known/new LLM endpoints/identifiers.
- [x] Implement logic to automatically test new LLMs in fallback/spare roles within the `llm_orchestrator`.
- [x] Create `docs/llm_adaptation.md` documenting this auto-evolution feature.

## 7. Finalize & Push to GitHub

- [x] Configure Git with the provided token: `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`.
- [ ] Stage all changes.
- [ ] Perform a final check:
    - [ ] No dummy API keys remain in committed code (check `.env.example` carefully).
    - [ ] No placeholder files remain.
    - [ ] `README.md`, `docs/project_context.md`, `docs/development/dev_diary.md`, and `.env.example` are valid and up-to-date.
- [ ] Commit changes with a descriptive message.
- [ ] Push changes to the `main` branch on GitHub.
- [ ] Verify the push was successful on GitHub.

## 8. Final Reporting

- [ ] Create a final completion report summarizing the actions taken and the final state of the repository.
- [ ] Notify the user of completion, attaching the report and key updated documents.
