import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models import db, Interview, Question, Answer
from services.question_service import get_questions_for_interview
from services.evaluator import evaluate_candidate_answer
from services.gap_detector import analyze_interview_gaps
from utils.validators import validate_interview_setup

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/interview/setup", methods=["GET"])
@login_required
def setup():
    return render_template("interview/setup.html")


@interview_bp.route("/interview/start", methods=["POST"])
@login_required
def start():
    role = request.form.get("role", "Python Developer").strip()
    difficulty = request.form.get("difficulty", "Medium").strip()
    category = request.form.get("category", "Technical").strip()
    mode = request.form.get("mode", "practice").strip()
    count_str = request.form.get("count", "5").strip()

    try:
        count = int(count_str)
        count = max(1, min(10, count))
    except ValueError:
        count = 5

    is_valid, err_msg = validate_interview_setup(role, difficulty, category, mode)
    if not is_valid:
        flash(err_msg, "error")
        return redirect(url_for("interview.setup"))

    # Fetch questions
    questions = get_questions_for_interview(role, difficulty, category, count=count)
    if not questions:
        flash("No questions found for the selected criteria. Please try another selection.", "warning")
        return redirect(url_for("interview.setup"))

    # Create interview record
    interview = Interview(
        user_id=current_user.id,
        role=role,
        difficulty=difficulty,
        category=category,
        mode=mode,
        total_questions=len(questions),
    )
    db.session.add(interview)
    db.session.commit()

    # Store question ID list in session for ordered traversal
    session[f"interview_{interview.id}_questions"] = [q.id for q in questions]

    return redirect(url_for("interview.view_interview", id=interview.id))


@interview_bp.route("/interview/<int:id>", methods=["GET"])
@login_required
def view_interview(id):
    interview = Interview.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if interview.is_completed:
        return redirect(url_for("interview.result", id=interview.id))

    # Retrieve question sequence
    q_ids = session.get(f"interview_{interview.id}_questions")
    if not q_ids:
        # Reconstruct if session lost
        q_ids = [a.question_id for a in interview.answers]
        if not q_ids:
            flash("Interview session expired. Please start a new interview.", "warning")
            return redirect(url_for("interview.setup"))

    # Current index: number of answered questions
    answered_q_ids = [a.question_id for a in interview.answers]
    current_index = len(answered_q_ids)

    if current_index >= len(q_ids):
        # All answered - finish interview
        return finish_interview_internal(interview)

    current_q_id = q_ids[current_index]
    current_question = db.get_or_404(Question, current_q_id)

    total_questions = len(q_ids)
    progress_percent = int((current_index / total_questions) * 100)

    # Note: We NEVER pass expected_answer or keywords to the interview template in Real Interview mode
    return render_template(
        "interview/interview.html",
        interview=interview,
        question=current_question,
        question_index=current_index + 1,
        total_questions=total_questions,
        progress_percent=progress_percent,
        is_real_mode=(interview.mode == "real"),
    )


@interview_bp.route("/interview/<int:id>/answer", methods=["POST"])
@login_required
def submit_answer(id):
    interview = Interview.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if interview.is_completed:
        return jsonify({"error": "Interview is already finished."}), 400

    # Read payload (supports JSON or Form POST)
    if request.is_json:
        data = request.get_json() or {}
        question_id = data.get("question_id")
        answer_text = data.get("answer_text", "").strip()
    else:
        question_id = request.form.get("question_id")
        answer_text = request.form.get("answer_text", "").strip()

    try:
        question_id = int(question_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid question ID."}), 400

    question = db.get_or_404(Question, question_id)

    # Run NLP evaluation pipeline
    eval_result = evaluate_candidate_answer(
        question_text=question.question,
        expected_answer=question.expected_answer,
        candidate_answer=answer_text,
        keywords=question.get_keywords_list()
    )

    # Save answer record
    answer = Answer(
        interview_id=interview.id,
        question_id=question.id,
        answer_text=answer_text,
        similarity_score=eval_result["similarity_score"],
        keyword_score=eval_result["keyword_score"],
        final_question_score=eval_result["final_question_score"],
    )
    answer.set_feedback_dict(eval_result["feedback"])
    db.session.add(answer)
    db.session.commit()

    # Check if more questions remain
    q_ids = session.get(f"interview_{interview.id}_questions", [])
    answered_count = len(interview.answers)
    is_finished = answered_count >= len(q_ids) if q_ids else False

    if is_finished:
        finish_interview_internal(interview)
        redirect_target = url_for("interview.result", id=interview.id)
    else:
        redirect_target = url_for("interview.view_interview", id=interview.id)

    if request.is_json:
        return jsonify({
            "status": "success",
            "is_finished": is_finished,
            "next_url": redirect_target,
            "eval_result": eval_result if interview.mode == "practice" else None
        })

    return redirect(redirect_target)


@interview_bp.route("/interview/<int:id>/finish", methods=["POST"])
@login_required
def finish(id):
    interview = Interview.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return finish_interview_internal(interview)


def finish_interview_internal(interview):
    """Helper to finalize score and set completion timestamp."""
    interview.completed_at = datetime.now(timezone.utc)
    interview.calculate_final_score()
    db.session.commit()
    # Clean up session question sequence
    session.pop(f"interview_{interview.id}_questions", None)
    return redirect(url_for("interview.result", id=interview.id))


@interview_bp.route("/interview/<int:id>/result", methods=["GET"])
@login_required
def result(id):
    interview = Interview.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    # If answers exist but not marked completed
    if not interview.is_completed:
        interview.completed_at = datetime.now(timezone.utc)
        interview.calculate_final_score()
        db.session.commit()

    # Calculate component averages
    answers = interview.answers
    if answers:
        avg_sim = round(sum(a.similarity_score for a in answers) / len(answers), 1)
        avg_kw = round(sum(a.keyword_score for a in answers) / len(answers), 1)
        final_score = interview.final_score or 0.0
    else:
        avg_sim = 0.0
        avg_kw = 0.0
        final_score = 0.0

    # Analyze gaps via Interview Gap Detector
    gap_analysis = analyze_interview_gaps(interview)

    return render_template(
        "interview/result.html",
        interview=interview,
        avg_similarity=avg_sim,
        avg_keywords=avg_kw,
        final_score=final_score,
        gap_analysis=gap_analysis,
    )


@interview_bp.route("/interview/<int:id>/review", methods=["GET"])
@login_required
def review(id):
    interview = Interview.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    answers = interview.answers
    return render_template("interview/review.html", interview=interview, answers=answers)
