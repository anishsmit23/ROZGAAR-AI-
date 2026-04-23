"""FastAPI application entrypoint."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware

from api.routes.email import router as email_router
from api.routes.interview import router as interview_router
from api.routes.jobs import router as jobs_router
from api.routes.resume import router as resume_router
from config.settings import get_settings

app = FastAPI(title="Autonomous AI Job Search Agent", version="0.2.0")

_settings = get_settings()
_cors_origins = list(
    {
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
    }
    | {o.strip() for o in _settings.cors_extra_origins.split(",") if o.strip()}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(email_router)
app.include_router(interview_router)

# ← NEW: in-memory workflow registry (swap for Redis in production)
_workflows: dict[str, dict[str, Any]] = {}

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_token = request.headers.get("session_token", str(uuid.uuid4()))
    request.state.session_token = session_token
    response = await call_next(request)
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# ← NEW: generic async workflow launcher
@app.post("/run-workflow")
async def run_workflow(payload: dict, background_tasks: BackgroundTasks, request: Request) -> dict:
    # Stable id for this run — do not use session_token (a new id per request if header missing).
    workflow_id = str(uuid.uuid4())
    _workflows[workflow_id] = {"status": "running", "result": None, "error": None}

    from Agents.orchestrator import run_orchestrator

    def _run():
        try:
            result = run_orchestrator(payload, thread_id=workflow_id)
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
    from Agents.orchestrator import _COMPILED_GRAPH
    config = {"configurable": {"thread_id": workflow_id}}
    state_tuple = _COMPILED_GRAPH.get_state(config)
    
    current_node = state_tuple.next[0] if state_tuple.next else None
    state_snapshot = state_tuple.values
    
    entry = _workflows.get(workflow_id, {"status": "unknown"})
    
    return {
        "workflow_id": workflow_id,
        "status": entry.get("status", "unknown"),
        "current_node": current_node,
        "state_snapshot": state_snapshot,
        "progress_pct": 100 if entry.get("status") == "done" else 50
    }


# ← NEW: result fetch endpoint
@app.get("/results/{workflow_id}")
async def get_results(workflow_id: str) -> dict:
    from Agents.orchestrator import _COMPILED_GRAPH
    config = {"configurable": {"thread_id": workflow_id}}
    state_tuple = _COMPILED_GRAPH.get_state(config)
    
    entry = _workflows.get(workflow_id, {})
    return {
        "workflow_id": workflow_id,
        "status": entry.get("status", "unknown"),
        "error": entry.get("error"),
        "result": state_tuple.values if state_tuple.values else entry.get("result")
    }

@app.get("/listings")
async def get_listings() -> dict:
    """Queries ChromaDB and returns matching job listings as JSON."""
    from config.settings import get_settings
    from memory.vector_store import VectorStore
    settings = get_settings()
    vector_store = VectorStore(settings.chroma_path)
    
    result = vector_store.jobs_seen.get(limit=500, include=["documents", "metadatas"])
    ids = result.get("ids", []) or []
    docs = result.get("documents", [])
    metadatas = result.get("metadatas", [])
    
    jobs = []
    for i in range(len(ids)):
        jobs.append({
            "job_id": ids[i],
            "description": docs[i] if docs else "",
            "metadata": metadatas[i] if metadatas else {}
        })
    return {"listings": jobs}


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