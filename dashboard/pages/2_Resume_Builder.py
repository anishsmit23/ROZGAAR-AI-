"""Streamlit page for generating tailored resumes."""

from __future__ import annotations

import streamlit as st

from Agents.orchestrator import run_orchestrator

st.set_page_config(page_title="Resume Builder", layout="wide")
st.title("Resume Builder")

job_description = st.text_area("Paste Job Description", height=220)

if st.button("Generate Tailored Resume") and job_description.strip():
    result = run_orchestrator(
        {
            "task": "tailor_resume",
            "job_description": job_description,
            "evaluation_target": "resume",
            "retry_count": 0,
            "max_retries": 2,
        }
    )
    st.success("Resume generated")
    st.text_area("Tailored Resume", value=result.get("tailored_resume_text", ""), height=260)
    st.json(result.get("evaluation", {}))
