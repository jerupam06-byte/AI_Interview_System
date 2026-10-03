import os
from typing import Dict, Any


def get_deterministic_chat_reply(message: str) -> str:
    """
    Intelligent domain-specific responses for interview prep when OpenAI API key is unavailable.
    """
    msg = message.lower()
    if "python" in msg or "gil" in msg or "decorator" in msg:
        return (
            "**Python Interview Tip:** In technical interviews, interviewers love questions on the GIL, "
            "mutable vs immutable objects, and decorators. When explaining decorators, emphasize that they are "
            "higher-order functions using closures, taking advantage of first-class functions in Python."
        )
    elif "sql" in msg or "query" in msg or "database" in msg:
        return (
            "**SQL Interview Tip:** Always be ready to distinguish `WHERE` (row filtering before aggregation) "
            "from `HAVING` (group filtering after aggregation). Also, master Window Functions like `ROW_NUMBER()`, "
            "`RANK()`, and `DENSE_RANK()`, as they frequently appear in coding assessments."
        )
    elif "ml" in msg or "machine learning" in msg or "overfitting" in msg or "bias" in msg:
        return (
            "**ML Interview Tip:** When discussing the Bias-Variance tradeoff, clearly define High Bias as underfitting "
            "(model too simple) and High Variance as overfitting (model learning noise). Mention mitigation strategies: "
            "regularization (L1/L2), cross-validation, and pruning."
        )
    elif "nlp" in msg or "tfidf" in msg or "transformer" in msg:
        return (
            "**NLP Interview Tip:** For classical NLP, explain how TF-IDF balances term frequency with document infrequency. "
            "For deep learning, be prepared to draw the Transformer Multi-Head Self-Attention equation: "
            "`Softmax((Q * K^T) / sqrt(d_k)) * V`."
        )
    elif "hr" in msg or "behavioral" in msg or "tell me about yourself" in msg:
        return (
            "**Behavioral Interview Strategy:** Use the **STAR Framework** (Situation, Task, Action, Result). "
            "Allocate 70% of your response to the **Action** (what you specifically did) and the **Result** (measurable outcomes, metrics, or lessons learned)."
        )
    else:
        return (
            "**Interview Preparation Assistant:** I'm here to help you practice Python, SQL, Machine Learning, Data Analytics, "
            "DSA, and behavioral questions. Try asking: *'How do I answer questions about Python memory management?'* or "
            "*'What are key SQL topics asked in Data Analyst interviews?'*"
        )


def generate_chat_response(message: str, user_id: int = None) -> str:
    """
    Processes a user query for the AI interview assistant.
    Uses OpenAI if available; falls back to deterministic guidance.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your-openai-api-key":
        return get_deterministic_chat_reply(message)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        system_prompt = (
            "You are an elite AI Technical Interview Coach assisting students and freshers preparing for MCA / BTech campus placements. "
            "You specialize in Python, SQL, Machine Learning, NLP, Data Analytics, DSA, and HR behavioral questions. "
            "Provide concise, encouraging, structured, and technically accurate explanations. "
            "Use Markdown bullet points and code snippets where helpful."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"{get_deterministic_chat_reply(message)}\n\n*(Note: Running offline mode. Live OpenAI status: {str(e)})*"
