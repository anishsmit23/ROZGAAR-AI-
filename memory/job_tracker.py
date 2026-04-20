"""SQLite-backed tracker for job applications and status changes."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from loguru import logger


class JobTracker:
    """Encapsulates CRUD operations for job application records."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS job_applications (
                    job_id TEXT PRIMARY KEY,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    applied_date TEXT,
                    resume_version TEXT,
                    email_sent INTEGER DEFAULT 0,
                    interview_date TEXT
                )
                """
            )
        logger.debug("Job tracker initialized at {}", self.db_path)

    def upsert(self, record: dict[str, Any]) -> None:
        """Insert or update a job application row."""

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO job_applications (
                    job_id, company, role, status, applied_date,
                    resume_version, email_sent, interview_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    company=excluded.company,
                    role=excluded.role,
                    status=excluded.status,
                    applied_date=excluded.applied_date,
                    resume_version=excluded.resume_version,
                    email_sent=excluded.email_sent,
                    interview_date=excluded.interview_date
                """,
                (
                    record["job_id"],
                    record["company"],
                    record["role"],
                    record.get("status", "saved"),
                    record.get("applied_date"),
                    record.get("resume_version"),
                    int(bool(record.get("email_sent", False))),
                    record.get("interview_date"),
                ),
            )

    def get(self, job_id: str) -> dict[str, Any] | None:
        """Fetch one tracked job by id."""

        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT job_id, company, role, status, applied_date, resume_version, email_sent, interview_date "
                "FROM job_applications WHERE job_id = ?",
                (job_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "job_id": row[0],
            "company": row[1],
            "role": row[2],
            "status": row[3],
            "applied_date": row[4],
            "resume_version": row[5],
            "email_sent": bool(row[6]),
            "interview_date": row[7],
        }

    def list_all(self) -> list[dict[str, Any]]:
        """Return all tracked jobs ordered by role and company."""

        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT job_id, company, role, status, applied_date, resume_version, email_sent, interview_date "
                "FROM job_applications ORDER BY role, company"
            )
            rows = cursor.fetchall()

        return [
            {
                "job_id": row[0],
                "company": row[1],
                "role": row[2],
                "status": row[3],
                "applied_date": row[4],
                "resume_version": row[5],
                "email_sent": bool(row[6]),
                "interview_date": row[7],
            }
            for row in rows
        ]

    def delete(self, job_id: str) -> None:
        """Delete a tracked row by id."""

        with self._connect() as connection:
            connection.execute("DELETE FROM job_applications WHERE job_id = ?", (job_id,))
