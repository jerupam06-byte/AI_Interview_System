import pytest
from models import User


def test_user_registration(client, app):
    """Test valid user registration and automatic redirection."""
    response = client.post(
        "/register",
        data={
            "name": "Alex Hunter",
            "email": "alex@university.edu",
            "password": "Password123",
            "confirm_password": "Password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="alex@university.edu").first()
        assert user is not None
        assert user.name == "Alex Hunter"
        assert user.check_password("Password123") is True


def test_duplicate_email_registration(client, test_user):
    """Test that duplicate email registration is rejected."""
    response = client.post(
        "/register",
        data={
            "name": "Another Candidate",
            "email": test_user.email,
            "password": "Password123",
            "confirm_password": "Password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already exists" in response.data.lower()


def test_login_invalid_password(client, test_user):
    """Test that incorrect password prevents login."""
    response = client.post(
        "/login",
        data={
            "email": test_user.email,
            "password": "WrongPassword!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"invalid email or password" in response.data.lower()


def test_protected_routes_redirect(client):
    """Test that unauthenticated access to dashboard/interview redirects to login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in (302, 401)
    assert "/login" in response.headers.get("Location", "")
