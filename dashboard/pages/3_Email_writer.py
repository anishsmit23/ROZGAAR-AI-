"""Streamlit page for generating personalized outreach emails."""

from __future__ import annotations

import streamlit as st

from Agents.orchestrator import run_orchestrator

st.set_page_config(page_title="Email Writer", layout="wide")
st.title("Email Writer")

company = st.text_input("Target Company")
role = st.text_input("Target Role")
background = st.text_area("Your Background Highlights", height=180)

if st.button("Generate Email") and company and role:
    result = run_orchestrator(
        {
            "task": "write_email",
            "company": company,
            "role": role,
            "candidate_background": background,
            "evaluation_target": "email",
            "retry_count": 0,
            "max_retries": 2,
        }
    )
    draft = result.get("email_draft", {})
    st.subheader(draft.get("subject", "Subject"))
    st.write(draft.get("body", ""))
    st.json(result.get("evaluation", {}))
