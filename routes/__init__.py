from .main import main_bp
from .auth import auth_bp
from .dashboard import dashboard_bp
from .interview import interview_bp
from .history import history_bp
from .assistant import assistant_bp
from .resume import resume_bp
from .profile import profile_bp


def register_blueprints(app):
    """Registers all route blueprints to the Flask application."""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(profile_bp)
