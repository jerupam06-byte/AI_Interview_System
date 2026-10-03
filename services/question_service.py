import json
from pathlib import Path
from typing import List, Optional
from models import db, Question


def seed_questions_if_needed(app=None) -> int:
    """
    Seeds questions from data/questions.json into the database
    if the questions table is empty or needs updates.
    """
    json_path = Path(__file__).resolve().parent.parent / "data" / "questions.json"
    if not json_path.exists():
        return 0

    existing_count = Question.query.count()
    if existing_count > 0:
        return existing_count

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    for item in data:
        q = Question(
            role=item.get("role", "Python Developer"),
            difficulty=item.get("difficulty", "Medium"),
            category=item.get("category", "Technical"),
            topic=item.get("topic", "General"),
            question=item.get("question", ""),
            expected_answer=item.get("expected_answer", ""),
            explanation=item.get("explanation", ""),
        )
        q.set_keywords_list(item.get("keywords", []))
        db.session.add(q)
        added += 1

    db.session.commit()
    return added


def seed_default_users_if_needed():
    """Seeds default demo and admin credentials if user table is empty."""
    from models import User
    try:
        if User.query.count() == 0:
            admin = User(name="Jerusha Pamella Felix M. (Admin)", email="admin@placement.edu")
            admin.set_password("Admin@2026")
            candidate = User(name="Jerusha Felix", email="candidate@placement.edu")
            candidate.set_password("Candidate@2026")
            db.session.add_all([admin, candidate])
            db.session.commit()
    except Exception as e:
        print(f"[Warning] User seeding note: {e}")


def get_questions_for_interview(
    role: str,
    difficulty: str,
    category: str,
    count: int = 5
) -> List[Question]:
    """
    Retrieves questions matching role, difficulty, and category criteria.
    Falls back gracefully to related difficulty or category if specific filters yield fewer questions.
    """
    query = Question.query.filter_by(role=role)

    # Filter by category
    if category != "Mixed":
        query = query.filter_by(category=category)

    # Filter by difficulty
    if difficulty != "All":
        query = query.filter_by(difficulty=difficulty)

    questions = query.limit(count).all()

    # Fallback if too few questions match the strict criteria
    if len(questions) < count:
        fallback_query = Question.query.filter_by(role=role)
        existing_ids = [q.id for q in questions]
        additional = (
            fallback_query.filter(~Question.id.in_(existing_ids))
            .limit(count - len(questions))
            .all()
        )
        questions.extend(additional)

    # If still fewer, pull from any role
    if len(questions) < count:
        existing_ids = [q.id for q in questions]
        more = (
            Question.query.filter(~Question.id.in_(existing_ids))
            .limit(count - len(questions))
            .all()
        )
        questions.extend(more)

    return questions[:count]
