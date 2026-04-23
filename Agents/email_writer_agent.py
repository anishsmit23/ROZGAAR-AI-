"""Email writer agent for personalized cold outreach drafts."""

from __future__ import annotations

from hashlib import md5
from pathlib import Path

from config.prompts import EMAIL_WRITER_PROMPT
from config import settings as app_settings
from models.email_draft import EmailDraft
from tools.file_io_tool import write_text


def run_email_writer_agent(state: dict) -> dict:
    """Generate a personalized cold email and save it as a text artifact."""

    company = state.get("company", "the company")
    role = state.get("role", "the role")
    background = state.get("candidate_background", "")

    prompt = (
        f"{EMAIL_WRITER_PROMPT}\n\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Candidate Background: {background}\n\n"
        "Write only subject and body in plain text."
    )

    response = app_settings.get_llm().invoke(prompt)
    raw_text = str(response.content).strip()

    if "\n" in raw_text:
        subject_line, body = raw_text.split("\n", maxsplit=1)
    else:
        subject_line, body = f"Application Interest: {role}", raw_text

    subject = subject_line.replace("Subject:", "").strip()
    digest = md5(f"{company}:{role}:{subject}".encode("utf-8")).hexdigest()[:10]
    draft = EmailDraft(
        draft_id=f"email_{digest}",
        subject=subject,
        body=body.strip(),
        company=company,
        role=role,
        to_email=state.get("to_email"),
    )

    out = state.get("email_output_path")
    path = Path(out) if out else Path("data/outputs/email_draft.txt")
    output_path = write_text(
        path,
        content=f"Subject: {draft.subject}\n\n{draft.body}",
    )

    state["email_draft"] = draft.model_dump(mode="json")
    state["email_output_path"] = str(output_path)
    return state
