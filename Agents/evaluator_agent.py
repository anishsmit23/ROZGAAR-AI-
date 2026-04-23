"""Evaluator agent using LLM-as-judge to score generated artifacts."""

from __future__ import annotations

import json
import re

from config.prompts import EVALUATOR_PROMPT
from config import settings as app_settings
from models.eval_result import EvalResult


def run_evaluator_agent(state: dict) -> dict:
    target = state.get("evaluation_target", "resume")
    job_description = state.get("job_description", "")

    if target == "resume":
        content = state.get("tailored_resume_text", "")
    else:
        content = state.get("email_draft", {}).get("body", "")

    prompt = (
        f"{EVALUATOR_PROMPT}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Target: {target}\n"
        f"Content:\n{content}\n\n"
        "Return ONLY a JSON object with keys: score (float 0-10), verdict (str), "
        "suggestions (list[str] of specific missing keywords or improvements), "
        "criteria (dict[str, float])."
    )

    response = app_settings.get_llm().invoke(prompt)
    raw_text = str(response.content).strip()

    # Strip markdown fences if present
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        parsed = json.loads(raw_text)
        result = EvalResult(**parsed)
    except Exception:
        # ← FIXED: don't default to 8.0 — use 5.0 so retry fires
        result = EvalResult(
            score=5.0,
            verdict="Parse error — defaulting to retry",
            suggestions=["Ensure stronger keyword alignment with the job description"],
            criteria={"parse_error": 1.0},
        )

    state["evaluation"] = result.model_dump(mode="json")
    state["needs_retry"] = result.score < 7.0
    state["judge_feedback"] = result.suggestions   # ← NEW: pass suggestions downstream
    return state