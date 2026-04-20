"""Job discovery and listing routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from Agents.orchestrator import run_orchestrator
from api.schemas import JobListResponse, JobSearchRequest
from config.settings import get_settings
from memory.job_tracker import JobTracker

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=JobListResponse)
async def get_jobs() -> JobListResponse:
    """Return jobs currently tracked in SQLite."""

    try:
        settings = get_settings()
        tracker = JobTracker(settings.db_path)
        return JobListResponse(jobs=tracker.list_all())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tracked jobs: {exc}") from exc


@router.post("/search", response_model=JobListResponse)
async def search_jobs(payload: JobSearchRequest) -> JobListResponse:
    """Search for jobs using query and result cap provided by caller."""

    try:
        final_state = await run_in_threadpool(
            run_orchestrator,
            {
                "task": "job_search",
                "job_search": {"query": payload.query, "max_results": payload.max_results},
            },
        )
        return JobListResponse(jobs=final_state.get("jobs", []))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search workflow failed: {exc}") from exc
