import re
import io
from typing import Dict, Any, List
from pypdf import PdfReader


ROLE_SKILL_BENCHMARKS = {
    "Python Developer": [
        "python", "flask", "django", "fastapi", "sql", "postgresql", "sqlite",
        "git", "github", "docker", "rest api", "unit testing", "pytest",
        "multiprocessing", "threading", "oop", "data structures", "algorithms",
        "orm", "sqlalchemy", "redis", "linux", "aws"
    ],
    "AI/ML Engineer": [
        "python", "machine learning", "deep learning", "nlp", "scikit-learn",
        "tensorflow", "pytorch", "pandas", "numpy", "transformers", "hugging face",
        "computer vision", "feature engineering", "model deployment", "sql",
        "git", "data preprocessing", "statistics", "math", "docker"
    ],
    "Data Analyst": [
        "sql", "python", "pandas", "numpy", "excel", "power bi", "tableau",
        "statistics", "a/b testing", "data visualization", "eda", "data cleaning",
        "business intelligence", "dashboards", "reporting", "git", "etl"
    ]
}


def extract_text_from_pdf(pdf_stream_or_bytes) -> str:
    """
    Extracts plain text from PDF stream or bytes in memory without saving to disk.
    Safe for ephemeral environments like Vercel.
    """
    try:
        if isinstance(pdf_stream_or_bytes, bytes):
            reader = PdfReader(io.BytesIO(pdf_stream_or_bytes))
        else:
            reader = PdfReader(pdf_stream_or_bytes)

        text_parts = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)

        return "\n".join(text_parts).strip()
    except Exception as e:
        raise ValueError(f"Could not read PDF file: {str(e)}")


def analyze_resume_text(resume_text: str, target_role: str = "Python Developer") -> Dict[str, Any]:
    """
    Analyzes resume text against required skills for target role.
    Provides match score, detected skills, missing skills, and actionable recommendations.
    """
    if not resume_text:
        return {
            "match_score": 0.0,
            "detected_skills": [],
            "missing_skills": [],
            "suggestions": ["The uploaded PDF appears empty or contains scanned images without selectable text."],
            "extracted_length": 0
        }

    lower_text = resume_text.lower()
    benchmark_skills = ROLE_SKILL_BENCHMARKS.get(target_role, ROLE_SKILL_BENCHMARKS["Python Developer"])

    detected = []
    missing = []

    for skill in benchmark_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, lower_text):
            detected.append(skill)
        else:
            missing.append(skill)

    total_benchmarks = len(benchmark_skills)
    match_score = round((len(detected) / total_benchmarks) * 100.0, 1)

    suggestions = []
    if missing:
        top_missing = missing[:5]
        suggestions.append(f"Consider highlighting experience with key {target_role} competencies: {', '.join(top_missing)}.")

    # Check for metrics and action verbs
    has_metrics = bool(re.search(r"\b(\d+%|\$\d+|\d+x|\d+ users|\d+ requests)\b", lower_text))
    if not has_metrics:
        suggestions.append("Add quantifiable achievements to your project descriptions (e.g., 'reduced latency by 35%', 'handled 1,000+ records').")

    suggestions.append("Ensure your GitHub and portfolio links are prominently featured in your header.")
    suggestions.append("Align your project bullet points with the STAR method (Situation, Task, Action, Result).")

    return {
        "match_score": match_score,
        "target_role": target_role,
        "detected_skills": detected,
        "missing_skills": missing,
        "suggestions": suggestions,
        "extracted_length": len(resume_text)
    }
