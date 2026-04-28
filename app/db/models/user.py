from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from app.db.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    preferences: Mapped[dict | None] = mapped_column(JSONB(), nullable=True)
    resume_blob: Mapped[str | None] = mapped_column(Text(), nullable=True)
