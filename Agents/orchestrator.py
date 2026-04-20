"""LangGraph orchestration graph for all job search agents."""

from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from Agents.email_writer_agent import run_email_writer_agent
from Agents.evaluator_agent import run_evaluator_agent
from Agents.interview_prep_agent import run_interview_prep_agent
from Agents.job_scraper_agent import run_job_scraper_agent
from Agents.resume_tailor_agent import run_resume_tailor_agent


class AgentState(TypedDict, total=False):
    """State container passed through every graph node."""

    task: Literal["job_search", "tailor_resume", "write_email", "interview_prep"]
    retry_count: int
    max_retries: int
    needs_retry: bool
    evaluation_target: Literal["resume", "email"]

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


def _route_resume_to_eval(_: AgentState) -> str:
    return "evaluator"


def _route_email_to_eval(_: AgentState) -> str:
    return "evaluator"


def _route_after_evaluation(state: AgentState) -> str:
    if not state.get("needs_retry", False):
        return END

    retry_count = int(state.get("retry_count", 0)) + 1
    state["retry_count"] = retry_count
    max_retries = int(state.get("max_retries", 2))

    if retry_count > max_retries:
        return END

    if state.get("evaluation_target") == "email":
        return "email_writer"
    return "resume_tailor"


def build_graph():
    """Construct and compile the LangGraph state machine."""

    graph = StateGraph(AgentState)

    graph.add_node("job_scraper", run_job_scraper_agent)
    graph.add_node("resume_tailor", run_resume_tailor_agent)
    graph.add_node("email_writer", run_email_writer_agent)
    graph.add_node("interview_prep_agent", run_interview_prep_agent)
    graph.add_node("evaluator", run_evaluator_agent)

    graph.add_conditional_edges(START, _route_from_start)

    graph.add_edge("job_scraper", END)
    graph.add_conditional_edges("resume_tailor", _route_resume_to_eval)
    graph.add_conditional_edges("email_writer", _route_email_to_eval)
    graph.add_edge("interview_prep_agent", END)

    graph.add_conditional_edges("evaluator", _route_after_evaluation)

    return graph.compile()


def run_orchestrator(initial_state: AgentState) -> AgentState:
    """Execute the workflow graph and return final state."""

    app = build_graph()
    return app.invoke(initial_state)
