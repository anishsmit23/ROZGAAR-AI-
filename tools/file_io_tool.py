"""File IO helper functions with safe defaults."""

from __future__ import annotations

from pathlib import Path


def read_text(file_path: Path) -> str:
    """Read UTF-8 text file content."""

    return file_path.read_text(encoding="utf-8")


def write_text(file_path: Path, content: str) -> Path:
    """Write UTF-8 text file content, creating parent folders if needed."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path
