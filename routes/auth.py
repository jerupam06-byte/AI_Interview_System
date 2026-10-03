from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from utils.validators import validate_registration, validate_email_address

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        is_valid, error_msg = validate_registration(name, email, password, confirm_password)
        if not is_valid:
            flash(error_msg, "error")
            return render_template("auth/register.html", name=name, email=email)

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email address already exists. Please sign in.", "warning")
            return render_template("auth/register.html", name=name, email=email)

        # Create user
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        session["user_id"] = user.id
        session["user_name"] = user.name

        flash(f"Welcome to AI Interview Prep, {user.name}! Your account has been created.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.args.get("next") or request.form.get("next")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("auth/login.html", email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please check your credentials.", "error")
            return render_template("auth/login.html", email=email)

        login_user(user)
        session["user_id"] = user.id
        session["user_name"] = user.name

        flash(f"Welcome back, {user.name}!", "success")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session.pop("user_id", None)
    session.pop("user_name", None)
    flash("You have been successfully signed out.", "info")
    return redirect(url_for("main.index"))
