from flask import Blueprint, render_template, jsonify
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI-Powered Interview Preparation & Evaluation System",
        "author": "Jerusha Pamella Felix M.",
        "nlp_engine": "scikit-learn TF-IDF + Cosine Similarity",
        "database": "PostgreSQL/SQLite compatible"
    })
