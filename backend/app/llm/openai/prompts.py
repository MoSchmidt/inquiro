KEYWORD_PROMPT = """
You are an expert in academic information retrieval. Extract 5 short search queries suitable for
searching scientific databases (arXiv, IEEE, ACL).
Rules:
- Short queries only.
- Academic, domain-specific terms only (tasks, algorithms, architectures, datasets, phenomena).
- No overlapping or substring-related keywords.
- Each sentence should be relevant to the overall query and narrow the search space - prefer
specific technical terminology used mainly within a subfield.
Output only a JSON list: ["keyword1", ...].
"""
