# AI Artist System - Deployment Checklist (v1.0 - Placeholder Stage)

**Date:** 2025-04-30

This checklist outlines the steps and considerations for deploying the AI Artist System in its current state (post-Phase 8). Many components rely on placeholders and require real implementations and API keys for full production deployment.

## 1. Environment Setup

*   [ ] **Python Version:** Ensure Python 3.11+ is installed.
*   [ ] **Dependencies:** Install required packages. Ideally, use a `requirements.txt` file (Note: A consolidated `requirements.txt` needs to be generated).
    ```bash
    # Example (assuming requirements.txt exists)
    # pip install -r requirements.txt 
    echo "Placeholder: Need to generate requirements.txt"
    ```
*   [ ] **Directory Structure:** Verify the standard project structure exists (`noktvrn_ai_artist/`, `output/`, `logs/`, etc.).

## 2. Configuration (`.env` Files)

Ensure `.env` files exist in relevant directories (`noktvrn_ai_artist/`, `batch_runner/`, `release_chain/`, `streamlit_app/`) and contain the necessary variables. **Bold** variables are critical and likely need real values.

*   **Database:**
    *   [ ] `DATABASE_URL`: **PostgreSQL connection string.** (Currently uses SQLite placeholder in some tests).
*   **API Keys (Placeholders):**
    *   [ ] `PEXELS_API_KEY`: **Required for `pexels_client.py`.**
    *   [ ] `SUNO_API_KEY`: **Required for actual Suno integration (currently placeholder).**
    *   [ ] `LUMA_API_KEY`: **Required for actual Luma integration (currently placeholder).**
    *   [ ] `TELEGRAM_BOT_TOKEN`: **Required for `telegram_service.py` and batch runner feedback.**
    *   [ ] `TELEGRAM_CHAT_ID`: **Required for Telegram notifications.**
    *   [ ] `TUNECORE_API_KEY`: **Required for actual TuneCore upload (currently placeholder).**
    *   [ ] `WEB3_PLATFORM_API_KEY`: **Required for actual Web3 upload (currently placeholder).**
*   **Directories:**
    *   [ ] `OUTPUT_BASE_DIR`: Path to the main output directory.
    *   [ ] `RELEASES_DIR`: Path to packaged releases.
    *   [ ] `RUN_STATUS_DIR`: Path for batch run status files.
    *   [ ] `DEPLOY_READY_DIR`: Path for deployment-ready files.
*   **File Paths:**
    *   [ ] `RELEASE_LOG_FILE`: Path to the markdown release log.
    *   [ ] `RELEASE_QUEUE_FILE`: Path to the JSON release queue.
    *   [ ] `UPLOAD_STATUS_FILE`: Path to the JSON upload status log.
    *   [ ] `EVOLUTION_LOG_FILE`: Path to the markdown evolution log.
*   **Logging:**
    *   [ ] `LOG_LEVEL` (various components): Set desired logging level (e.g., INFO, DEBUG).

## 3. Database Setup

*   [ ] **PostgreSQL Instance:** Ensure a PostgreSQL database is running and accessible.
*   [ ] **Schema Application:** Apply database schemas in the correct order (dependencies matter!).
    *   [ ] Apply `artist_progression_log.sql`.
    *   [ ] Apply `content_performance.sql` (Note: This currently has a dependency on `approved_releases` which might need creation or modification).
    *   [ ] Apply any other required schemas (e.g., for artist profiles if not using files).

## 4. API Key Verification

*   [ ] Verify all necessary **real** API keys listed in Section 2 are obtained and correctly configured in the `.env` files.

## 5. Component Status Review

Confirm understanding of which components are placeholders:
*   [ ] **LLM Integration:** Currently placeholder/mock. Needs real implementation.
*   [ ] **Audio Generation (Suno):** Client exists, but generation logic is placeholder.
*   [ ] **Video Generation (Luma):** Client exists, but generation logic is placeholder.
*   [ ] **Release Upload (TuneCore, Web3):** Upload functions are placeholders.
*   [ ] **Artist Selection/Parameter Adaptation:** Logic in `batch_runner` is placeholder.
*   [ ] **Feedback Mechanism:** Telegram polling requires an external webhook server to update status files based on button clicks.

## 6. External Dependencies

*   [ ] **Telegram Webhook Server:** A separate service must be running to receive callbacks from Telegram buttons and update the corresponding `run_status/run_*.json` file status to `approved` or `rejected`.

## 7. Testing

*   [ ] **Unit Tests:** Run all available unit tests.
    ```bash
    # Example command structure (adjust paths)
    # python3.11 -m unittest discover -s /home/ubuntu/ai_artist_system/noktvrn_ai_artist/tests
    echo "Placeholder: Need consolidated test runner command"
    ```
*   [ ] **Integration Testing (Manual):**
    *   [ ] Create dummy artist profile(s).
    *   [ ] Manually create a dummy `run_status/run_*.json` file with `status: approved`.
    *   [ ] Run `release_chain.py` directly or via `batch_runner.py` (if modified to pick up manual files) to test release packaging.
    *   [ ] Run `release_uploader.py` to test processing of the queued release and creation of `deploy_ready` output.
    *   [ ] Launch Streamlit app (`streamlit run streamlit_app/main.py`) and check dashboards (Monitoring, Release Management).

## 8. Deployment Steps

*   [ ] **Database:** Ensure schema is applied.
*   [ ] **Batch Runner:**
    *   [ ] Configure `.env` file.
    *   [ ] Start `artist_batch_runner.py` (e.g., using `nohup`, `screen`, or a process manager like `systemd`).
*   [ ] **Streamlit Application:**
    *   [ ] Configure `.env` file.
    *   [ ] Start the Streamlit app (`streamlit run streamlit_app/main.py`). Consider using a production server like Gunicorn + Nginx for public access.
*   [ ] **Telegram Webhook Server:** Deploy and start the external webhook server.

## 9. Monitoring

*   [ ] **Streamlit Dashboards:** Regularly check the Monitoring and Release Management dashboards.
*   [ ] **Logs:** Monitor application logs (stdout/stderr or configured log files) for errors.
*   [ ] **Output Files:** Check `release_log.md`, `release_queue.json`, `release_upload_status.json`, `artist_evolution_log.md` for expected updates.

## 10. Pre-Deployment Cleanup

*   [ ] **Logs:** Review and archive/delete old/unnecessary log files from `/logs/` (see `cleanup_report.md`).
*   [ ] **Test Data:** Remove dummy run files, test releases, or other test artifacts from `output/` directories.
*   [ ] **Git Status:** Ensure no uncommitted changes remain before deploying.

**Note:** This checklist is based on the system's state after Phase 8. It must be updated as placeholder components are replaced with real implementations.

