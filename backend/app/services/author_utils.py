"""Utility helpers for working with author metadata."""

from typing import Any, Dict, Optional


def normalize_authors(authors: Any) -> Optional[Dict[str, str]]:
    """
    Normalize various author representations into a dict of index -> name.

    Expected input formats include:
    - dict already mapping indices/roles to names (returned as-is)
    - list of [last, first, middle] triplets such as
      [["Doe", "Jane", ""], ["Smith", "John", "A."]]
    """

    if isinstance(authors, dict):
        return authors

    if not isinstance(authors, list):
        return None

    formatted: list[str] = []
    for item in authors:
        if isinstance(item, (list, tuple)) and item:
            last = item[0] or ""
            first = item[1] if len(item) > 1 else ""
            middle = item[2] if len(item) > 2 else ""
            name = " ".join(part for part in [first, middle, last] if part)
            if name:
                formatted.append(name)

    if not formatted:
        return None

    return {str(idx): name for idx, name in enumerate(formatted)}


