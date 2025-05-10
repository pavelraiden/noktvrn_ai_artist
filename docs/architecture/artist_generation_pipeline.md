# Artist Content Generation Pipeline

This document details the step-by-step process for generating new content (music tracks and associated videos) for an AI artist within the platform.

## Pipeline Overview

The pipeline transforms an initial trigger or request into a finalized, approved content release stored in the database. It involves several core modules and external API interactions.

*See `/docs/architecture/diagrams.md` for a visual representation of this flow.*

## Pipeline Stages

1.  **Trigger:**
    *   **Source:** The pipeline can be initiated manually (e.g., via a UI action in Streamlit - *not fully implemented*), on a schedule, or automatically triggered by the `Artist Evolution Service` based on performance analysis or strategic goals.
    *   **Input:** Artist ID, potentially specific parameters or themes from the `Style Adaptor` or evolution logic.

2.  **Track Generation:**
    *   **Module:** `Content Generation Flow` interacts with `Generation Services`.
    *   **Action:** Calls the `Suno API Client` (`api_clients/suno_client.py`) to generate a new music track based on the artist profile and adapted parameters (e.g., genre, mood, tempo, lyrics prompt).
    *   **Output:** URL of the generated track (hosted by Suno).

3.  **Video Selection (Stock Footage):**
    *   **Input:** Generated track URL, artist profile, style parameters.
    *   **Modules:** `Content Generation Flow`, `Generation Services`, `Audio Analyzer` (`video_processing/audio_analyzer.py`), `Video Selector` (`video_processing/video_selector.py`), `Pexels API Client` (`api_clients/pexels_client.py`), `Stock Success Tracker` (`analytics/stock_success_tracker.py`).
    *   **Actions:**
        *   `Audio Analyzer` analyzes the track to extract features (tempo, mood, energy, keywords).
        *   `Video Selector` uses these features and potentially keywords from the artist profile to query the `Pexels API Client` for relevant stock videos.
        *   `Video Selector` consults the `Stock Success Tracker` to prioritize sources based on past performance.
        *   `Video Selector` selects the most suitable stock video URL(s).
        *   *(Future Enhancement):* Implement basic video editing (cutting, filtering) using `scripts/video_gen/ffmpeg_controller.py` on selected stock footage.
    *   **Output:** URL of the selected stock video (Pexels).

4.  **Approval Workflow:**
    *   **Modules:** `Streamlit App`, `Telegram Service` (`streamlit_app/services/telegram_service.py`), `Webhook Server` (`streamlit_app/webhook_server.py`).
    *   **Action:**
        *   The generated track and selected video URLs are presented for human review (e.g., via a Telegram message sent by `Telegram Service`).
        *   The reviewer uses Telegram buttons ("Approve"/"Reject").
        *   Telegram sends a callback to the `Webhook Server`.
        *   The `Webhook Server` processes the approval/rejection.
    *   **Output:** Approval status (Approved/Rejected).

5.  **Release Storage:**
    *   **Modules:** `Webhook Server`, `Database Service` (`streamlit_app/services/database_service.py`).
    *   **Action:** If approved, the `Webhook Server` (via `Database Service`) inserts the track URL, video URL, artist ID, and other relevant metadata into the `approved_releases` table in the PostgreSQL database.
    *   **Output:** New record in the `approved_releases` table.

## Simplified Diagram

*(This diagram is also available in `/docs/architecture/diagrams.md`)*

```mermaid
graph TD
    A[Trigger (Manual/Scheduled/Evolution)] --> B{Generate Track};
    B -- Artist Profile/Params --> C[Suno API Client];
    C -- Track URL --> D{Select Video};
    D -- Track URL/Profile/Params --> E[Audio Analyzer];
    E -- Audio Features --> F[Video Selector];
    F -- Keywords/Source Prefs --> G[Pexels API Client];
    G -- Stock Video URLs --> F;
    F -- Selected Video URL --> H{Approval Workflow};
    H -- Track & Video URLs --> J[Telegram Service];
    J -- Approval Request --> K[Human Reviewer];
    K -- Approve/Reject --> L[Telegram Callback];
    L --> M[Webhook Server];
    M -- Approval Status & URLs --> N{Store Release};
    N -- Release Data --> O[Database Service];
    O -- Insert --> P[DB Table: approved_releases];
```

## Dependencies & Status

*   **External APIs:** Suno, Pexels, Telegram.
*   **Core Modules:** `Generation Services`, `Audio Analyzer`, `Video Selector`, `API Clients`, `Database Services`, `Telegram Service`, `Webhook Server` are considered active and implemented.
*   **Trigger Mechanism:** Manual/UI trigger not fully implemented; relies on direct script execution or future scheduling/evolution triggers.
*   **Video Generation:** Currently relies solely on selecting stock footage via Pexels. Direct video generation (e.g., using other AI models) is not implemented.


