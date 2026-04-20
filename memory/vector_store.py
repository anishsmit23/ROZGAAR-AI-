"""ChromaDB wrapper for semantic storage of jobs and application artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from models.job import Job


class VectorStore:
    """Manages ChromaDB collections for job search workflows."""

    def __init__(self, persist_directory: Path) -> None:
        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.jobs_seen: Collection = self.client.get_or_create_collection(name="jobs_seen")
        self.applications: Collection = self.client.get_or_create_collection(name="applications")

    def add_job(self, job: Job) -> None:
        """Store a job listing in the jobs_seen collection."""

        self.jobs_seen.upsert(
            ids=[job.job_id],
            documents=[job.description],
            metadatas=[
                {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "url": str(job.url) if job.url else "",
                }
            ],
        )

    def search_jobs(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Semantic search over scraped job descriptions."""

        result = self.jobs_seen.query(query_texts=[query], n_results=limit)
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metadata_rows = result.get("metadatas", [[]])[0]

        return [
            {
                "job_id": ids[index],
                "description": docs[index],
                "metadata": metadata_rows[index],
            }
            for index in range(len(ids))
        ]

    def add_application(self, application_id: str, content: str, metadata: dict[str, Any]) -> None:
        """Store generated resume/email artifacts for traceability."""

        self.applications.upsert(ids=[application_id], documents=[content], metadatas=[metadata])

    def get_application(self, application_id: str) -> dict[str, Any] | None:
        """Fetch one generated artifact by id."""

        result = self.applications.get(ids=[application_id], include=["documents", "metadatas"])
        ids = result.get("ids", [])
        if not ids:
            return None

        return {
            "application_id": ids[0],
            "content": result.get("documents", [""])[0],
            "metadata": result.get("metadatas", [{}])[0],
        }
