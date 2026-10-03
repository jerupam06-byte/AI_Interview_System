import json
from datetime import datetime, timezone
from . import db


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)
    answer_text = db.Column(db.Text, nullable=False, default="")
    similarity_score = db.Column(db.Float, default=0.0)
    keyword_score = db.Column(db.Float, default=0.0)
    final_question_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text, nullable=True)  # JSON formatted feedback
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def get_feedback_dict(self) -> dict:
        if not self.feedback:
            return {}
        try:
            return json.loads(self.feedback)
        except Exception:
            return {"general": self.feedback}

    def set_feedback_dict(self, data: dict):
        self.feedback = json.dumps(data)

    def to_dict(self, include_details: bool = True):
        data = {
            "id": self.id,
            "interview_id": self.interview_id,
            "question_id": self.question_id,
            "answer_text": self.answer_text,
            "similarity_score": self.similarity_score,
            "keyword_score": self.keyword_score,
            "final_question_score": self.final_question_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_details:
            data["feedback"] = self.get_feedback_dict()
        return data

    def __repr__(self):
        return f"<Answer {self.id} for Q{self.question_id} (Score: {self.final_question_score})>"
