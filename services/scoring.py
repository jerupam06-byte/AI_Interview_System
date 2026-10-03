import re
from typing import Dict


def calculate_completeness_score(candidate_answer: str) -> float:
    """
    Evaluates the structural coherence and articulation of the answer,
    looking at sentence boundaries and explanatory connector words.
    """
    text = candidate_answer.strip()
    if not text:
        return 0.0

    words = text.split()
    if len(words) < 5:
        return 20.0

    score = 40.0

    # Checks for multiple sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 3]
    if len(sentences) >= 2:
        score += 25.0
    elif len(sentences) == 1 and len(words) >= 15:
        score += 15.0

    # Checks for logical connector keywords commonly used in good interview answers
    connectors = [
        "because", "such as", "for example", "therefore", "in contrast",
        "furthermore", "however", "additionally", "which means", "firstly",
        "secondly", "to optimize", "in order to", "as a result"
    ]
    lower_text = text.lower()
    found_connectors = sum(1 for c in connectors if c in lower_text)
    if found_connectors >= 2:
        score += 35.0
    elif found_connectors == 1:
        score += 20.0

    return min(100.0, max(0.0, float(score)))


def calculate_length_sanity_score(candidate_answer: str, expected_answer: str) -> float:
    """
    Assesses answer length and depth against the expected baseline answer.
    Penalizes overly terse or unelaborated responses.
    """
    cand_words = len(candidate_answer.strip().split())
    exp_words = max(1, len(expected_answer.strip().split()))

    if cand_words == 0:
        return 0.0
    if cand_words < 4:
        return 10.0
    if cand_words < 10:
        return 40.0

    # Ratio of candidate answer length compared to expected
    ratio = cand_words / exp_words
    if ratio >= 0.6:
        return 100.0
    elif ratio >= 0.4:
        return 80.0
    elif ratio >= 0.25:
        return 65.0
    else:
        return 50.0


def calculate_weighted_score(
    similarity_score: float,
    keyword_score: float,
    candidate_answer: str,
    expected_answer: str
) -> Dict[str, float]:
    """
    Computes final transparent weighted scoring per Section 10 specification:
      - Similarity score: 60%
      - Keyword coverage: 20%
      - Answer completeness/structure: 10%
      - Answer length/relevance sanity check: 10%
      
    Returns a dictionary of all score components and final weighted score clamped to 0-100.
    """
    if not candidate_answer or not candidate_answer.strip():
        return {
            "similarity_score": 0.0,
            "keyword_score": 0.0,
            "completeness_score": 0.0,
            "length_score": 0.0,
            "final_score": 0.0,
        }

    # Extremely short answers (< 3 words) cannot receive inflated scores
    words = candidate_answer.strip().split()
    if len(words) < 3:
        similarity_score = min(similarity_score, 15.0)
        keyword_score = min(keyword_score, 20.0)

    completeness_score = calculate_completeness_score(candidate_answer)
    length_score = calculate_length_sanity_score(candidate_answer, expected_answer)

    # Weighted calculation
    weighted = (
        (0.60 * similarity_score)
        + (0.20 * keyword_score)
        + (0.10 * completeness_score)
        + (0.10 * length_score)
    )

    final_clamped = round(min(100.0, max(0.0, weighted)), 1)

    return {
        "similarity_score": round(similarity_score, 1),
        "keyword_score": round(keyword_score, 1),
        "completeness_score": round(completeness_score, 1),
        "length_score": round(length_score, 1),
        "final_score": final_clamped,
    }
