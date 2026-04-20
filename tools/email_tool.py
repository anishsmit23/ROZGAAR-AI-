"""SMTP email utility for optional cold email delivery."""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from config.settings import get_settings
from exceptions import ToolExecutionError


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send plain text email through configured SMTP host."""

    settings = get_settings()
    if not settings.smtp_user or not settings.smtp_password:
        raise ToolExecutionError("SMTP_USER or SMTP_PASSWORD missing in .env")

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.smtp_user
    message["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.sendmail(settings.smtp_user, [to_email], message.as_string())
    except Exception as exc:
        raise ToolExecutionError(f"Failed to send email: {exc}") from exc
