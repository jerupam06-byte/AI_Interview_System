import pytest
from app import create_app
from models import db, User, Question, Interview


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(name="Test Candidate", email="test@candidate.edu")
        user.set_password("Secret123")
        db.session.add(user)
        db.session.commit()
        return db.session.get(User, user.id)
