"""Job listing model definitions."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Job(BaseModel):
    """Represents a structured job listing extracted from search results."""

    job_id: str = Field(description="Stable id for deduplication and tracking")
    title: str
    company: str
    location: str = "Remote"
    description: str
    required_skills: List[str] = Field(default_factory=list)
    url: Optional[HttpUrl] = None
    contact_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
