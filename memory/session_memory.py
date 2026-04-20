"""Simple in-process session memory manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionMemory:
    """Short-lived memory object for request-scoped state."""

    payload: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        """Store a key-value pair in session memory."""

        self.payload[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Read value from session memory with fallback."""

        return self.payload.get(key, default)

    def clear(self) -> None:
        """Clear all in-memory session data."""

        self.payload.clear()
