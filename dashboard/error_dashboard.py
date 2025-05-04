# /home/ubuntu/ai_artist_system_clone/dashboard/error_dashboard.py
"""
Streamlit Dashboard for viewing Error Reports from the AI Artist System.
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Import DB functions ---
try:
    # Ensure DB is initialized if run standalone
    from services.artist_db_service import get_error_reports, initialize_database

    initialize_database()  # Make sure tables exist
except ImportError as e:
    st.error(
        f"Failed to import database service: {e}. Please ensure the service file exists and dependencies are installed."
    )
    st.stop()

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="AI Artist System - Error Dashboard", layout="wide")
st.title("📊 AI Artist System - Error Reporting Dashboard")
st.caption(
    f"Displaying error reports logged by the system. Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
# --- Sidebar Filters ---
st.sidebar.header("Filters")
limit = st.sidebar.number_input(
    "Number of reports to show", min_value=10, max_value=500, value=50, step=10
)
status_options = [
    "all",
    "new",
    "analyzed",
    "fix_suggested",
    "fix_attempted",
    "fix_failed",
    "fix_applied",
    "ignored",
    "monitor_failed",
    "parse_failed",
]
selected_status = st.sidebar.selectbox(
    "Filter by Status", options=status_options, index=0
)


# --- Fetch Data --- #
@st.cache_data(ttl=60)  # Cache data for 60 seconds
def load_data(limit_val, status_filter_val):
    status_arg = status_filter_val if status_filter_val != "all" else None
    reports = get_error_reports(limit=limit_val, status_filter=status_arg)
    if reports:
        df = pd.DataFrame(reports)
        # Convert timestamp to datetime objects for better display/sorting
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Reorder columns for better readability
        cols_order = [
            "report_id",
            "timestamp",
            "status",
            "service_name",
            "error_hash",
            "error_log",
            "analysis",
            "fix_suggestion",
        ]
        df = df[[col for col in cols_order if col in df.columns]]
        return df
    return pd.DataFrame()  # Return empty dataframe if no reports


df_reports = load_data(limit, selected_status)

# --- Main Display Area --- #
if df_reports.empty:
    st.warning(
        f"No error reports found matching the criteria (Status: {selected_status})."
    )
else:
    st.subheader(f"Recent Error Reports (Status: {selected_status.capitalize()})")

    # --- Basic Stats/Trends --- #
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Reports Shown", len(df_reports))
    with col2:
        if not df_reports.empty:
            status_counts = df_reports["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            st.bar_chart(status_counts, x="status", y="count", use_container_width=True)
        else:
            st.write("No data for status chart.")

    # --- Data Table --- #
    st.dataframe(df_reports, use_container_width=True, hide_index=True)

    # --- Detail View --- #
    st.subheader("Error Report Details")
    selected_id = st.selectbox(
        "Select Report ID to view details", options=df_reports["report_id"].tolist()
    )

    if selected_id:
        selected_report = (
            df_reports[df_reports["report_id"] == selected_id].iloc[0].to_dict()
        )
        report_id = selected_report.get("report_id")
        st.write(f"**Report ID:** {report_id}")
        timestamp = selected_report.get("timestamp")
        st.write(f"**Timestamp:** {timestamp}")
        status = selected_report.get("status")
        st.write(f"**Status:** {status}")
        service_name = selected_report.get("service_name", "N/A")
        st.write(f"**Service:** {service_name}")
        error_hash = selected_report.get("error_hash", "N/A")
        st.write(f"**Error Hash:** {error_hash}")
        with st.expander("Error Log"):
            st.code(selected_report.get("error_log", "Not Available"), language="log")

        with st.expander("LLM Analysis"):
            st.markdown(
                selected_report.get("analysis", "*Not Available or Not Analyzed Yet*")
            )

        with st.expander("LLM Fix Suggestion"):
            # Display as diff if it looks like one, otherwise as markdown/text
            fix_suggestion = selected_report.get(
                "fix_suggestion", "*Not Available or Not Generated Yet*"
            )
            if isinstance(fix_suggestion, str) and (
                "--- a/" in fix_suggestion or "+++ b/" in fix_suggestion
            ):
                st.code(fix_suggestion, language="diff")
            else:
                st.markdown(fix_suggestion)

# --- How to Run --- #
st.sidebar.markdown("--- ")
st.sidebar.markdown("**How to Run:**")
st.sidebar.code("streamlit run dashboard/error_dashboard.py")
