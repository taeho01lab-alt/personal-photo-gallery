# Personal Photo Gallery Web Application

소프트웨어공학 프로젝트 요구사항에 맞춘 개인 사진 갤러리 웹 애플리케이션입니다. 제공된 초기 ZIP의 구조를 유지하여 루트 Flask 백엔드와 `frontend/` React 앱으로 구성했습니다.

## Stack

- Backend: Flask
- Frontend: React Create React App
- Database: SQLite

## Structure

```text
.
├── app.py
├── schema.sql
├── API.md
├── requirements.txt
├── tests/
├── uploads/
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
└── docs/
```

## Features

- 회원가입, 로그인, 로그아웃
- 비회원도 조회 가능한 사용자 목록
- 로그인 사용자 전용 사진 조회, 업로드, 본인 사진 수정
- 키워드 기반 사진 검색
- 게시물 기반 DM 전송
- 메시지함 조회, 답장, 삭제

## Run Backend

```powershell
pip install -r requirements.txt
python app.py
```

기본 주소는 `http://127.0.0.1:5000`입니다.

5000 포트가 이미 사용 중이거나 OneDrive 경로에서 SQLite 오류가 나면 다음처럼 실행하세요.

```powershell
$env:PORT='5051'
$env:DATABASE='C:\Users\taeho\Downloads\gallery_app.db'
$env:UPLOAD_FOLDER='C:\Users\taeho\Downloads\gallery_uploads'
python app.py
```

## Run Frontend

```powershell
cd frontend
npm install
$env:REACT_APP_API_BASE_URL='http://127.0.0.1:5000'
npm start
```

백엔드를 5051 포트로 띄웠다면 `REACT_APP_API_BASE_URL`도 `http://127.0.0.1:5051`로 지정하세요.

## Test

```powershell
python -m pytest -p no:cacheprovider --basetemp=.pytest_tmp tests
```

## Documents

- [API.md](API.md)
- [docs/use_cases.md](docs/use_cases.md)
- [docs/test_cases.md](docs/test_cases.md)
- [docs/uml.md](docs/uml.md)
- [docs/test_report.md](docs/test_report.md)
