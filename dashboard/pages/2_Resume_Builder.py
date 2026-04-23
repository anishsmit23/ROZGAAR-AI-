"""Resume builder page — runs the tailoring workflow in-process or via API."""

from __future__ import annotations

import streamlit as st

from dashboard.execution import run_workflow_with_progress

st.set_page_config(page_title="Resume Builder", layout="wide")
st.title("Resume Builder")

st.caption(
    "Aligns your base resume to a job description, then scores the output. "
    "Use **BASE_RESUME_PATH** in `.env` (PDF) or paste text below for best results."
)

job_description = st.text_area("Paste job description", height=220)
base_resume = st.text_area("Paste base resume (optional if PDF is configured)", height=120)

if st.button("Generate tailored resume", type="primary") and job_description.strip():
    with st.spinner("Tailoring and evaluating — this can take a minute…"):
        try:
            result = run_workflow_with_progress(
                {
                    "task": "tailor_resume",
                    "job_description": job_description,
                    "base_resume": base_resume,
                    "evaluation_target": "resume",
                    "retry_count": 0,
                    "max_retries": 2,
                }
            )
        except Exception:
            st.stop()

    text = (result or {}).get("tailored_resume_text", "")
    if not text or text.startswith("Error:"):
        st.error(text or "No output from the agent.")
    else:
        st.success("Resume generated")
        st.text_area("Tailored resume", value=text, height=260, key="out_resume")
        pdf_path = (result or {}).get("tailored_resume_pdf_path", "")
        if pdf_path:
            st.caption(f"PDF path: `{pdf_path}` (under `data/outputs` when running locally).")
        evaluation = (result or {}).get("evaluation", {}) or {}
        col1, col2 = st.columns(2)
        col1.metric("Judge score", f"{float(evaluation.get('score', 0) or 0):.1f} / 10")
        col2.write(f"**Verdict:** {evaluation.get('verdict', '')}")
        if evaluation.get("suggestions"):
            st.subheader("Improvement suggestions")
            for s in evaluation["suggestions"]:
                st.write(f"• {s}")
