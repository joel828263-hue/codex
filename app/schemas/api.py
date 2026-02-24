from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UploadPdfRequest(BaseModel):
    filename: str


class UploadPdfResponse(BaseModel):
    pdf_source_id: int
    filename: str


class ExtractRequest(BaseModel):
    pdf_source_id: int
    subject_id: int


class ExtractResponse(BaseModel):
    message: str
    created_questions: int


class StartExamRequest(BaseModel):
    user_id: str
    subject_id: int
    question_count: int = Field(gt=0, le=200)
    mode: Literal["random", "wrong_first", "mixed"] = "random"


class ExamQuestion(BaseModel):
    attempt_item_id: int
    question_id: int
    stem: str
    choices: list[dict[str, str]]
    question_image_path: str | None = None


class StartExamResponse(BaseModel):
    attempt_id: int
    started_at: datetime
    questions: list[ExamQuestion]


class SubmitItem(BaseModel):
    attempt_item_id: int
    selected_answer: Literal["A", "B", "C", "D"]


class SubmitExamRequest(BaseModel):
    items: list[SubmitItem]


class SubmitExamResponse(BaseModel):
    attempt_id: int
    correct_count: int
    total_count: int
    score: float


class WrongNoteResponse(BaseModel):
    question_id: int
    wrong_count: int
    last_wrong_answer: str | None
    last_wrong_at: datetime | None
    next_review_at: datetime | None
