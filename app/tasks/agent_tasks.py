from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from app.db.base import async_session
from app.db.models.agent_event import AgentEvent
from app.db.models.agent_run import AgentRun
from app.tasks.celery_app import celery_app


async def _set_run_status(run_id: str, status: str, output: dict | None = None) -> None:
    async with async_session() as session:
        run = await session.get(AgentRun, uuid.UUID(run_id))
        if not run:
            return
        run.status = status
        if output:
            run.output_snapshot = output
        await session.commit()


async def _log_event(run_id: str, user_id: str, step_name: str, payload: dict | None = None) -> None:
    async with async_session() as session:
        event = AgentEvent(
            run_id=uuid.UUID(run_id),
            user_id=uuid.UUID(user_id),
            step_name=step_name,
            payload=payload or {},
        )
        session.add(event)
        await session.commit()


@celery_app.task(bind=True, max_retries=3, queue="agents")
def run_job_search(self, user_id: str, query_params: dict, run_id: str) -> dict:
    async def _run() -> dict:
        await _set_run_status(run_id, "running")
        await _log_event(run_id, user_id, "search_started", {"query": query_params})
        await _log_event(run_id, user_id, "search_completed", {"total": 0})
        output = {"completed_at": datetime.now(tz=timezone.utc).isoformat()}
        await _set_run_status(run_id, "completed", output)
        return output

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2, queue="agents")
def run_resume_tailor(self, user_id: str, application_id: str, run_id: str) -> dict:
    async def _run() -> dict:
        await _set_run_status(run_id, "running")
        await _log_event(run_id, user_id, "tailor_started", {"application_id": application_id})
        await _log_event(run_id, user_id, "tailor_completed", {"application_id": application_id})
        await _set_run_status(run_id, "completed", {"application_id": application_id})
        output = {"application_id": application_id}
        return output

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2, queue="agents")
def run_email_generation(self, user_id: str, application_id: str, run_id: str) -> dict:
    async def _run() -> dict:
        await _set_run_status(run_id, "running")
        await _log_event(run_id, user_id, "email_started", {"application_id": application_id})
        await _log_event(run_id, user_id, "email_completed", {"application_id": application_id})
        await _set_run_status(run_id, "completed", {"application_id": application_id})
        output = {"application_id": application_id}
        return output

    return asyncio.run(_run())
