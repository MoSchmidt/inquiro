from enum import Enum

class PaperSource(Enum):
    ARXIV = "ARXIV"

class PaperType(Enum):
    JOURNAL = "JOURNAL"
    CONFERENCE = "CONFERENCE"
    PREPRINT = "PREPRINT"
    WORKSHOP = "WORKSHOP"
    THESIS = "THESIS"
    OTHER = "OTHER"
