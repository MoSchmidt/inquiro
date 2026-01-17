"""Metrics for evaluating keyword extraction accuracy."""

from typing import Dict, List, Set


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


def calculate_precision(extracted: List[str], ground_truth: List[str]) -> float:
    """
    Calculate precision: proportion of extracted keywords that are correct.

    Precision = |extracted ∩ ground_truth| / |extracted|

    Args:
        extracted: List of extracted keywords
        ground_truth: List of ground truth keywords

    Returns:
        Precision score between 0.0 and 1.0
    """
    extracted_set = normalize_keywords(extracted)
    ground_truth_set = normalize_keywords(ground_truth)

    if not extracted_set:
        return 0.0  # No extracted keywords means precision is 0

    intersection = len(extracted_set & ground_truth_set)
    return intersection / len(extracted_set)


def calculate_recall(extracted: List[str], ground_truth: List[str]) -> float:
    """
    Calculate recall: proportion of ground truth keywords that were extracted.

    Recall = |extracted ∩ ground_truth| / |ground_truth|

    Args:
        extracted: List of extracted keywords
        ground_truth: List of ground truth keywords

    Returns:
        Recall score between 0.0 and 1.0
    """
    extracted_set = normalize_keywords(extracted)
    ground_truth_set = normalize_keywords(ground_truth)

    if not ground_truth_set:
        # If no ground truth, recall is undefined, but we'll return 1.0 if nothing extracted
        return 1.0 if not extracted_set else 0.0

    intersection = len(extracted_set & ground_truth_set)
    return intersection / len(ground_truth_set)


def calculate_f1_score(extracted: List[str], ground_truth: List[str]) -> float:
    """
    Calculate F1 score: harmonic mean of precision and recall.

    F1 = 2 * (precision * recall) / (precision + recall)

    Args:
        extracted: List of extracted keywords
        ground_truth: List of ground truth keywords

    Returns:
        F1 score between 0.0 and 1.0
    """
    precision = calculate_precision(extracted, ground_truth)
    recall = calculate_recall(extracted, ground_truth)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)


def calculate_all_metrics(extracted: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """
    Calculate all metrics (Jaccard, Precision, Recall, F1) at once.

    Args:
        extracted: List of extracted keywords
        ground_truth: List of ground truth keywords

    Returns:
        Dictionary containing all metric scores
    """
    return {
        "jaccard": calculate_keyword_jaccard(extracted, ground_truth),
        "precision": calculate_precision(extracted, ground_truth),
        "recall": calculate_recall(extracted, ground_truth),
        "f1": calculate_f1_score(extracted, ground_truth),
    }
