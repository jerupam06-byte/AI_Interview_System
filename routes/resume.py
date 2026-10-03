import json
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, ResumeAnalysis
from services.resume_analyzer import extract_text_from_pdf, analyze_resume_text

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume", methods=["GET"])
@login_required
def analyzer():
    previous_analyses = (
        ResumeAnalysis.query.filter_by(user_id=current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template("resume/analyzer.html", previous_analyses=previous_analyses, result=None)


@resume_bp.route("/resume/analyze", methods=["POST"])
@login_required
def analyze():
    if "resume" not in request.files:
        flash("Please select a PDF resume file to upload.", "warning")
        return redirect(url_for("resume.analyzer"))

    file = request.files["resume"]
    target_role = request.form.get("target_role", "Python Developer").strip()

    if file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("resume.analyzer"))

    if not file.filename.lower().endswith(".pdf"):
        flash("Only PDF format resumes are supported.", "error")
        return redirect(url_for("resume.analyzer"))

    try:
        # Read into memory without writing to disk
        pdf_bytes = file.read()
        extracted_text = extract_text_from_pdf(pdf_bytes)

        if not extracted_text:
            flash("Could not extract readable text from this PDF. Please ensure it is not a scanned image.", "warning")
            return redirect(url_for("resume.analyzer"))

        analysis = analyze_resume_text(extracted_text, target_role=target_role)

        record = ResumeAnalysis(
            user_id=current_user.id,
            filename=secure_filename(file.filename),
            extracted_text=extracted_text[:4000],  # store reasonable preview snippet
            detected_skills=json.dumps(analysis["detected_skills"]),
            suggestions=json.dumps(analysis["suggestions"]),
            target_role=target_role,
            match_score=analysis["match_score"]
        )
        db.session.add(record)
        db.session.commit()

        previous_analyses = (
            ResumeAnalysis.query.filter_by(user_id=current_user.id)
            .order_by(ResumeAnalysis.created_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "resume/analyzer.html",
            previous_analyses=previous_analyses,
            result=analysis,
            filename=secure_filename(file.filename)
        )
    except Exception as e:
        flash(f"Resume analysis failed: {str(e)}", "error")
        return redirect(url_for("resume.analyzer"))
