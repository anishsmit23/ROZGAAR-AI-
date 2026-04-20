"""Email draft model definitions."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class EmailDraft(BaseModel):
    """Represents a cold outreach email generated for a target role."""

    draft_id: str
    to_email: Optional[EmailStr] = None
    subject: str
    body: str
    company: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
