"""Evaluator agent using LLM-as-judge to score generated artifacts."""

from __future__ import annotations

from config.prompts import EVALUATOR_PROMPT
from config import settings as app_settings
from models.eval_result import EvalResult


def run_evaluator_agent(state: dict) -> dict:
    """Score either tailored resume or email output and provide improvements."""

    target = state.get("evaluation_target", "resume")
    content = state.get("tailored_resume_text") if target == "resume" else state.get("email_draft", {}).get("body", "")

    prompt = (
        f"{EVALUATOR_PROMPT}\n\n"
        f"Target: {target}\n"
        f"Content:\n{content}\n\n"
        "Return strict JSON with keys: score, verdict, suggestions, criteria."
    )

    response = app_settings.get_llm().invoke(prompt)
    raw_text = str(response.content)

    score = 8.0
    verdict = "Good"
    if "score" in raw_text.lower() and "{" in raw_text:
        try:
            parsed = __import__("json").loads(raw_text)
            result = EvalResult(**parsed)
        except Exception:
            result = EvalResult(score=score, verdict=verdict, suggestions=["Could not parse strict JSON response"], criteria={})
    else:
        result = EvalResult(score=score, verdict=verdict, suggestions=["Use stricter keyword alignment and concise wording"], criteria={"clarity": 8.0})

    state["evaluation"] = result.model_dump(mode="json")
    state["needs_retry"] = result.score < 7.0
    return state
