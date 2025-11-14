KEYWORD_PROMPT="""
You are an expert in academic information retrieval. Extract 7–15 single-word academic keywords suitable for searching scientific databases (arXiv, IEEE, ACL).

Rules:

- Single words only.
- Academic, domain-specific terms only (tasks, algorithms, architectures, datasets, phenomena).
- Exclude broad or high-frequency terms (e.g., learning, inference, neural, optimization, classification, system, model, method).
- No generic research words (e.g., study, analysis, results, approach).
- No overlapping or substring-related keywords.
- Each keyword must significantly narrow the search space — prefer specific technical terminology used mainly within a subfield.

Output only a JSON list: ["keyword1", ...].
"""