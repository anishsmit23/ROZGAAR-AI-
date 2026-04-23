"""Streamlit page for viewing tracked jobs."""

from __future__ import annotations

import streamlit as st

from config.settings import get_settings
from dashboard.components.metrics_bar import render_metrics
from memory.job_tracker import JobTracker

st.set_page_config(page_title="Job Tracker", layout="wide")
st.title("Job Tracker")

settings = get_settings()
tracker = JobTracker(settings.db_path)
rows = tracker.list_all()

applied_count = len([row for row in rows if row.get("status") == "applied"])
interview_count = len([row for row in rows if row.get("interview_date")])

render_metrics(total_jobs=len(rows), applied=applied_count, interviews=interview_count)

if rows:
    st.dataframe(rows, use_container_width=True)
else:
    st.info("No jobs tracked yet. Open **Job Search** in the sidebar, run a query, and results will show here.")
