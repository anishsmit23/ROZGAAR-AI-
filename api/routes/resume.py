"""Resume tailoring API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from Agents.orchestrator import run_orchestrator
from api.schemas import ResumeTailorRequest, ResumeTailorResponse

router = APIRouter(tags=["resume"])


@router.post("/tailor-resume", response_model=ResumeTailorResponse)
async def tailor_resume(payload: ResumeTailorRequest) -> ResumeTailorResponse:
    """Generate a resume variant tailored to the provided JD."""

    try:
        final_state = await run_in_threadpool(
            run_orchestrator,
            {
                "task": "tailor_resume",
                "job_description": payload.job_description,
                "base_resume": payload.base_resume,
                "evaluation_target": "resume",
                "retry_count": 0,
                "max_retries": 2,
            },
        )
        return ResumeTailorResponse(
            tailored_resume_text=final_state.get("tailored_resume_text", ""),
            tailored_resume_pdf_path=final_state.get("tailored_resume_pdf_path", ""),
            evaluation=final_state.get("evaluation", {}),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume tailoring workflow failed: {exc}") from exc
