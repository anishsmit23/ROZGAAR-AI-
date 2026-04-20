"""Local launcher for FastAPI and Streamlit processes."""

from __future__ import annotations

import os
import subprocess
import sys
from multiprocessing import Process

from config.settings import get_settings


def run_fastapi() -> None:
    """Run FastAPI backend with Uvicorn."""

    settings = get_settings()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            settings.fastapi_host,
            "--port",
            str(settings.fastapi_port),
            "--reload",
        ],
        check=False,
    )


def run_streamlit() -> None:
    """Run Streamlit dashboard on configured port."""

    settings = get_settings()
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = str(settings.streamlit_port)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"], env=env, check=False)


if __name__ == "__main__":
    api_process = Process(target=run_fastapi)
    app_process = Process(target=run_streamlit)

    api_process.start()
    app_process.start()

    api_process.join()
    app_process.join()
