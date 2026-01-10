"""Enumerations shared across database models."""

from enum import Enum


class PaperSource(Enum):
    """Supported sources for fetching papers."""

    ARXIV = "ARXIV"


class PaperType(Enum):
    """High-level classifications for scholarly papers."""

    JOURNAL = "JOURNAL"
    CONFERENCE = "CONFERENCE"
    PREPRINT = "PREPRINT"
    WORKSHOP = "WORKSHOP"
    THESIS = "THESIS"
    OTHER = "OTHER"


class PaperContentStatus(Enum):
    """Lifecycle status of paper content parsing and storage."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"