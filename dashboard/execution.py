"""Run agent workflows from Streamlit: in-process by default, or remote API when configured."""

from __future__ import annotations

import os

import httpx
import streamlit as st

from Agents.orchestrator import run_orchestrator
from config.settings import get_settings
from exceptions import ConfigurationError, JobSearchAgentError, ToolExecutionError

_TIMEOUT = 600.0


def use_remote_api() -> bool:
    return os.environ.get("ROZGAAR_USE_API", "").strip().lower() in ("1", "true", "yes")


def _api_base() -> str:
    raw = (os.environ.get("ROZGAAR_API_URL") or get_settings().public_api_url or "").strip()
    return raw.rstrip("/")


def run_workflow_in_process(state: dict) -> dict:
    """Execute the LangGraph pipeline in the Streamlit process (default for `streamlit run`)."""

    return run_orchestrator(state)


def run_workflow(state: dict) -> dict:
    """
    If ROZGAAR_USE_API=1, call the FastAPI backend. Otherwise run in-process.
    In-process is recommended when only Streamlit is started (e.g. Streamlit Community Cloud
    with bundled logic, or local `streamlit run`).
    """

    if not use_remote_api():
        return run_workflow_in_process(state)

    base = _api_base()
    if not base:
        st.warning("ROZGAAR_USE_API is set but no ROZGAAR_API_URL / PUBLIC_API_URL. Running in-process.")
        return run_workflow_in_process(state)

    task = state.get("task", "job_search")
    with httpx.Client(timeout=_TIMEOUT) as client:
        if task == "job_search":
            payload = state.get("job_search", {}) or {}
            r = client.post(
                f"{base}/search",
                json={"query": payload.get("query", "jobs"), "max_results": int(payload.get("max_results", 10))},
            )
            r.raise_for_status()
            return {"task": "job_search", "jobs": r.json().get("jobs", [])}
        if task == "tailor_resume":
            r = client.post(
                f"{base}/tailor-resume",
                json={"job_description": state.get("job_description", ""), "base_resume": state.get("base_resume", "")},
            )
            r.raise_for_status()
            body = r.json()
            return {
                "task": "tailor_resume",
                "tailored_resume_text": body.get("tailored_resume_text", ""),
                "tailored_resume_pdf_path": body.get("tailored_resume_pdf_path", ""),
                "evaluation": body.get("evaluation", {}),
            }
        if task == "write_email":
            r = client.post(
                f"{base}/generate-email",
                json={
                    "company": state.get("company", ""),
                    "role": state.get("role", ""),
                    "candidate_background": state.get("candidate_background", ""),
                    "to_email": state.get("to_email"),
                },
            )
            r.raise_for_status()
            body = r.json()
            return {
                "task": "write_email",
                "email_draft": body.get("email_draft", {}),
                "evaluation": body.get("evaluation", {}),
            }
        if task == "interview_prep":
            r = client.post(
                f"{base}/interview-prep",
                json={
                    "company": state.get("company", ""),
                    "role": state.get("role", ""),
                    "job_description": state.get("job_description", ""),
                },
            )
            r.raise_for_status()
            return {"task": "interview_prep", "interview_prep": r.json().get("interview_prep", "")}
        return run_workflow_in_process(state)


def run_workflow_with_progress(state: dict) -> dict:
    """Streamlit-friendly wrapper: spinner + error surface."""

    with st.spinner("Running agents — this can take a minute…"):
        try:
            return run_workflow(state)
        except (ConfigurationError, ToolExecutionError, JobSearchAgentError) as exc:
            st.error(str(exc))
            raise
        except httpx.HTTPError as exc:
            st.error(f"API request failed: {exc}")
            raise
