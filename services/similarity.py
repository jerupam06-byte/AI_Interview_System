import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text: str) -> str:
    """
    Normalizes input text by converting to lowercase, removing punctuation,
    and collapsing extraneous whitespace.
    """
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    # Replace punctuation with spaces to prevent concatenating words
    for punct in string.punctuation:
        text = text.replace(punct, " ")
    # Normalize whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_tfidf_similarity(expected_answer: str, candidate_answer: str) -> float:
    """
    Calculates the cosine similarity between expected and candidate answers
    using TF-IDF vectorization with unigram and bigram features.
    
    Returns:
        float: Similarity percentage between 0.0 and 100.0.
    """
    norm_expected = normalize_text(expected_answer)
    norm_candidate = normalize_text(candidate_answer)

    # Empty answer check
    if not norm_candidate or not norm_expected:
        return 0.0

    # Ensure there are meaningful words
    if len(norm_candidate.split()) < 1:
        return 0.0

    try:
        # Use unigrams and bigrams with English stop-words
        # If text is too short or only stop words, fallback to no stop words
        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([norm_expected, norm_candidate])
        except ValueError:
            # Fallback if empty vocabulary after stop words
            vectorizer = TfidfVectorizer(ngram_range=(1, 1))
            tfidf_matrix = vectorizer.fit_transform([norm_expected, norm_candidate])

        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity_matrix[0][0]) * 100.0
        
        # Clamp between 0.0 and 100.0
        return max(0.0, min(100.0, round(score, 2)))
    except Exception:
        return 0.0
