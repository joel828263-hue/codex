# 경제 뉴스 + 종목 리포트 자동 수집기 (초보자용)

코딩을 잘 몰라도 **복붙 실행**으로 시작할 수 있게 만든 파이썬 예제입니다.

## 1) 딱 1번만 설치

### Windows
1. [python.org](https://www.python.org/downloads/) 에서 Python 설치
2. 설치할 때 **Add Python to PATH** 체크
3. 터미널(CMD/PowerShell) 열고 아래 입력

```bash
pip install -r requirements.txt
```

### Mac
```bash
python3 -m pip install -r requirements.txt
```

## 2) 실행

예: 삼성전자 리포트 + 경제뉴스 수집

```bash
python app.py --stock 삼성전자
```

Mac에서 `python`이 안되면:

```bash
python3 app.py --stock 삼성전자
```

## 3) 결과 확인

실행 후 `output/` 폴더에 아래 파일이 생깁니다.
- `news_날짜시간.md`
- `report_종목명_날짜시간.md`

텍스트 편집기로 열면 번역된 내용이 보입니다.

## 자주 생기는 에러

- `pip` 명령이 없다고 나오면: `python -m pip install -r requirements.txt`
- SSL/네트워크 오류: 잠시 후 재시도
- 특정 날짜에 리포트가 없으면: 종목명을 다르게 시도 (예: `삼성전자`, `SK하이닉스`)

## 자동화(선택)
- Windows: 작업 스케줄러에 `python app.py --stock 삼성전자` 등록
- Mac/Linux: 크론탭에 등록
