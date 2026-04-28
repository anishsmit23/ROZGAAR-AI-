from __future__ import annotations

from app.vector.client import get_chroma_client


class ChromaCollections:
    def __init__(self) -> None:
        self.client = get_chroma_client()
        self.job_embeddings = self.client.get_or_create_collection("job_embeddings")
        self.resume_chunk_embeddings = self.client.get_or_create_collection("resume_chunk_embeddings")
        self.skill_taxonomy = self.client.get_or_create_collection("skill_taxonomy")
