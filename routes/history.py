from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Interview

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
@login_required
def history():
    interviews = (
        Interview.query.filter_by(user_id=current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )

    completed = [i for i in interviews if i.is_completed]
    avg_score = (
        round(sum(i.final_score for i in completed if i.final_score is not None) / len(completed), 1)
        if completed
        else 0.0
    )

    return render_template(
        "dashboard/history.html",
        interviews=interviews,
        completed_count=len(completed),
        avg_score=avg_score,
    )
