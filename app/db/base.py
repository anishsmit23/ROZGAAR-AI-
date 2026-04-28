from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

async_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)
