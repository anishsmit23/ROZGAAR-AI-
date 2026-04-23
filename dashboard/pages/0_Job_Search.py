"""Discover jobs from the web, persist to the tracker, and Chroma for semantic search."""

from __future__ import annotations

import streamlit as st

from dashboard.execution import run_workflow_with_progress

st.set_page_config(page_title="Job Search", layout="wide")
st.title("Job Search")

st.caption(
    "Searches the web (SerpAPI + Google) and records results in the Job Tracker. "
    "Set SERPAPI_KEY in your environment."
)

query = st.text_input("Search query", value="remote software engineer jobs")
max_results = st.slider("Max results", min_value=1, max_value=30, value=10)

if st.button("Run search", type="primary") and query.strip():
    with st.spinner("Searching and saving jobs — several seconds to a few minutes…"):
        try:
            result = run_workflow_with_progress(
                {
                    "task": "job_search",
                    "job_search": {"query": query.strip(), "max_results": max_results},
                }
            )
        except Exception:
            st.stop()

    jobs = result.get("jobs", [])
    if not jobs:
        st.warning("No jobs returned. Check SERPAPI_KEY and your query, then try again.")
    else:
        st.success(f"Found {len(jobs)} job(s). Open **Job Tracker** to review and manage them.")
        st.dataframe(
            [
                {
                    "Title": j.get("title"),
                    "Company": j.get("company"),
                    "Location": j.get("location"),
                    "URL": j.get("url", ""),
                }
                for j in jobs
            ],
            use_container_width=True,
            column_config={"URL": st.column_config.LinkColumn("URL")},
        )
