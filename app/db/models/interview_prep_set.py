from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InterviewPrepSet(Base):
    __tablename__ = "interview_prep_sets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"))
    questions: Mapped[dict | None] = mapped_column(JSONB())
    answers: Mapped[dict | None] = mapped_column(JSONB())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
