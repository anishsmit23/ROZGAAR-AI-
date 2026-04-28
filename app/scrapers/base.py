from __future__ import annotations

from abc import ABC, abstractmethod


class BaseJobScraper(ABC):
    @abstractmethod
    async def search(self, query: dict) -> list[dict]:
        raise NotImplementedError
