from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class JobSearchRequest(BaseModel):
    query: str
    location: str | None = None
    remote: bool = False
    limit: int = 25


class JobRead(BaseModel):
    id: str
    company: str | None = None
    role: str | None = None
    location: str | None = None
    seniority: str | None = None
    source: str | None = None
    url: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
