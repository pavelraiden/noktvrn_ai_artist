import streamlit as st
import json
import os
import sys
from datetime import datetime

# Add project root to sys.path to allow importing release_manager
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Attempt to import ReleaseManager and ReleaseStatus
# This assumes release_manager.py is in /home/ubuntu/workspace/project_root/release_chain/
try:
    from release_chain.release_manager import ReleaseManager, ReleaseStatus
except ImportError as e:
    st.error(
        f"Error importing ReleaseManager: {e}. Ensure release_manager.py is in the correct path and PYTHONPATH is set."
    )

    # Provide a dummy ReleaseManager and ReleaseStatus if import fails, so UI can partially load
    class ReleaseStatus(Enum):
        PENDING_PREVIEW = "pending_preview"
        PREVIEW_READY = "preview_ready"
        PENDING_APPROVAL = "pending_approval"
        APPROVED = "approved"
        REJECTED = "rejected"
        PENDING_UPLOAD = "pending_upload"
        UPLOADED = "uploaded"
        FAILED = "failed"

    class ReleaseManager:
        def __init__(self, config):
            self.config = config
            st.warning("Using DUMMY ReleaseManager due to import error.")

        def get_release_status(self, release_id):
            return {
                "release_id": release_id,
                "status": "error_loading_status",
                "history": [],
                "error": "Could not load ReleaseManager",
            }

        def _get_metadata_path(self, release_id: str) -> str:
            # This won't actually be used if get_all_release_ids can't list files
            return os.path.join(
                self.config.get("release_metadata_dir", "./release_metadata"),
                f"{release_id}.json",
            )

        def get_all_release_ids(self) -> list:
            metadata_dir = self.config.get(
                "release_metadata_dir", "./release_metadata"
            )
            if not os.path.exists(metadata_dir):
                return []
            try:
                return [
                    f.replace(".json", "")
                    for f in os.listdir(metadata_dir)
                    if f.endswith(".json")
                ]
            except Exception as e:
                st.error(f"Error listing release IDs: {e}")
                return []


# Configuration for ReleaseManager (adjust paths as needed)
# These paths should correspond to where ReleaseManager saves its data.
RELEASE_MANAGER_CONFIG = {
    "release_metadata_dir": os.path.join(
        PROJECT_ROOT, "release_chain", "test_release_metadata"
    ),  # Adjust if you used a different dir
    "preview_dir": os.path.join(
        PROJECT_ROOT, "release_chain", "test_previews"
    ),
    "upload_dir": os.path.join(
        PROJECT_ROOT, "release_chain", "test_upload_ready"
    ),
}

# Initialize ReleaseManager
# Ensure the dummy or real ReleaseManager is available here
if "ReleaseManager" in globals():
    release_manager = ReleaseManager(config=RELEASE_MANAGER_CONFIG)
else:
    # This case should ideally not be hit if the dummy is defined correctly above
    st.error("Critical error: ReleaseManager class not defined.")
    release_manager = None  # UI will be non-functional

st.set_page_config(
    page_title="AI Music Release Pipeline Status", layout="wide"
)

st.title("🎵 AI Music Release Pipeline Status")
st.caption(
    f"Monitoring releases from: {RELEASE_MANAGER_CONFIG['release_metadata_dir']}"
)


def display_release_details(release_id):
    if not release_manager:
        st.error("ReleaseManager not initialized. Cannot fetch details.")
        return

    try:
        status_data = release_manager.get_release_status(release_id)
    except Exception as e:
        st.error(f"Error fetching status for {release_id}: {e}")
        return

    st.subheader(f"Details for Release ID: {release_id}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Current Status",
            status_data.get("status", "N/A").replace("_", " ").title(),
        )
        st.text(f"Last Updated: {status_data.get('last_updated', 'N/A')}")

    with col2:
        if status_data.get("song_metadata"):
            st.text_input(
                "Song Title",
                status_data["song_metadata"].get("title", "N/A"),
                disabled=True,
            )
            st.text_input(
                "Artist",
                status_data["song_metadata"].get("artist", "N/A"),
                disabled=True,
            )
        else:
            st.info("Song metadata not available.")

    st.markdown("---    ")
    st.markdown("#### File Paths")
    paths_data = {
        "Original Song Path": status_data.get("original_song_path", "N/A"),
        "Preview Path": status_data.get("preview_path", "N/A"),
        "Upload Path": status_data.get("upload_path", "N/A"),
    }
    st.json(paths_data)

    st.markdown("---    ")
    st.markdown("#### History")
    history = status_data.get("history", [])
    if history:
        for entry in reversed(history):  # Show newest first
            with st.expander(
                f"{datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} - {entry['status'].replace('_', ' ').title()}"
            ):
                st.write(f"**Notes:** {entry.get('notes', 'No notes.')}")
                if entry.get("details"):
                    st.json(entry["details"])
    else:
        st.info("No history available for this release.")

    if status_data.get("upload_details"):
        st.markdown("---    ")
        st.markdown("#### Upload Details")
        st.json(status_data.get("upload_details"))

    if status_data.get("error"):
        st.markdown("---    ")
        st.error(
            f"Error associated with this release: {status_data.get('error')}"
        )


# Sidebar for selecting release
st.sidebar.title("Release Selection")

if not release_manager:
    st.sidebar.error("ReleaseManager not available.")
    all_release_ids = []
else:
    try:
        all_release_ids = release_manager.get_all_release_ids()
    except Exception as e:
        st.sidebar.error(f"Failed to load release IDs: {e}")
        all_release_ids = []

if not all_release_ids:
    st.sidebar.info(
        "No releases found. Ensure the metadata directory is correct and contains release files."
    )
    st.info(
        "No releases found to display. Please initiate a release using the `release_manager.py` script or ensure the metadata directory is correctly configured and populated."
    )
else:
    selected_release_id = st.sidebar.selectbox(
        "Select a Release ID to view details:", options=all_release_ids
    )
    if selected_release_id:
        display_release_details(selected_release_id)
    else:
        st.info("Select a Release ID from the sidebar to see its details.")

# Refresh button
if st.sidebar.button("Refresh Release List"):
    st.experimental_rerun()

st.sidebar.markdown("---    ")
st.sidebar.markdown(
    "**Note:** This UI reads data from the release metadata JSON files. Ensure the `ReleaseManager` script is run to create and update these files."
)

# To run this Streamlit app:
# 1. Ensure you are in the `/home/ubuntu/workspace/project_root/streamlit_ui/` directory.
# 2. Run the command: streamlit run app.py
