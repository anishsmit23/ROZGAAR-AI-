"""Email draft generation API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from Agents.orchestrator import run_orchestrator
from api.schemas import EmailRequest, EmailResponse

router = APIRouter(tags=["email"])


@router.post("/generate-email", response_model=EmailResponse)
async def generate_email(payload: EmailRequest) -> EmailResponse:
    """Generate a personalized outreach email draft."""

    try:
        final_state = await run_in_threadpool(
            run_orchestrator,
            {
                "task": "write_email",
                "company": payload.company,
                "role": payload.role,
                "to_email": payload.to_email,
                "candidate_background": payload.candidate_background,
                "evaluation_target": "email",
                "retry_count": 0,
                "max_retries": 2,
            },
        )
        return EmailResponse(
            email_draft=final_state.get("email_draft", {}),
            evaluation=final_state.get("evaluation", {}),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email generation workflow failed: {exc}") from exc
