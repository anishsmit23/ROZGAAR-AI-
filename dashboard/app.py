"""Main Streamlit dashboard landing page."""

from __future__ import annotations

import os

import streamlit as st

st.set_page_config(page_title="Rozgaar — AI job agent", layout="wide", page_icon="🎯")

st.title("Rozgaar — job application copilot")
st.write(
    "Search for roles, tailor your resume, draft outreach, and build interview prep — "
    "or call the same flows from the FastAPI backend for automation."
)

with st.expander("Configuration (read once)"):
    st.markdown(
        """
        - **GROQ_API_KEY** — required for LLM steps (resume, email, interview, evaluator; Groq).
        - **SERPAPI_KEY** — required for **Job Search** (web results via SerpAPI).
        - **BASE_RESUME_PATH** — default PDF to tailor; you can also paste text on the Resume page.
        - **Streamlit + API (split processes):** set `ROZGAAR_USE_API=1` and `ROZGAAR_API_URL` or `PUBLIC_API_URL`
          so the app calls your FastAPI host instead of running agents in-process.
        - **CORS (Streamlit Community Cloud, etc.):** add your app URL to **CORS_EXTRA_ORIGINS** in `.env`.
        """
    )
    st.caption(
        f"In-process mode: `ROZGAAR_USE_API` = `{os.environ.get('ROZGAAR_USE_API', 'not set')}`"
    )

st.subheader("Pages")
st.page_link("pages/0_Job_Search.py", label="1. Job search", icon="🔎")
st.page_link("pages/1_Job_Tracker.py", label="2. Job tracker", icon="📋")
st.page_link("pages/2_Resume_Builder.py", label="3. Resume builder", icon="📝")
st.page_link("pages/3_Email_writer.py", label="4. Email writer", icon="✉️")
st.page_link("pages/4_Interview_agent.py", label="5. Interview prep", icon="🎤")
