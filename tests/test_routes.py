import pytest
from models import db, Question, Interview


def test_public_routes(client):
    """Verify landing page, about page, and health check are responsive."""
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"Interview" in res_home.data

    res_about = client.get("/about")
    assert res_about.status_code == 200
    assert b"Jerusha Pamella Felix M." in res_about.data

    res_health = client.get("/health")
    assert res_health.status_code == 200
    json_data = res_health.get_json()
    assert json_data["status"] == "healthy"


def test_interview_flow_with_authenticated_user(client, test_user, app):
    """Test full cycle: Login -> Setup -> Start -> Answer -> Result -> Review."""
    # 1. Login
    login_res = client.post(
        "/login",
        data={"email": test_user.email, "password": "Secret123"},
        follow_redirects=True,
    )
    assert login_res.status_code == 200

    # 2. Access setup
    setup_res = client.get("/interview/setup")
    assert setup_res.status_code == 200

    # Ensure question exists in db
    with app.app_context():
        q = Question(
            role="Python Developer",
            difficulty="Easy",
            category="Technical",
            topic="Python",
            question="What is a list in Python?",
            expected_answer="A list is a mutable ordered sequence of elements.",
            keywords='["list", "mutable", "ordered"]',
            explanation="Core Python collection type."
        )
        db.session.add(q)
        db.session.commit()
        q_id = q.id

    # 3. Start interview
    start_res = client.post(
        "/interview/start",
        data={
            "role": "Python Developer",
            "difficulty": "Easy",
            "category": "Technical",
            "mode": "practice",
            "count": "1",
        },
        follow_redirects=False,
    )
    assert start_res.status_code == 302
    interview_url = start_res.headers.get("Location")
    interview_id = int(interview_url.split("/")[-1])

    # 4. View interview page
    view_res = client.get(f"/interview/{interview_id}")
    assert view_res.status_code == 200
    assert b"Question 1 of" in view_res.data
    assert b"Your Answer:" in view_res.data

    with app.app_context():
        # Get the first question for this role
        first_q = Question.query.filter_by(role="Python Developer").first()
        active_q_id = first_q.id

    # 5. Submit candidate answer
    ans_res = client.post(
        f"/interview/{interview_id}/answer",
        data={
            "question_id": active_q_id,
            "answer_text": "In Python, lists are mutable ordered data structures that allow modifications in place.",
        },
        follow_redirects=True,
    )
    assert ans_res.status_code == 200

    # 6. Verify result page
    result_res = client.get(f"/interview/{interview_id}/result")
    assert result_res.status_code == 200
    assert b"Personalized Interview Gap Detector" in result_res.data
    assert b"Placement Innovation Feature" in result_res.data

    # 7. Verify review page
    review_res = client.get(f"/interview/{interview_id}/review")
    assert review_res.status_code == 200
    assert b"Model Benchmark Answer" in review_res.data


def test_ai_assistant_chat_endpoint(client, test_user):
    """Test AI assistant endpoint returns structured reply without crashing."""
    client.post("/login", data={"email": test_user.email, "password": "Secret123"})
    res = client.post(
        "/assistant/chat",
        json={"message": "Can you explain the Python GIL?"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "reply" in data
    assert len(data["reply"]) > 10
