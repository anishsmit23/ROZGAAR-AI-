"""Streamlit page for interview preparation generation."""

from __future__ import annotations

import streamlit as st

from dashboard.execution import run_workflow_with_progress

st.set_page_config(page_title="Interview Agent", layout="wide")
st.title("Interview prep")

st.caption(
    "Uses the job description and similar jobs from your Chroma store (if any) to generate Q&A. "
    "Requires **GROQ_API_KEY** (Groq)."
)

company = st.text_input("Company")
role = st.text_input("Role")
job_description = st.text_area("Job description", height=220)

if st.button("Generate interview prep", type="primary") and role and job_description.strip():
    with st.spinner("Preparing Q&A — this can take a minute…"):
        try:
            result = run_workflow_with_progress(
                {
                    "task": "interview_prep",
                    "company": company,
                    "role": role,
                    "job_description": job_description,
                }
            )
        except Exception:
            st.stop()

    st.text_area("Q&A set", value=(result or {}).get("interview_prep", ""), height=360)
