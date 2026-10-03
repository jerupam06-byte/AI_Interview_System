import re
from typing import List, Tuple
from .similarity import normalize_text


def match_keywords(candidate_answer: str, expected_keywords: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Evaluates keyword coverage in the candidate answer.
    Supports single-word and multi-word keywords with boundary-aware matching.
    
    Returns:
        tuple: (keyword_score: float [0-100], matched_keywords: list, missing_keywords: list)
    """
    if not candidate_answer or not expected_keywords:
        return 0.0, [], expected_keywords or []

    normalized_candidate = normalize_text(candidate_answer)
    if not normalized_candidate:
        return 0.0, [], expected_keywords

    matched = []
    missing = []

    for kw in expected_keywords:
        norm_kw = normalize_text(kw)
        if not norm_kw:
            continue
            
        # Pattern matching for word boundaries
        # Handles hyphenated or spaced terms accurately
        pattern = r"\b" + re.escape(norm_kw) + r"\b"
        if re.search(pattern, normalized_candidate):
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(expected_keywords)
    if total == 0:
        score = 100.0
    else:
        score = round((len(matched) / total) * 100.0, 2)

    return min(100.0, max(0.0, score)), matched, missing
