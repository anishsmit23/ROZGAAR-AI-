from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.db.base import async_session
from app.db.models.agent_event import AgentEvent
from app.db.models.agent_run import AgentRun

router = APIRouter()


@router.websocket("/ws/tasks/{task_id}")
async def task_events_ws(websocket: WebSocket, task_id: str) -> None:
    await websocket.accept()
    last_seen: datetime | None = None

    async with async_session() as session:
        stmt = select(AgentRun).where(AgentRun.task_id == task_id)
        result = await session.execute(stmt)
        run = result.scalar_one_or_none()

    if not run:
        await websocket.send_json({"error": "Unknown task_id"})
        await websocket.close()
        return

    try:
        while True:
            async with async_session() as session:
                stmt = select(AgentEvent).where(AgentEvent.run_id == run.id)
                if last_seen:
                    stmt = stmt.where(AgentEvent.created_at > last_seen)
                stmt = stmt.order_by(AgentEvent.created_at.asc())

                result = await session.execute(stmt)
                events = list(result.scalars().all())
                if events:
                    last_seen = events[-1].created_at
                    await websocket.send_json(
                        {
                            "run_id": str(run.id),
                            "events": [
                                {
                                    "step_name": e.step_name,
                                    "payload": e.payload,
                                    "created_at": e.created_at.isoformat() if e.created_at else None,
                                }
                                for e in events
                            ],
                        }
                    )

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
