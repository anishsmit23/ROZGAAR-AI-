from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends

from app.auth.users import fastapi_users
from app.db.base import async_session
from app.db.models.user import User
from app.vector.collections import ChromaCollections


async def get_db() -> AsyncIterator:
    async with async_session() as session:
        yield session


def get_chroma() -> ChromaCollections:
    return ChromaCollections()


get_current_user = fastapi_users.current_user(active=True)
