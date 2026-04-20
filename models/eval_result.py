"""Evaluation result model definitions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvalResult(BaseModel):
    """Quality score and feedback returned by evaluator agent."""

    score: float = Field(ge=0.0, le=10.0)
    verdict: str
    suggestions: list[str] = Field(default_factory=list)
    criteria: dict[str, float] = Field(default_factory=dict)
