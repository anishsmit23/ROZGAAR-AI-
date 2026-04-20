"""Tool-level unit tests."""

from __future__ import annotations

from pathlib import Path

from tools.file_io_tool import read_text, write_text


def test_file_io_round_trip(tmp_path: Path):
    """Verify text write and read helpers are symmetric."""

    path = tmp_path / "sample.txt"
    write_text(path, "hello")
    assert read_text(path) == "hello"
