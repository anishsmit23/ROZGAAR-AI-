"""Interview prep API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from Agents.orchestrator import run_orchestrator
from api.schemas import InterviewPrepRequest, InterviewPrepResponse

router = APIRouter(tags=["interview"])


@router.post("/interview-prep", response_model=InterviewPrepResponse)
async def interview_prep(payload: InterviewPrepRequest) -> InterviewPrepResponse:
    """Generate interview prep questions and answer guidelines."""

    try:
        final_state = await run_in_threadpool(
            run_orchestrator,
            {
                "task": "interview_prep",
                "company": payload.company,
                "role": payload.role,
                "job_description": payload.job_description,
            },
        )
        return InterviewPrepResponse(interview_prep=final_state.get("interview_prep", ""))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interview prep workflow failed: {exc}") from exc
