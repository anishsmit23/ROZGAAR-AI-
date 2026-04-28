from __future__ import annotations

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import get_settings


def get_checkpointer() -> PostgresSaver:
    settings = get_settings()
    return PostgresSaver.from_conn_string(settings.database_url)
