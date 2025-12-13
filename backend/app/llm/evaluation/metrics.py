"""Metrics for evaluating keyword extraction accuracy."""

from typing import List, Set


def normalize_keywords(keywords: List[str]) -> Set[str]:
    """
    Normalize keywords for comparison: lowercase and strip whitespace.

    Args:
        keywords: List of keyword strings

    Returns:
        Set of normalized keyword strings
    """
    normalized = set()
    for keyword in keywords:
        if not keyword or not keyword.strip():
            continue
        # Lowercase and strip
        kw_clean = keyword.lower().strip()
        # Also add individual words from multi-word keywords for partial matching
        # This helps when extracted keywords are phrases containing ground truth keywords
        words = kw_clean.split()
        normalized.add(kw_clean)  # Add the full phrase
        # Add individual significant words (length > 2) for partial matching
        for word in words:
            if len(word) > 2:
                normalized.add(word)
    return normalized


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.

    Jaccard similarity = |A ∩ B| / |A ∪ B|

    Args:
        set1: First set of strings
        set2: Second set of strings

    Returns:
        Jaccard similarity score between 0.0 and 1.0
    """
    if not set1 and not set2:
        return 1.0  # Both empty sets are considered identical

    if not set1 or not set2:
        return 0.0  # One empty, one non-empty

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    if union == 0:
        return 1.0

    return intersection / union


def calculate_keyword_jaccard(extracted: List[str], ground_truth: List[str]) -> float:
    """
    Calculate Jaccard similarity between extracted and ground truth keywords.

    Args:
        extracted: List of extracted keywords
        ground_truth: List of ground truth keywords

    Returns:
        Jaccard similarity score between 0.0 and 1.0
    """
    extracted_set = normalize_keywords(extracted)
    ground_truth_set = normalize_keywords(ground_truth)

    return jaccard_similarity(extracted_set, ground_truth_set)
