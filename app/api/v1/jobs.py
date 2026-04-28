from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.db.base import async_session
from app.db.models.job_posting import JobPosting
from app.db.models.user import User
from app.deps import get_current_user
from app.schemas.job import JobRead

router = APIRouter()


@router.get("/jobs", response_model=list[JobRead])
async def list_jobs(
    company: str | None = None,
    seniority: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
) -> list[JobRead]:
    stmt = select(JobPosting).where(JobPosting.user_id == user.id)
    if company:
        stmt = stmt.where(JobPosting.company == company)
    if seniority:
        stmt = stmt.where(JobPosting.seniority == seniority)
    stmt = stmt.order_by(JobPosting.created_at.desc()).limit(limit).offset(offset)

    async with async_session() as session:
        result = await session.execute(stmt)
        return list(result.scalars().all())
