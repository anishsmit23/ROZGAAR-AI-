"""FastAPI application entrypoint for backend services."""

from __future__ import annotations

from fastapi import FastAPI

from api.routes.email import router as email_router
from api.routes.interview import router as interview_router
from api.routes.jobs import router as jobs_router
from api.routes.resume import router as resume_router

app = FastAPI(title="Autonomous AI Job Search Agent", version="0.1.0")

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(email_router)
app.include_router(interview_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint used by local and container runtimes."""

    return {"status": "ok"}
