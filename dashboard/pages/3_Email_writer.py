"""Streamlit page for generating personalized outreach emails."""

from __future__ import annotations

import streamlit as st

from dashboard.execution import run_workflow_with_progress

st.set_page_config(page_title="Email Writer", layout="wide")
st.title("Email writer")

st.caption("Generates a cold email draft, then runs the evaluator. Set **GROQ_API_KEY** in `.env`.")

company = st.text_input("Target company")
role = st.text_input("Target role")
to_email = st.text_input("Recipient email (optional)", value="")
background = st.text_area("Your background highlights", height=180)

if st.button("Generate email", type="primary") and company and role:
    with st.spinner("Writing and evaluating — this can take a minute…"):
        try:
            result = run_workflow_with_progress(
                {
                    "task": "write_email",
                    "company": company,
                    "role": role,
                    "to_email": to_email or None,
                    "candidate_background": background,
                    "evaluation_target": "email",
                    "retry_count": 0,
                    "max_retries": 2,
                }
            )
        except Exception:
            st.stop()

    draft = (result or {}).get("email_draft", {}) or {}
    st.subheader(draft.get("subject", "Subject"))
    st.write(draft.get("body", ""))
    eval_block = (result or {}).get("evaluation", {}) or {}
    with st.expander("Evaluator details"):
        st.json(eval_block)
