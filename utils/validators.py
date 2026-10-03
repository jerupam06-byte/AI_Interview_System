import re
from typing import Tuple


def validate_email_address(email: str) -> bool:
    """Basic regex validation for email structure."""
    if not email or len(email) > 120:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_registration(name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
    """Validates user registration form fields."""
    if not name or len(name.strip()) < 2:
        return False, "Full Name must be at least 2 characters long."
    if not email or not validate_email_address(email):
        return False, "Please provide a valid email address."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, ""


def validate_interview_setup(role: str, difficulty: str, category: str, mode: str) -> Tuple[bool, str]:
    """Validates interview configuration options."""
    valid_roles = ["Python Developer", "AI/ML Engineer", "Data Analyst"]
    valid_difficulties = ["Easy", "Medium", "Hard", "All"]
    valid_categories = ["Technical", "HR / Behavioral", "Mixed"]
    valid_modes = ["practice", "real"]

    if role not in valid_roles:
        return False, "Invalid role selected."
    if difficulty not in valid_difficulties:
        return False, "Invalid difficulty selected."
    if category not in valid_categories:
        return False, "Invalid interview category selected."
    if mode not in valid_modes:
        return False, "Invalid mode selected."

    return True, ""
