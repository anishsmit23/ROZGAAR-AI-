"""Resume tailoring agent that aligns resume language with target JD."""

from __future__ import annotations

from pathlib import Path

from config.prompts import RESUME_TAILOR_PROMPT
from config import settings as app_settings
from tools.file_io_tool import write_text
from tools.pdf_tool import extract_pdf_text, generate_resume_pdf


def run_resume_tailor_agent(state: dict) -> dict:
    """Generate a tailored resume draft and persist TXT + PDF outputs."""

    settings = app_settings.get_settings()
    base_resume_path = settings.base_resume_path
    job_description = state.get("job_description", "")

    source_text = extract_pdf_text(base_resume_path) if base_resume_path.exists() else state.get("base_resume", "")
    prompt = (
        f"{RESUME_TAILOR_PROMPT}\n\n"
        f"Base Resume:\n{source_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Return concise tailored bullet points only."
    )

    response = app_settings.get_llm().invoke(prompt)
    tailored_text = str(response.content).strip()

    out_dir = Path("data/outputs")
    txt_path = write_text(out_dir / "tailored_resume.txt", tailored_text)
    pdf_path = generate_resume_pdf(
        output_path=out_dir / "tailored_resume.pdf",
        title="Tailored Resume",
        lines=[line.strip() for line in tailored_text.splitlines() if line.strip()],
    )

    state["tailored_resume_text"] = tailored_text
    state["tailored_resume_txt_path"] = str(txt_path)
    state["tailored_resume_pdf_path"] = str(pdf_path)
    return state
