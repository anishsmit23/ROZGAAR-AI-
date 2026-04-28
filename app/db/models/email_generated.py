from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EmailGenerated(Base):
    __tablename__ = "emails_generated"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"))
    subject: Mapped[str | None] = mapped_column(Text())
    body: Mapped[str | None] = mapped_column(Text())
    tone: Mapped[str | None] = mapped_column(String(64))
    version: Mapped[int | None] = mapped_column(Integer())
    eval_score: Mapped[float | None] = mapped_column(Float())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
