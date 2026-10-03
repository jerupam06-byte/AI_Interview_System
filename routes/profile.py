from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Interview, Answer
from services.gap_detector import analyze_interview_gaps

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    interviews = (
        Interview.query.filter_by(user_id=current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )
    completed = [i for i in interviews if i.is_completed]
    total_answers = (
        Answer.query.join(Interview)
        .filter(Interview.user_id == current_user.id)
        .count()
    )

    avg_score = (
        round(sum(i.final_score for i in completed if i.final_score is not None) / len(completed), 1)
        if completed
        else 0.0
    )
    best_score = (
        round(max(i.final_score for i in completed if i.final_score is not None), 1)
        if completed
        else 0.0
    )

    return render_template(
        "dashboard/profile.html",
        user=current_user,
        total_interviews=len(completed),
        total_answers=total_answers,
        avg_score=avg_score,
        best_score=best_score,
        recent_interviews=completed[:5],
    )
