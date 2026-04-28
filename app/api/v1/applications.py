from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.db.base import async_session
from app.db.models.application import Application, ApplicationState
from app.db.models.agent_run import AgentRun
from app.db.models.job_posting import JobPosting
from app.db.models.user import User
from app.deps import get_current_user
from app.schemas.application import ApplicationCreateResponse, ApplicationRead
from app.tasks.agent_tasks import run_email_generation, run_resume_tailor

router = APIRouter()


@router.post("/applications/{job_id}/tailor", response_model=ApplicationCreateResponse)
async def tailor_resume(
    job_id: str,
    user: User = Depends(get_current_user),
) -> ApplicationCreateResponse:
    async with async_session() as session:
        job = await session.get(JobPosting, job_id)
        if not job or job.user_id != user.id:
            raise HTTPException(status_code=404, detail="Job not found")

        application = Application(
            user_id=user.id,
            job_posting_id=job.id,
            state=ApplicationState.TAILORING,
        )
        session.add(application)
        await session.commit()
        await session.refresh(application)

        run = AgentRun(
            user_id=user.id,
            graph_name="ResumeTailoringGraph",
            input_snapshot={"application_id": str(application.id)},
            status="queued",
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)

    task_result = run_resume_tailor.delay(str(user.id), str(application.id), str(run.id))

    async with async_session() as session:
        run = await session.get(AgentRun, run.id)
        if run:
            run.task_id = task_result.id
            await session.commit()

    return ApplicationCreateResponse(application_id=str(application.id), task_id=task_result.id)


@router.post("/applications/{application_id}/generate-email", response_model=ApplicationCreateResponse)
async def generate_email(
    application_id: str,
    user: User = Depends(get_current_user),
) -> ApplicationCreateResponse:
    async with async_session() as session:
        application = await session.get(Application, application_id)
        if not application or application.user_id != user.id:
            raise HTTPException(status_code=404, detail="Application not found")
        if application.state != ApplicationState.TAILORED:
            raise HTTPException(status_code=409, detail="Application is not in TAILORED state")

        run = AgentRun(
            user_id=user.id,
            graph_name="EmailGenerationGraph",
            input_snapshot={"application_id": application_id},
            status="queued",
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)

    task_result = run_email_generation.delay(str(user.id), application_id, str(run.id))

    async with async_session() as session:
        run = await session.get(AgentRun, run.id)
        if run:
            run.task_id = task_result.id
            await session.commit()

    return ApplicationCreateResponse(application_id=application_id, task_id=task_result.id)


@router.get("/applications", response_model=list[ApplicationRead])
async def list_applications(
    state: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
) -> list[ApplicationRead]:
    stmt = select(Application).where(Application.user_id == user.id)
    if state:
        stmt = stmt.where(Application.state == state)
    stmt = stmt.order_by(Application.created_at.desc()).limit(limit).offset(offset)

    async with async_session() as session:
        result = await session.execute(stmt)
        return list(result.scalars().all())
