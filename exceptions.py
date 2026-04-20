"""Custom exception hierarchy for the job search agent."""

from __future__ import annotations


class JobSearchAgentError(Exception):
    """Base application exception for predictable failures."""


class ConfigurationError(JobSearchAgentError):
    """Raised when required configuration is missing or invalid."""


class ToolExecutionError(JobSearchAgentError):
    """Raised when an external tool integration fails."""


class ValidationError(JobSearchAgentError):
    """Raised when model validation fails in business workflows."""
