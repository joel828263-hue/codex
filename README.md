# PDF 기반 CBT 문제은행 MVP (FastAPI + SQLite)

요청하신 흐름을 **바로 실행 가능한 형태**로 만든 백엔드+간단 UI MVP입니다.

## 지금 되는 것

- 관리자 파이프라인 API
  - `POST /upload/pdf`: PDF 메타 등록
  - `POST /admin/extract`: (현재는 목업) PDF 추출 작업 생성
- CBT API
  - `POST /exam/start`: 과목/문항수/모드 기반 출제
  - `POST /exam/{attempt_id}/submit`: 채점 + 오답노트 누적
  - `GET /wrong-notes/{user_id}`: 오답노트 조회
- 기본 웹 화면
  - `GET /` : 과목 생성 → PDF 등록/추출 → 시험 시작/제출까지 데모 가능

---

## 1) 실행 방법 (웹앱처럼)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

브라우저에서 아래 주소를 열면 됩니다.

- 데모 UI: `http://127.0.0.1:8000`
- Swagger 문서: `http://127.0.0.1:8000/docs`

---

## 2) 데스크톱 앱처럼 실행하는 방법

완전한 네이티브 앱 패키징 전 단계로,
**앱 실행 시 자동으로 로컬 서버를 띄우고 브라우저를 열어주는 방식**을 제공합니다.

```bash
python desktop_app.py
```

- 실행하면 `http://127.0.0.1:8000` 이 자동으로 열립니다.
- 종료는 터미널에서 `Ctrl + C`.

> 원하시면 다음 단계로 PyInstaller를 붙여서 `exe`/`app` 형태 배포까지 확장 가능합니다.

---

## 3) OpenAI 추출 연동 지점

`app/services/extractor.py`의 `extract_questions_from_pdf(...)`는 현재 목업입니다.
실서비스에서는 여기서 다음을 수행하면 됩니다.

1. PDF 파일 업로드 → OpenAI Files API(file_id)
2. Responses API 입력에 `input_file` + 추출 지시문
3. Structured Outputs(JSON schema strict)로 문제/선지/정답/해설/bbox 수신
4. bbox 기반 페이지 크롭 이미지 저장 후 `questions` 반영

---

## 4) 데이터 모델

- `subjects`
- `pdf_sources`
- `questions`
- `attempts`
- `attempt_items`
- `wrong_notes`

오답노트는 `wrong_count`, `last_wrong_at`, `next_review_at`를 갱신합니다.
