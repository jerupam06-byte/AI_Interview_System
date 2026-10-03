import pytest
from services.resume_analyzer import analyze_resume_text


def test_resume_analyzer_text_matching():
    """Verify resume text analysis accurately identifies skills and gaps."""
    sample_text = """
    Software Engineering Graduate. Proficient in Python, Flask, PostgreSQL, and Docker.
    Built REST APIs using SQLAlchemy and performed unit testing with pytest.
    """
    analysis = analyze_resume_text(sample_text, target_role="Python Developer")
    assert analysis["match_score"] > 30.0
    assert "python" in analysis["detected_skills"]
    assert "flask" in analysis["detected_skills"]
    assert "postgresql" in analysis["detected_skills"]
    assert "docker" in analysis["detected_skills"]
    assert len(analysis["suggestions"]) > 0


def test_resume_analyzer_empty_text():
    """Empty or unparseable resumes should return safe default suggestions."""
    analysis = analyze_resume_text("", target_role="Data Analyst")
    assert analysis["match_score"] == 0.0
    assert len(analysis["detected_skills"]) == 0
