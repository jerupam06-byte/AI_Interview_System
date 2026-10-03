from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Interview, Answer, Question
from services.gap_detector import analyze_interview_gaps, aggregate_historical_gaps

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Fetch user interviews ordered by created_at desc
    interviews = (
        Interview.query.filter_by(user_id=current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )

    completed_interviews = [i for i in interviews if i.is_completed]
    total_interviews = len(completed_interviews)

    # Calculate statistics
    if total_interviews > 0:
        scores = [i.final_score for i in completed_interviews if i.final_score is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        best_score = round(max(scores), 1) if scores else 0.0
    else:
        avg_score = 0.0
        best_score = 0.0

    # Total questions answered
    total_questions_answered = (
        Answer.query.join(Interview)
        .filter(Interview.user_id == current_user.id)
        .count()
    )

    # Calculate readiness score & category
    if avg_score >= 80:
        readiness_status = "Placement Ready"
        readiness_class = "readiness-high"
        readiness_percent = min(100, int(avg_score))
    elif avg_score >= 60:
        readiness_status = "Approaching Target"
        readiness_class = "readiness-mid"
        readiness_percent = int(avg_score)
    elif total_interviews > 0:
        readiness_status = "Foundation Building"
        readiness_class = "readiness-low"
        readiness_percent = max(20, int(avg_score))
    else:
        readiness_status = "Ready to Begin"
        readiness_class = "readiness-none"
        readiness_percent = 0

    recent_interviews = interviews[:5]

    # Chart data: historical scores trend (chronological)
    chronological_completed = list(reversed(completed_interviews[-10:]))
    chart_dates = [i.created_at.strftime("%b %d") for i in chronological_completed]
    chart_scores = [i.final_score or 0.0 for i in chronological_completed]

    # Aggregate skill gaps across user's history
    gap_summary = aggregate_historical_gaps(interviews)

    return render_template(
        "dashboard/dashboard.html",
        total_interviews=total_interviews,
        avg_score=avg_score,
        best_score=best_score,
        total_questions_answered=total_questions_answered,
        readiness_status=readiness_status,
        readiness_class=readiness_class,
        readiness_percent=readiness_percent,
        recent_interviews=recent_interviews,
        chart_dates=chart_dates,
        chart_scores=chart_scores,
        gap_labels=gap_summary["labels"],
        gap_values=gap_summary["values"],
    )


@dashboard_bp.route("/api/dashboard/chart-data")
@login_required
def chart_data():
    completed = (
        Interview.query.filter_by(user_id=current_user.id)
        .filter(Interview.completed_at.isnot(None))
        .order_by(Interview.created_at.asc())
        .limit(15)
        .all()
    )
    labels = [i.created_at.strftime("%b %d, %H:%M") for i in completed]
    scores = [i.final_score or 0.0 for i in completed]
    return jsonify({"labels": labels, "scores": scores})
