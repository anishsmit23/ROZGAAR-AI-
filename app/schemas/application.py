from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ApplicationCreateResponse(BaseModel):
    application_id: str
    task_id: str


class ApplicationRead(BaseModel):
    id: str
    job_posting_id: str
    resume_version_id: str | None = None
    state: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
