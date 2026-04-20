"""Main Streamlit dashboard landing page."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="AI Job Search Agent", layout="wide")

st.title("Autonomous AI Job Search Agent")
st.write(
    "Use the sidebar pages to search jobs, tailor resumes, generate outreach emails, "
    "and prepare for interviews."
)
