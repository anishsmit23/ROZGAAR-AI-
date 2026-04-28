from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApplicationState(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    TAILORING = "TAILORING"
    TAILORED = "TAILORED"
    EMAIL_DRAFT = "EMAIL_DRAFT"
    REVIEWED = "REVIEWED"
    SUBMITTED = "SUBMITTED"
    INTERVIEWING = "INTERVIEWING"
    CLOSED = "CLOSED"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    job_posting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_postings.id"))
    resume_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("resume_versions.id"))

    state: Mapped[ApplicationState] = mapped_column(Enum(ApplicationState, name="application_state"), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
