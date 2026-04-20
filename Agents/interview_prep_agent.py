"""Interview preparation agent generating role-targeted Q&A sets."""

from __future__ import annotations

from config.prompts import INTERVIEW_PREP_PROMPT
from config import settings as app_settings
from tools.file_io_tool import write_text


def run_interview_prep_agent(state: dict) -> dict:
    """Generate technical, behavioral, and culture-fit interview prep."""

    role = state.get("role", "Software Engineer")
    company = state.get("company", "Target Company")
    job_description = state.get("job_description", "")

    prompt = (
        f"{INTERVIEW_PREP_PROMPT}\n\n"
        f"Role: {role}\n"
        f"Company: {company}\n"
        f"Job Description: {job_description}\n\n"
        "Create: 5 technical, 3 behavioral (STAR), 2 culture-fit questions with strong answer outlines."
    )

    response = app_settings.get_llm().invoke(prompt)
    qa_text = str(response.content).strip()

    output_path = write_text(
        __import__("pathlib").Path("data/outputs/interview_prep.txt"),
        qa_text,
    )

    state["interview_prep"] = qa_text
    state["interview_prep_path"] = str(output_path)
    return state
