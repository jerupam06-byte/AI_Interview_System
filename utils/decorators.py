from functools import wraps
from flask import session, redirect, url_for, flash, request
from flask_login import current_user


def login_required_custom(f):
    """
    Ensures user is authenticated via session or flask-login.
    Redirects to login with next URL parameter if unauthenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_logged_in = False
        if current_user and current_user.is_authenticated:
            is_logged_in = True
        elif session.get("user_id"):
            is_logged_in = True

        if not is_logged_in:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.endpoint))
        return f(*args, **kwargs)
    return decorated_function
