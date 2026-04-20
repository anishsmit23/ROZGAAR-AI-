"""Reusable Streamlit component for displaying one job card."""

from __future__ import annotations

import streamlit as st


def render_job_card(job: dict) -> None:
    """Render a compact job card with core listing metadata."""

    with st.container(border=True):
        st.subheader(job.get("title", "Unknown Role"))
        st.caption(f"{job.get('company', 'Unknown Company')} | {job.get('location', 'Remote')}")
        st.write(job.get("description", "No description available."))
        url = job.get("url")
        if url:
            st.link_button("Open Job", url)
