from __future__ import annotations

from app.scrapers.base import BaseJobScraper


class SerpApiScraper(BaseJobScraper):
    async def search(self, query: dict) -> list[dict]:
        return []
