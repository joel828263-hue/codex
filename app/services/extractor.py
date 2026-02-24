from sqlmodel import Session

from app.models import Question


def extract_questions_from_pdf(session: Session, pdf_source_id: int, subject_id: int) -> int:
    """MVP mock extractor.

    실서비스에서는 OpenAI Responses API + Structured Outputs로 대체하세요.
    """
    seed_question = Question(
        subject_id=subject_id,
        pdf_source_id=pdf_source_id,
        stem="샘플 문제: 2 + 2는?",
        choice_a="1",
        choice_b="2",
        choice_c="3",
        choice_d="4",
        answer="D",
        explanation="2 + 2 = 4",
        difficulty="easy",
        question_image_path="/static/questions/sample_q.png",
        explanation_image_path="/static/explanations/sample_e.png",
    )
    session.add(seed_question)
    session.commit()
    return 1
