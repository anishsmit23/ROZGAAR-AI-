# Autonomous AI Job Search Agent


UNDER CONSTRUCTION 🚧 

Production-minded scaffold for a multi-agent job search system using LangGraph, FastAPI, Streamlit, ChromaDB, and SQLite.

## Features

- Agent orchestration with LangGraph
- Job scraping pipeline with semantic memory + relational tracker
- Resume tailoring and email writing agents with evaluator retry loop
- FastAPI backend routes for each workflow
- Streamlit dashboard pages for day-to-day usage

## Quick Start

1. Create and activate a Python 3.11+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

4. Run both backend and dashboard:

```bash
python main.py
```

- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501

## API Endpoints

- `GET /health`
- `GET /jobs`
- `POST /search`
- `POST /tailor-resume`
- `POST /generate-email`
- `POST /interview-prep`

## Notes

- Agents are synchronous pure functions that mutate and return state.
- All prompts are centralized in `config/prompts.py`.
- External integrations are isolated under `tools/`.
- Memory backends are isolated under `memory/`.
