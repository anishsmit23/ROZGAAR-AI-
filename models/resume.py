"""Resume model definitions."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ResumeBullet(BaseModel):
    """A single bullet point within a resume section."""

    text: str


class ResumeSection(BaseModel):
    """A resume section (e.g., experience, projects)."""

    name: str
    bullets: List[ResumeBullet] = Field(default_factory=list)


class Resume(BaseModel):
    """Structured resume object used by tailoring workflows."""

    candidate_name: str
    headline: str = ""
    summary: str = ""
    sections: List[ResumeSection] = Field(default_factory=list)
