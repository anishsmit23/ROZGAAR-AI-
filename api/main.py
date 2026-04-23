"""FastAPI application entrypoint."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from api.routes.email import router as email_router
from api.routes.interview import router as interview_router
from api.routes.jobs import router as jobs_router
from api.routes.resume import router as resume_router

app = FastAPI(title="Autonomous AI Job Search Agent", version="0.2.0")

# ← NEW: allow Streamlit (port 8501) and any future frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(email_router)
app.include_router(interview_router)

# ← NEW: in-memory workflow registry (swap for Redis in production)
_workflows: dict[str, dict[str, Any]] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# ← NEW: generic async workflow launcher
@app.post("/run-workflow")
async def run_workflow(payload: dict, background_tasks: BackgroundTasks) -> dict:
    workflow_id = str(uuid.uuid4())
    _workflows[workflow_id] = {"status": "running", "result": None, "error": None}

    from Agents.orchestrator import run_orchestrator

    def _run():
        try:
            result = run_orchestrator(payload)
            _workflows[workflow_id]["result"] = result
            _workflows[workflow_id]["status"] = "done"
        except Exception as exc:
            _workflows[workflow_id]["error"] = str(exc)
            _workflows[workflow_id]["status"] = "failed"

    background_tasks.add_task(_run)
    return {"workflow_id": workflow_id}


# ← NEW: status polling endpoint
@app.get("/status/{workflow_id}")
async def get_status(workflow_id: str) -> dict:
    entry = _workflows.get(workflow_id)
    if not entry:
        return {"status": "not_found"}
    return {"workflow_id": workflow_id, "status": entry["status"]}


# ← NEW: result fetch endpoint
@app.get("/results/{workflow_id}")
async def get_results(workflow_id: str) -> dict:
    entry = _workflows.get(workflow_id)
    if not entry:
        return {"status": "not_found"}
    return {"workflow_id": workflow_id, **entry}


# ← NEW: analytics endpoint for Streamlit training dashboard
@app.get("/analytics")
async def get_analytics() -> dict:
    from config.settings import get_settings
    from memory.job_tracker import JobTracker
    settings = get_settings()
    tracker = JobTracker(settings.db_path)
    rows = tracker.list_all()
    return {
        "total_jobs": len(rows),
        "applied": len([r for r in rows if r["status"] == "applied"]),
        "interviews": len([r for r in rows if r["interview_date"]]),
        "email_sent": len([r for r in rows if r["email_sent"]]),
    }