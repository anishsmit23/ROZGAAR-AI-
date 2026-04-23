"""LangGraph orchestration graph for all job search agents."""

from __future__ import annotations

import uuid
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from Agents.email_writer_agent import run_email_writer_agent
from Agents.evaluator_agent import run_evaluator_agent
from Agents.interview_prep_agent import run_interview_prep_agent
from Agents.job_scraper_agent import run_job_scraper_agent
from Agents.resume_tailor_agent import run_resume_tailor_agent


class AgentState(TypedDict, total=False):
    task: Literal["job_search", "tailor_resume", "write_email", "interview_prep"]
    retry_count: int
    max_retries: int
    needs_retry: bool
    evaluation_target: Literal["resume", "email"]
    judge_feedback: list[str]          # ← NEW: carries suggestions from judge back to tailor

    job_search: dict
    jobs: list[dict]

    base_resume: str
    job_description: str
    tailored_resume_text: str
    tailored_resume_txt_path: str
    tailored_resume_pdf_path: str

    company: str
    role: str
    to_email: str
    candidate_background: str
    email_draft: dict
    email_output_path: str

    interview_prep: str
    interview_prep_path: str

    evaluation: dict


def _route_from_start(state: AgentState) -> str:
    task = state.get("task", "job_search")
    if task == "tailor_resume":
        return "resume_tailor"
    if task == "write_email":
        return "email_writer"
    if task == "interview_prep":
        return "interview_prep_agent"
    return "job_scraper"


def _route_after_evaluation(state: AgentState) -> str:
    """Pure routing — reads state only, never mutates it."""
    if not state.get("needs_retry", False):
        return END

    retry_count = int(state.get("retry_count", 0))
    max_retries = int(state.get("max_retries", 2))

    if retry_count >= max_retries:
        return END

    return "increment_retry"


# ← NEW: separate node that increments retry_count (routing functions can't mutate state)
def _increment_retry(state: AgentState) -> dict:
    return {"retry_count": int(state.get("retry_count", 0)) + 1}


def _route_from_increment_retry(state: AgentState) -> str:
    if state.get("evaluation_target") == "email":
        return "email_writer"
    return "resume_tailor"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("job_scraper", run_job_scraper_agent)
    graph.add_node("resume_tailor", run_resume_tailor_agent)
    graph.add_node("email_writer", run_email_writer_agent)
    graph.add_node("interview_prep_agent", run_interview_prep_agent)
    graph.add_node("evaluator", run_evaluator_agent)
    graph.add_node("increment_retry", _increment_retry)   # ← NEW node

    graph.add_conditional_edges(START, _route_from_start)

    graph.add_edge("job_scraper", END)
    graph.add_edge("resume_tailor", "evaluator")
    graph.add_edge("email_writer", "evaluator")
    graph.add_edge("interview_prep_agent", END)

    graph.add_conditional_edges("evaluator", _route_after_evaluation)
    # When routing back to tailor/email, go through increment_retry first
    graph.add_conditional_edges("increment_retry", _route_from_increment_retry)

    return graph


# Compile once at module load — not on every request
def _get_compiled_graph():
    from config.settings import get_settings
    settings = get_settings()
    db_path = settings.db_path.parent / "langgraph_checkpoints.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return build_graph().compile(checkpointer=checkpointer)

_COMPILED_GRAPH = _get_compiled_graph()


def run_orchestrator(initial_state: AgentState, thread_id: str = None) -> AgentState:
    config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
    return _COMPILED_GRAPH.invoke(initial_state, config=config)