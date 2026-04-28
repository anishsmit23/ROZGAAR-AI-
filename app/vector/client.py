from __future__ import annotations

from urllib.parse import urlparse

import chromadb

from app.config import get_settings

settings = get_settings()


def get_chroma_client() -> chromadb.HttpClient:
    parsed = urlparse(settings.chroma_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8000
    return chromadb.HttpClient(host=host, port=port)
