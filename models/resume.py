import json
from datetime import datetime, timezone
from . import db


class ResumeAnalysis(db.Model):
    __tablename__ = "resume_analysis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    detected_skills = db.Column(db.Text, nullable=False)  # JSON list
    suggestions = db.Column(db.Text, nullable=False)  # JSON list or text
    target_role = db.Column(db.String(100), default="General", nullable=False)
    match_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def get_detected_skills(self) -> list:
        if not self.detected_skills:
            return []
        try:
            return json.loads(self.detected_skills)
        except Exception:
            return [s.strip() for s in self.detected_skills.split(",") if s.strip()]

    def get_suggestions(self) -> list:
        if not self.suggestions:
            return []
        try:
            parsed = json.loads(self.suggestions)
            if isinstance(parsed, list):
                return parsed
            return [parsed]
        except Exception:
            return [self.suggestions]

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "target_role": self.target_role,
            "match_score": self.match_score,
            "detected_skills": self.get_detected_skills(),
            "suggestions": self.get_suggestions(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ResumeAnalysis {self.id} for User {self.user_id}>"
