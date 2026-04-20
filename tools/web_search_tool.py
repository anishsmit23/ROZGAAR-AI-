"""Web search wrapper powered by SerpAPI with graceful fallback."""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from config.settings import get_settings
from exceptions import ToolExecutionError


def search_web(query: str, num_results: int = 10) -> list[dict[str, Any]]:
    """Search jobs or companies and return normalized organic results."""

    settings = get_settings()
    if not settings.serpapi_key:
        raise ToolExecutionError("SERPAPI_KEY is missing. Please update .env.")

    params = {
        "q": query,
        "api_key": settings.serpapi_key,
        "engine": "google",
        "num": num_results,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get("https://serpapi.com/search.json", params=params)
            response.raise_for_status()
            payload = response.json()

        organic_results = payload.get("organic_results", [])
        normalized: list[dict[str, Any]] = []
        for row in organic_results:
            normalized.append(
                {
                    "title": row.get("title", "Untitled"),
                    "url": row.get("link", ""),
                    "snippet": row.get("snippet", ""),
                    "source": row.get("source", "google"),
                }
            )
        return normalized
    except Exception as exc:
        logger.exception("Search API call failed")
        raise ToolExecutionError(f"search_web failed: {exc}") from exc
