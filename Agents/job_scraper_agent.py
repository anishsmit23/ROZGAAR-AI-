"""Job scraper agent that queries the web and stores normalized job records."""

from __future__ import annotations

from hashlib import md5
from typing import TypedDict

from config import settings as app_settings
from memory.job_tracker import JobTracker
from memory.vector_store import VectorStore
from models.job import Job
from tools.web_search_tool import search_web


class JobScraperInput(TypedDict, total=False):
    query: str
    max_results: int


def run_job_scraper_agent(state: dict) -> dict:
    """Search for jobs, normalize records, and persist to memory layers."""

    payload: JobScraperInput = state.get("job_search", {})
    query = payload.get("query", "machine learning engineer jobs remote")
    max_results = int(payload.get("max_results", 10))

    settings = app_settings.get_settings()
    tracker = JobTracker(settings.db_path)
    vector_store = VectorStore(settings.chroma_path)

    search_rows = search_web(query, num_results=max_results)
    jobs: list[Job] = []

    for row in search_rows:
        digest = md5(f"{row.get('title', '')}:{row.get('url', '')}".encode("utf-8")).hexdigest()[:12]
        job = Job(
            job_id=f"job_{digest}",
            title=row.get("title", "Unknown role"),
            company=(row.get("source") or "Unknown company").title(),
            location="Remote",
            description=row.get("snippet", ""),
            required_skills=[],
            url=row.get("url") or None,
        )
        jobs.append(job)
        vector_store.add_job(job)
        tracker.upsert(
            {
                "job_id": job.job_id,
                "company": job.company,
                "role": job.title,
                "status": "saved",
                "resume_version": None,
                "email_sent": False,
            }
        )

    state["jobs"] = [job.model_dump(mode="json") for job in jobs]
    return state
