import os
from pathlib import Path
from flask import Flask, render_template
from flask_login import LoginManager
from config import config_by_name, Config
from models import db, User
from routes import register_blueprints
from services.question_service import seed_questions_if_needed
from utils.helpers import format_datetime, get_score_badge_class, get_score_label

BASE_DIR = Path(__file__).resolve().parent


def create_app(config_name: str = None) -> Flask:
    """Application factory for AI Interview System."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development").lower()
        if config_name not in config_by_name:
            config_name = "development"

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_object(config_by_name[config_name])

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Register Jinja context filters & processors
    @app.context_processor
    def inject_helpers():
        return {
            "format_datetime": format_datetime,
            "get_score_badge_class": get_score_badge_class,
            "get_score_label": get_score_label,
            "current_year": 2026,
            "author_name": "Jerusha Pamella Felix M.",
            "project_name": "AI-Powered Interview Preparation & Evaluation System",
        }

    # Register Blueprints
    register_blueprints(app)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_code=404, error_message="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("base.html", error_code=500, error_message="Internal Server Error"), 500

    # Auto-initialize database tables and seed starter question bank
    with app.app_context():
        try:
            db.create_all()
            seed_questions_if_needed()
        except Exception as e:
            # In some serverless/read-only build environments, db creation happens via external migration
            print(f"[Warning] Database initialization note: {e}")

    return app


# WSGI instance for Vercel and production runners
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
