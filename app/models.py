from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class PdfSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(index=True)
    pdf_source_id: Optional[int] = Field(default=None, index=True)
    stem: str
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    answer: str
    explanation: str
    difficulty: str = Field(default="medium")
    question_image_path: Optional[str] = None
    explanation_image_path: Optional[str] = None


class Attempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    subject_id: int = Field(index=True)
    question_count: int
    mode: str = Field(default="random")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None


class AttemptItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(index=True)
    question_id: int = Field(index=True)
    selected_answer: Optional[str] = None
    is_correct: Optional[bool] = None


class WrongNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    question_id: int = Field(index=True)
    wrong_count: int = Field(default=0)
    last_wrong_answer: Optional[str] = None
    last_wrong_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
