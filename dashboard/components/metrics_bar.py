"""Small dashboard metrics component."""

from __future__ import annotations

import streamlit as st


def render_metrics(total_jobs: int, applied: int, interviews: int) -> None:
    """Render key dashboard metrics in 3 columns."""

    col1, col2, col3 = st.columns(3)
    col1.metric("Jobs Tracked", total_jobs)
    col2.metric("Applied", applied)
    col3.metric("Interviews", interviews)
