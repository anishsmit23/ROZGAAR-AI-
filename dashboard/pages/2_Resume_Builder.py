"""Resume builder page — calls FastAPI backend, polls for result."""

from __future__ import annotations

import time
import httpx
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Resume Builder", layout="wide")
st.title("Resume Builder")

job_description = st.text_area("Paste Job Description", height=220)
base_resume = st.text_area("Paste Base Resume (optional if PDF uploaded)", height=120)

if st.button("Generate Tailored Resume") and job_description.strip():
    with st.spinner("Submitting workflow..."):
        resp = httpx.post(f"{API_BASE}/run-workflow", json={
            "task": "tailor_resume",
            "job_description": job_description,
            "base_resume": base_resume,
            "evaluation_target": "resume",
            "retry_count": 0,
            "max_retries": 2,
        })
        workflow_id = resp.json()["workflow_id"]

    progress = st.progress(0, text="Running agents...")
    for i in range(60):          # poll up to 60 seconds
        time.sleep(1)
        status_resp = httpx.get(f"{API_BASE}/status/{workflow_id}")
        status = status_resp.json()["status"]
        progress.progress(min(i * 2, 90), text=f"Status: {status}")
        if status in ("done", "failed"):
            break

    result_resp = httpx.get(f"{API_BASE}/results/{workflow_id}")
    result = result_resp.json()

    if result.get("status") == "done":
        progress.progress(100, text="Done!")
        data = result.get("result", {})
        st.success("Resume generated")
        st.text_area("Tailored Resume", value=data.get("tailored_resume_text", ""), height=260)
        evaluation = data.get("evaluation", {})
        col1, col2 = st.columns(2)
        col1.metric("Judge Score", f"{evaluation.get('score', 0):.1f} / 10")
        col2.write(f"**Verdict:** {evaluation.get('verdict', '')}")
        if evaluation.get("suggestions"):
            st.subheader("Improvement suggestions")
            for s in evaluation["suggestions"]:
                st.write(f"• {s}")
    else:
        st.error(f"Workflow failed: {result.get('error')}")