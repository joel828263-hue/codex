from datetime import datetime, timedelta
import random

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.db.database import get_session, init_db
from app.models import Attempt, AttemptItem, PdfSource, Question, Subject, WrongNote
from app.schemas.api import (
    ExtractRequest,
    ExtractResponse,
    StartExamRequest,
    StartExamResponse,
    SubmitExamRequest,
    SubmitExamResponse,
    UploadPdfRequest,
    UploadPdfResponse,
    WrongNoteResponse,
    ExamQuestion,
)
from app.services.extractor import extract_questions_from_pdf

app = FastAPI(title="PDF CBT Bank MVP", version="0.1.0")


@app.get("/")
def home():
    return FileResponse("app/static_index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/subjects/{name}")
def create_subject(name: str, session: Session = Depends(get_session)):
    existing = session.exec(select(Subject).where(Subject.name == name)).first()
    if existing:
        return existing
    subject = Subject(name=name)
    session.add(subject)
    session.commit()
    session.refresh(subject)
    return subject


@app.post("/upload/pdf", response_model=UploadPdfResponse)
def upload_pdf(request: UploadPdfRequest, session: Session = Depends(get_session)):
    row = PdfSource(filename=request.filename)
    session.add(row)
    session.commit()
    session.refresh(row)
    return UploadPdfResponse(pdf_source_id=row.id, filename=row.filename)


@app.post("/admin/extract", response_model=ExtractResponse)
def admin_extract(request: ExtractRequest, session: Session = Depends(get_session)):
    source = session.get(PdfSource, request.pdf_source_id)
    if not source:
        raise HTTPException(status_code=404, detail="PDF source not found")

    created = extract_questions_from_pdf(session, request.pdf_source_id, request.subject_id)
    return ExtractResponse(message="extraction completed", created_questions=created)


@app.post("/exam/start", response_model=StartExamResponse)
def exam_start(request: StartExamRequest, session: Session = Depends(get_session)):
    questions = session.exec(
        select(Question).where(Question.subject_id == request.subject_id)
    ).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No questions in subject")

    random.shuffle(questions)
    selected = questions[: request.question_count]

    attempt = Attempt(
        user_id=request.user_id,
        subject_id=request.subject_id,
        question_count=len(selected),
        mode=request.mode,
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    out_questions = []
    for q in selected:
        item = AttemptItem(attempt_id=attempt.id, question_id=q.id)
        session.add(item)
        session.commit()
        session.refresh(item)

        out_questions.append(
            ExamQuestion(
                attempt_item_id=item.id,
                question_id=q.id,
                stem=q.stem,
                question_image_path=q.question_image_path,
                choices=[
                    {"label": "A", "text": q.choice_a},
                    {"label": "B", "text": q.choice_b},
                    {"label": "C", "text": q.choice_c},
                    {"label": "D", "text": q.choice_d},
                ],
            )
        )

    return StartExamResponse(attempt_id=attempt.id, started_at=attempt.started_at, questions=out_questions)


@app.post("/exam/{attempt_id}/submit", response_model=SubmitExamResponse)
def exam_submit(
    attempt_id: int, request: SubmitExamRequest, session: Session = Depends(get_session)
):
    attempt = session.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    correct = 0
    total = 0
    for answer in request.items:
        item = session.get(AttemptItem, answer.attempt_item_id)
        if not item or item.attempt_id != attempt_id:
            raise HTTPException(status_code=400, detail="Invalid attempt item")

        question = session.get(Question, item.question_id)
        if not question:
            continue

        item.selected_answer = answer.selected_answer
        item.is_correct = question.answer == answer.selected_answer
        session.add(item)

        total += 1
        if item.is_correct:
            correct += 1
        else:
            note = session.exec(
                select(WrongNote).where(
                    WrongNote.user_id == attempt.user_id,
                    WrongNote.question_id == question.id,
                )
            ).first()
            if not note:
                note = WrongNote(user_id=attempt.user_id, question_id=question.id)

            note.wrong_count += 1
            note.last_wrong_answer = answer.selected_answer
            note.last_wrong_at = datetime.utcnow()
            note.next_review_at = datetime.utcnow() + timedelta(days=3)
            session.add(note)

    attempt.submitted_at = datetime.utcnow()
    attempt.score = (correct / total * 100.0) if total else 0.0
    session.add(attempt)
    session.commit()

    return SubmitExamResponse(
        attempt_id=attempt_id, correct_count=correct, total_count=total, score=attempt.score
    )


@app.get("/wrong-notes/{user_id}", response_model=list[WrongNoteResponse])
def get_wrong_notes(user_id: str, session: Session = Depends(get_session)):
    notes = session.exec(select(WrongNote).where(WrongNote.user_id == user_id)).all()
    return [
        WrongNoteResponse(
            question_id=n.question_id,
            wrong_count=n.wrong_count,
            last_wrong_answer=n.last_wrong_answer,
            last_wrong_at=n.last_wrong_at,
            next_review_at=n.next_review_at,
        )
        for n in notes
    ]
