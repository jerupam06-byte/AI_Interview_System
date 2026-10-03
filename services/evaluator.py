from typing import Dict, Any, List
from .similarity import compute_tfidf_similarity
from .keyword_matcher import match_keywords
from .scoring import calculate_weighted_score
from .ai_feedback import get_ai_feedback


def evaluate_candidate_answer(
    question_text: str,
    expected_answer: str,
    candidate_answer: str,
    keywords: List[str]
) -> Dict[str, Any]:
    """
    Main evaluation pipeline:
    1. TF-IDF vectorization and cosine similarity calculation.
    2. Boundary-aware keyword matching and coverage calculation.
    3. Transparent 4-factor weighted score calculation (60/20/10/10).
    4. AI-assisted / deterministic feedback generation.
    
    Returns comprehensive evaluation details:
        - similarity_score (float)
        - keyword_score (float)
        - completeness_score (float)
        - length_score (float)
        - final_score (float, 0-100)
        - matched_keywords (list)
        - missing_keywords (list)
        - feedback (dict: strengths, weaknesses, suggestions, improved_answer)
    """
    # Step 1: TF-IDF Cosine Similarity
    similarity = compute_tfidf_similarity(expected_answer, candidate_answer)

    # Step 2: Keyword matching
    keyword_score, matched_kws, missing_kws = match_keywords(candidate_answer, keywords)

    # Step 3: Transparent Weighted Scoring
    scores = calculate_weighted_score(
        similarity_score=similarity,
        keyword_score=keyword_score,
        candidate_answer=candidate_answer,
        expected_answer=expected_answer
    )

    # Step 4: Feedback generation
    feedback_data = get_ai_feedback(
        question=question_text,
        expected_answer=expected_answer,
        candidate_answer=candidate_answer,
        similarity_score=scores["similarity_score"],
        keyword_score=scores["keyword_score"],
        matched_keywords=matched_kws,
        missing_keywords=missing_kws
    )

    # Add score breakdown to feedback
    feedback_data["score_breakdown"] = {
        "similarity_weight": "60%",
        "similarity_score": scores["similarity_score"],
        "keyword_weight": "20%",
        "keyword_score": scores["keyword_score"],
        "completeness_weight": "10%",
        "completeness_score": scores["completeness_score"],
        "length_sanity_weight": "10%",
        "length_score": scores["length_score"],
        "final_score": scores["final_score"]
    }

    return {
        "similarity_score": scores["similarity_score"],
        "keyword_score": scores["keyword_score"],
        "completeness_score": scores["completeness_score"],
        "length_score": scores["length_score"],
        "final_question_score": scores["final_score"],
        "matched_keywords": matched_kws,
        "missing_keywords": missing_kws,
        "feedback": feedback_data
    }
