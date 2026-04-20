"""Streamlit page for interview preparation generation."""

from __future__ import annotations

import streamlit as st

from Agents.orchestrator import run_orchestrator

st.set_page_config(page_title="Interview Agent", layout="wide")
st.title("Interview Agent")

company = st.text_input("Company")
role = st.text_input("Role")
job_description = st.text_area("Job Description", height=220)

if st.button("Generate Interview Prep") and role and job_description:
    result = run_orchestrator(
        {
            "task": "interview_prep",
            "company": company,
            "role": role,
            "job_description": job_description,
        }
    )
    st.text_area("Q&A Set", value=result.get("interview_prep", ""), height=360)
