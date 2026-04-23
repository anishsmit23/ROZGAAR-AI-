"""Agent-level smoke tests."""

from __future__ import annotations

from Agents.orchestrator import run_orchestrator


def test_orchestrator_interview_prep_smoke(monkeypatch):
    """Ensure orchestrator can execute interview prep path."""

    class FakeLLM:
        def invoke(self, _: str):
            class Resp:
                content = "Q1: Example?\nA1: Example answer."

            return Resp()

    monkeypatch.setattr("config.settings.get_llm", lambda: FakeLLM())

    class FakeVectorStore:
        def __init__(self, *args, **kwargs): pass
        def search_jobs(self, *args, **kwargs): return []
        def add_application(self, *args, **kwargs): pass
    
    monkeypatch.setattr("Agents.interview_prep_agent.VectorStore", FakeVectorStore)

    result = run_orchestrator(
        {
            "task": "interview_prep",
            "company": "Acme",
            "role": "ML Engineer",
            "job_description": "Build and deploy models",
        }
    )
    assert "interview_prep" in result
