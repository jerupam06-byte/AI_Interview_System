from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .question import Question
from .interview import Interview
from .answer import Answer
from .chat import ChatHistory
from .resume import ResumeAnalysis

__all__ = ["db", "User", "Question", "Interview", "Answer", "ChatHistory", "ResumeAnalysis"]
