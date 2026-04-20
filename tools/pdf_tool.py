"""PDF helpers for parsing source resume and generating tailored versions."""

from __future__ import annotations

from pathlib import Path

import fitz
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def extract_pdf_text(file_path: Path) -> str:
    """Extract concatenated text from all pages in a PDF."""

    with fitz.open(file_path) as document:
        return "\n".join(page.get_text("text") for page in document)


def generate_resume_pdf(output_path: Path, title: str, lines: list[str]) -> Path:
    """Create a clean single-column resume PDF from text lines."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=LETTER)
    width, height = LETTER

    y = height - 72
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(72, y, title)
    y -= 28

    pdf.setFont("Helvetica", 11)
    for line in lines:
        if y < 72:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - 72
        pdf.drawString(72, y, line[:120])
        y -= 16

    pdf.save()
    return output_path
