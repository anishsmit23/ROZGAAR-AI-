from __future__ import annotations

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, queue="scrapers")
def scrape_job_board(self, source: str, query: dict) -> dict:
    return {"source": source, "query": query, "status": "queued"}
