import pytest
from services.gap_detector import classify_term_to_skill, analyze_interview_gaps
from models import db, Question, Interview, Answer


def test_classify_term_to_skill():
    """Verify terms map accurately into their skill taxonomy areas."""
    assert classify_term_to_skill("global interpreter lock") == "Python"
    assert classify_term_to_skill("list comprehension") == "Python"
    assert classify_term_to_skill("window functions") == "SQL & Databases"
    assert classify_term_to_skill("star schema") == "SQL & Databases"
    assert classify_term_to_skill("overfitting") == "Machine Learning"
    assert classify_term_to_skill("transformer") == "NLP & Transformers"
    assert classify_term_to_skill("a/b testing") == "Data Analysis & Statistics"
    assert classify_term_to_skill("star method") == "HR & Communication"


def test_analyze_interview_gaps(app, test_user):
    """Test full Gap Detector execution across answered interview session."""
    with app.app_context():
        q1 = Question(
            role="Python Developer",
            difficulty="Medium",
            category="Technical",
            topic="Python",
            question="Explain the GIL in Python.",
            expected_answer="The Global Interpreter Lock is a mutex in CPython that controls bytecode execution.",
            keywords='["global interpreter lock", "gil", "cpython", "mutex"]'
        )
        q2 = Question(
            role="Python Developer",
            difficulty="Medium",
            category="Technical",
            topic="SQL",
            question="How do you optimize SQL queries?",
            expected_answer="Use indexing, analyze slow queries, and solve N+1 problems with eager loading.",
            keywords='["indexing", "eager loading", "n+1 problem"]'
        )
        db.session.add_all([q1, q2])
        db.session.commit()

        interview = Interview(
            user_id=test_user.id,
            role="Python Developer",
            difficulty="Medium",
            category="Technical",
            mode="practice",
            total_questions=2
        )
        db.session.add(interview)
        db.session.commit()

        # High scoring answer: candidate articulated GIL concepts
        ans1 = Answer(
            interview_id=interview.id,
            question_id=q1.id,
            answer_text="The GIL is a mutex in CPython that serializes execution.",
            final_question_score=85.0
        )
        # Low scoring answer: candidate missed SQL concepts
        ans2 = Answer(
            interview_id=interview.id,
            question_id=q2.id,
            answer_text="I try to write simple queries.",
            final_question_score=30.0
        )
        db.session.add_all([ans1, ans2])
        db.session.commit()

        gap_report = analyze_interview_gaps(interview)
        assert "demonstrated" in gap_report
        assert "priority_gaps" in gap_report
        assert "recommendations" in gap_report
        assert "skill_breakdown" in gap_report
        
        # Verify demonstrated contains GIL/mutex concepts
        demo_concepts = [d["concept"] for d in gap_report["demonstrated"]]
        assert any(c in demo_concepts for c in ["gil", "mutex", "cpython", "global interpreter lock"])

        # Verify priority gaps contains omitted SQL concepts
        gap_concepts = [g["concept"] for g in gap_report["priority_gaps"]]
        assert any(c in gap_concepts for c in ["indexing", "eager loading", "n+1 problem"])
