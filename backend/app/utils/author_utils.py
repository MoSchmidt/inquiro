"""Utility helpers for working with author metadata."""

from typing import List, Any


def normalize_authors(authors: Any) -> List[str]:
    """
    Normalize author representations from either:
    - dict mapping → ["name1", "name2", ...]
    - list of lists/tuples → [["last", "first", "middle", ...], ...]

    Always returns a flat List[str].
    """

    # Case 1: dict | None → convert safely to list of values
    if isinstance(authors, dict):
        return [str(name) for name in authors.values() if name]

    if authors is None:
        return []

    # Case 2: invalid type → return empty list
    if not isinstance(authors, list):
        return []

    formatted: List[str] = []

    for item in authors:
        if isinstance(item, (list, tuple)) and item:
            last = item[0] or ""
            first = item[1] if len(item) > 1 else ""
            middle = item[2] if len(item) > 2 else ""

            name = " ".join(part for part in [first, middle, last] if part).strip()

            if name:
                formatted.append(name)

    return formatted
