import json
import os
from typing import Dict, List, Any


def generate_deterministic_feedback(
    question: str,
    expected_answer: str,
    candidate_answer: str,
    similarity_score: float,
    keyword_score: float,
    matched_keywords: List[str],
    missing_keywords: List[str]
) -> Dict[str, Any]:
    """
    Generates intelligent deterministic feedback when OpenAI API is not configured or unavailable.
    Guarantees 100% offline functionality without crashing.
    """
    strengths = []
    weaknesses = []
    suggestions = []

    if not candidate_answer.strip():
        return {
            "strengths": ["No answer provided."],
            "weaknesses": ["The response was left blank. No credit could be awarded."],
            "suggestions": ["Attempt every interview question by identifying the core topic and sharing any relevant principles you know."],
            "improved_answer": expected_answer,
            "provider": "deterministic"
        }

    # Analyze strengths
    if similarity_score >= 70:
        strengths.append(f"Strong semantic alignment ({similarity_score:.1f}%) with the expected answer.")
    elif similarity_score >= 40:
        strengths.append(f"Demonstrated foundational understanding with moderate semantic similarity ({similarity_score:.1f}%).")
    else:
        strengths.append("Provided an initial response attempting to address the topic.")

    if matched_keywords:
        sample_matched = ", ".join(f"'{k}'" for k in matched_keywords[:4])
        strengths.append(f"Accurately incorporated key technical terminology: {sample_matched}.")

    # Analyze weaknesses
    if missing_keywords:
        sample_missing = ", ".join(f"'{k}'" for k in missing_keywords[:4])
        weaknesses.append(f"Omitted crucial concept terms: {sample_missing}.")
    if similarity_score < 50:
        weaknesses.append("Response lacked sufficient technical depth or diverged from the core expected principles.")
    if len(candidate_answer.split()) < 15:
        weaknesses.append("The response was relatively concise and could benefit from further architectural elaboration or examples.")

    # Generate actionable suggestions
    if missing_keywords:
        suggestions.append(f"Structure your response around core mechanisms like {missing_keywords[0]} to substantiate your explanation.")
    suggestions.append("Follow the STAR or Concept-Mechanism-Impact framework to structure your answer logically.")
    if len(candidate_answer.split()) < 25:
        suggestions.append("Provide a concrete production use case or trade-off to demonstrate hands-on experience.")

    return {
        "strengths": strengths if strengths else ["Response demonstrates an initial understanding of the question."],
        "weaknesses": weaknesses if weaknesses else ["Minor nuances could be further polished."],
        "suggestions": suggestions,
        "improved_answer": expected_answer,
        "provider": "deterministic"
    }


def get_ai_feedback(
    question: str,
    expected_answer: str,
    candidate_answer: str,
    similarity_score: float,
    keyword_score: float,
    matched_keywords: List[str],
    missing_keywords: List[str]
) -> Dict[str, Any]:
    """
    Calls OpenAI API if OPENAI_API_KEY is configured to generate qualitative feedback.
    Falls back gracefully to deterministic feedback on any error or missing key.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your-openai-api-key":
        return generate_deterministic_feedback(
            question, expected_answer, candidate_answer,
            similarity_score, keyword_score, matched_keywords, missing_keywords
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""
You are an expert technical interviewer evaluating a student candidate's response.
Do NOT generate a numeric score. The deterministic scoring system has already evaluated the numbers.
Provide qualitative feedback strictly as valid JSON with keys:
- "strengths": list of 1-3 concise strings
- "weaknesses": list of 1-3 concise strings
- "suggestions": list of 1-3 actionable advice strings
- "improved_answer": a concise, exemplary model answer

Question: {question}
Expected Answer: {expected_answer}
Candidate's Answer: {candidate_answer}
Deterministic Similarity: {similarity_score}%
Deterministic Keyword Match: {keyword_score}%
Matched Keywords: {', '.join(matched_keywords)}
Missing Keywords: {', '.join(missing_keywords)}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional hiring manager giving constructive, encouraging interview feedback in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        data["provider"] = "openai"
        return data
    except Exception as e:
        # Graceful fallback to deterministic engine
        feedback = generate_deterministic_feedback(
            question, expected_answer, candidate_answer,
            similarity_score, keyword_score, matched_keywords, missing_keywords
        )
        feedback["fallback_reason"] = str(e)
        return feedback
