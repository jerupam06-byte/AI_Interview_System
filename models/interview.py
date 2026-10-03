from datetime import datetime, timezone
from . import db


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    mode = db.Column(db.String(20), default="practice", nullable=False)  # 'practice' or 'real'
    total_questions = db.Column(db.Integer, default=5, nullable=False)
    final_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    answers = db.relationship(
        "Answer",
        backref="interview",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Answer.id",
    )

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    def calculate_final_score(self) -> float:
        """Calculates average score across all answered questions."""
        if not self.answers:
            return 0.0
        total = sum(a.final_question_score for a in self.answers if a.final_question_score is not None)
        avg = round(total / len(self.answers), 1)
        self.final_score = avg
        return avg

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role,
            "difficulty": self.difficulty,
            "category": self.category,
            "mode": self.mode,
            "total_questions": self.total_questions,
            "final_score": self.final_score,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "answers_count": len(self.answers),
        }

    def __repr__(self):
        return f"<Interview {self.id} - {self.role} ({self.mode})>"
