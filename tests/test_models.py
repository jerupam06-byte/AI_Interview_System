import pytest
from models import db, User, Question, Interview, Answer


def test_user_password_hashing(app):
    with app.app_context():
        user = User(name="Dev User", email="dev@example.com")
        user.set_password("MySecurePass#2026")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "MySecurePass#2026"
        assert user.check_password("MySecurePass#2026") is True
        assert user.check_password("WrongPassword") is False


def test_question_keywords_helpers(app):
    with app.app_context():
        q = Question(
            role="Python Developer",
            difficulty="Easy",
            category="Technical",
            topic="Python",
            question="What is a tuple?",
            expected_answer="An immutable ordered sequence.",
        )
        q.set_keywords_list(["tuple", "immutable", "ordered"])
        db.session.add(q)
        db.session.commit()

        fetched = db.session.get(Question, q.id)
        assert fetched.get_keywords_list() == ["tuple", "immutable", "ordered"]


def test_interview_and_answer_score_calculation(app, test_user):
    with app.app_context():
        q = Question(
            role="Python Developer",
            difficulty="Easy",
            category="Technical",
            question="What is PEP 8?",
            expected_answer="Style guide for Python.",
            keywords='["pep 8", "style guide"]'
        )
        db.session.add(q)
        db.session.commit()

        interview = Interview(
            user_id=test_user.id,
            role="Python Developer",
            difficulty="Easy",
            category="Technical",
            total_questions=2
        )
        db.session.add(interview)
        db.session.commit()

        ans1 = Answer(
            interview_id=interview.id,
            question_id=q.id,
            answer_text="Style guide for Python code.",
            final_question_score=80.0
        )
        ans2 = Answer(
            interview_id=interview.id,
            question_id=q.id,
            answer_text="Style rules.",
            final_question_score=90.0
        )
        db.session.add_all([ans1, ans2])
        db.session.commit()

        avg = interview.calculate_final_score()
        assert avg == 85.0
        assert interview.final_score == 85.0
