"""Interview preparation agent — retrieves similar JDs from ChromaDB before generating Q&A."""

from __future__ import annotations

from config.prompts import INTERVIEW_PREP_PROMPT
from config import settings as app_settings
from memory.vector_store import VectorStore
from tools.file_io_tool import write_text
from pathlib import Path


def run_interview_prep_agent(state: dict) -> dict:
    role = state.get("role", "Software Engineer")
    company = state.get("company", "Target Company")
    job_description = state.get("job_description", "")

    # ← NEW: retrieve similar job descriptions for richer context
    settings = app_settings.get_settings()
    vector_store = VectorStore(settings.chroma_path)
    similar_jobs = vector_store.search_jobs(
        query=f"{role} {job_description[:300]}", limit=3
    )
    context_block = ""
    if similar_jobs:
        snippets = [j["description"][:300] for j in similar_jobs]
        context_block = "\n\nSimilar roles for context:\n" + "\n---\n".join(snippets)

    prompt = (
        f"{INTERVIEW_PREP_PROMPT}\n\n"
        f"Role: {role}\n"
        f"Company: {company}\n"
        f"Job Description: {job_description}"
        f"{context_block}\n\n"
        "Create: 5 technical, 3 behavioral (STAR), 2 culture-fit questions with strong answer outlines."
    )

    response = app_settings.get_llm().invoke(prompt)
    qa_text = str(response.content).strip()

    output_path = write_text(Path("data/outputs/interview_prep.txt"), qa_text)

    state["interview_prep"] = qa_text
    state["interview_prep_path"] = str(output_path)
    return state