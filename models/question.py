import json
from datetime import datetime, timezone
from . import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    topic = db.Column(db.String(50), default="General", nullable=False)
    question = db.Column(db.Text, nullable=False)
    expected_answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=False)  # stored as JSON array string
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    answers = db.relationship("Answer", backref="question", lazy=True, cascade="all, delete-orphan")

    def get_keywords_list(self) -> list:
        if not self.keywords:
            return []
        try:
            parsed = json.loads(self.keywords)
            if isinstance(parsed, list):
                return parsed
            return [k.strip() for k in str(self.keywords).split(",") if k.strip()]
        except Exception:
            return [k.strip() for k in str(self.keywords).split(",") if k.strip()]

    def set_keywords_list(self, keywords_list: list):
        self.keywords = json.dumps(keywords_list)

    def to_dict(self, include_expected: bool = False):
        data = {
            "id": self.id,
            "role": self.role,
            "difficulty": self.difficulty,
            "category": self.category,
            "topic": self.topic,
            "question": self.question,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_expected:
            data["expected_answer"] = self.expected_answer
            data["keywords"] = self.get_keywords_list()
            data["explanation"] = self.explanation
        return data

    def __repr__(self):
        return f"<Question {self.id} - {self.role} ({self.difficulty})>"
