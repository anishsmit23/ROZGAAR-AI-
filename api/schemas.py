"""Shared request and response schemas for API routes."""

from __future__ import annotations

from pydantic import BaseModel, Field


class JobSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    max_results: int = Field(default=10, ge=1, le=50)


class JobListResponse(BaseModel):
    status: str = "ok"
    jobs: list[dict]


class ResumeTailorRequest(BaseModel):
    job_description: str = Field(min_length=10)
    base_resume: str = ""


class ResumeTailorResponse(BaseModel):
    status: str = "ok"
    tailored_resume_text: str
    tailored_resume_pdf_path: str
    evaluation: dict


class EmailRequest(BaseModel):
    company: str
    role: str
    candidate_background: str = ""
    to_email: str | None = None


class EmailResponse(BaseModel):
    status: str = "ok"
    email_draft: dict
    evaluation: dict


class InterviewPrepRequest(BaseModel):
    company: str
    role: str
    job_description: str


class InterviewPrepResponse(BaseModel):
    status: str = "ok"
    interview_prep: str


class AgentResponse(BaseModel):
    status: str = "ok"
    data: dict
