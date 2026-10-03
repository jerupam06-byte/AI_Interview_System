import pytest
from services.similarity import compute_tfidf_similarity, normalize_text
from services.keyword_matcher import match_keywords
from services.scoring import calculate_weighted_score
from services.evaluator import evaluate_candidate_answer


def test_text_normalization():
    """Verify text is lowered, punctuation stripped, and whitespace collapsed."""
    raw = "  Hello, World!!   This IS Python-3.  "
    norm = normalize_text(raw)
    assert norm == "hello world this is python 3"


def test_empty_answer_scoring():
    """Empty answer must strictly return 0 across all scoring dimensions."""
    res = evaluate_candidate_answer(
        question_text="What is the GIL?",
        expected_answer="The Global Interpreter Lock is a mutex in CPython.",
        candidate_answer="",
        keywords=["gil", "mutex", "cpython"]
    )
    assert res["final_question_score"] == 0.0
    assert res["similarity_score"] == 0.0
    assert res["keyword_score"] == 0.0


def test_whitespace_answer_scoring():
    """Whitespace-only answers must receive 0."""
    res = evaluate_candidate_answer(
        question_text="What is a decorator?",
        expected_answer="A decorator wraps a function.",
        candidate_answer="    \n\t   ",
        keywords=["decorator", "function"]
    )
    assert res["final_question_score"] == 0.0


def test_tfidf_cosine_similarity():
    """Cosine similarity of identical text should approach 100%."""
    text = "The Global Interpreter Lock is a mutex in CPython that protects memory management."
    score = compute_tfidf_similarity(text, text)
    assert score >= 98.0

    # Orthogonal / completely different text should have very low or 0 score
    diff = compute_tfidf_similarity("apples oranges bananas", "quantum physics gravitational relativity")
    assert diff == 0.0


def test_multi_word_keyword_matching():
    """Verifies that multi-word phrases and single keywords are matched accurately."""
    candidate = "I understand that the global interpreter lock in cpython prevents true multi-threading."
    expected_kws = ["global interpreter lock", "cpython", "multi-threading", "garbage collection"]
    
    score, matched, missing = match_keywords(candidate, expected_kws)
    assert "global interpreter lock" in matched
    assert "cpython" in matched
    assert "multi-threading" in matched
    assert "garbage collection" in missing
    assert score == 75.0


def test_weighted_scoring_formula():
    """Tests the 60% similarity + 20% keywords + 10% completeness + 10% sanity formula."""
    scores = calculate_weighted_score(
        similarity_score=80.0,
        keyword_score=100.0,
        candidate_answer="The Global Interpreter Lock is a mutex in CPython because it synchronizes bytecode execution. For example, it prevents race conditions.",
        expected_answer="The Global Interpreter Lock is a mutex in CPython that synchronizes execution."
    )
    # 0.60*80 = 48
    # 0.20*100 = 20
    # completeness >= 70 => >= 7.0
    # length >= 80 => >= 8.0
    # Total ~ 83+
    assert scores["final_score"] >= 80.0
    assert scores["final_score"] <= 100.0
