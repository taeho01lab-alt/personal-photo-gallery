# Personal Photo Gallery Web Application

## 프로젝트 정보

- 과목: 소프트웨어공학 팀 프로젝트
- 소속: 동국대학교
- 프로젝트명: Personal Photo Gallery Web Application
- 팀원:
  - 2021112087 손태호
  - 2021112039 김지태
- 주요 기술:
  - Backend: Flask, Python
  - Frontend: React, Create React App
  - Database: SQLite

## 프로젝트 개요

Personal Photo Gallery Web Application은 사용자가 사진을 업로드하고, 다른 사용자가 업로드한 사진을 조회하며, 사진 게시물을 기반으로 업로더에게 Direct Message를 보낼 수 있는 웹 애플리케이션입니다.

이 프로젝트는 단순한 사진 업로드 기능만 제공하는 것이 아니라, 사용자 권한에 따라 접근 가능한 기능을 분리하고, 사진 검색 및 메시지 기능까지 포함하여 작은 규모의 SNS형 사진 갤러리 서비스를 구성하는 것을 목표로 합니다.

백엔드는 루트 디렉터리의 `app.py`에서 Flask API 서버로 동작하고, 프론트엔드는 `frontend/` 폴더 안의 React 애플리케이션으로 동작합니다. 데이터는 SQLite 데이터베이스에 저장되며, 업로드된 사진 파일은 서버의 `uploads/` 폴더에 저장됩니다.

## 구현 목표

이 프로젝트의 핵심 목표는 다음과 같습니다.

1. 사용자는 회원가입, 로그인, 로그아웃을 할 수 있어야 합니다.
2. 비회원도 전체 사용자 목록은 조회할 수 있어야 합니다.
3. 사진 조회, 사진 업로드, 사진 수정, 검색, 메시지 기능은 로그인 사용자만 사용할 수 있어야 합니다.
4. 로그인한 사용자는 설명, 키워드, 사진 비밀번호를 포함하여 사진을 업로드할 수 있어야 합니다.
5. 사진 업로더는 본인이 업로드한 사진의 설명, 키워드, 사진 비밀번호를 수정할 수 있어야 합니다.
6. 사용자는 키워드를 기반으로 사진을 검색할 수 있어야 합니다.
7. 사용자는 다른 사용자의 사진 게시물에서 업로더에게 DM을 보낼 수 있어야 합니다.
8. 사용자는 메시지함에서 받은 메시지와 보낸 메시지를 조회하고, 답장하거나 삭제할 수 있어야 합니다.

## 주요 기능

### 1. 회원 기능

회원 기능은 사용자 인증과 권한 처리를 담당합니다.

- 회원가입
- 로그인
- 로그아웃
- 현재 로그인 사용자 조회
- 세션 기반 인증 처리

회원가입 시 사용자는 아이디, 비밀번호, 표시 이름, 이메일을 입력할 수 있습니다. 비밀번호는 평문으로 저장하지 않고 Werkzeug의 password hash 기능을 이용하여 해시 형태로 저장합니다. 로그인에 성공하면 Flask 세션에 사용자 ID를 저장하여 이후 요청에서 로그인 상태를 확인합니다.

### 2. 사용자 목록 기능

사용자 목록 조회는 비회원도 접근할 수 있는 기능입니다. 프로젝트 요구사항에서 비회원에게 허용되는 기능은 사용자 목록 조회뿐이므로, 이 기능은 별도의 로그인 검사를 하지 않습니다.

제공되는 사용자 정보는 다음과 같습니다.

- 사용자 ID
- 아이디
- 표시 이름
- 이메일
- 가입일

### 3. 사진 기능

사진 기능은 로그인한 사용자만 사용할 수 있습니다.

지원 기능은 다음과 같습니다.

- 전체 사진 목록 조회
- 사진 상세 조회
- 사진 업로드
- 본인 사진 수정
- 업로드된 사진 파일 제공

사진 업로드 시 필요한 값은 다음과 같습니다.

- 사진 파일
- 사진 설명
- 키워드
- 사진 비밀번호

사진 파일은 서버의 `uploads/` 폴더에 저장됩니다. 실제 저장 파일명은 UUID 기반으로 생성하여 파일명 충돌을 방지합니다. 원본 파일명은 데이터베이스에 별도로 저장합니다.

사진 수정은 본인 사진에 대해서만 가능합니다. 다른 사용자가 업로드한 사진을 수정하려고 하면 서버는 `403 Forbidden` 응답을 반환합니다.

### 4. 키워드 검색 기능

사진 검색은 키워드 기반으로 동작합니다.

사용자가 검색어를 입력하면 서버는 다음 항목을 기준으로 사진을 검색합니다.

- 사진 설명
- 사진에 연결된 키워드

키워드는 쉼표로 구분하여 입력할 수 있습니다. 예를 들어 `travel, summer, friend`처럼 입력하면 각각의 키워드가 분리되어 저장됩니다.

### 5. Direct Message 기능

DM 기능은 이 프로젝트의 중요한 기능 중 하나입니다. 사용자는 다른 사용자의 사진 게시물에서 해당 사진의 업로더에게 메시지를 보낼 수 있습니다.

지원 기능은 다음과 같습니다.

- 게시물 기반 DM 전송
- 메시지함 조회
- 받은 메시지 조회
- 보낸 메시지 조회
- 메시지 답장
- 메시지 삭제
- 메시지 읽음 처리 API

메시지는 특정 사진과 연결될 수 있습니다. 따라서 사용자는 어떤 사진을 보고 메시지를 보냈는지 메시지함에서 확인할 수 있습니다. 답장은 기존 메시지를 기준으로 상대방에게 새 메시지를 보내는 방식으로 구현했습니다.

메시지 삭제는 실제 DB row를 즉시 삭제하는 방식이 아니라, 보낸 사람과 받은 사람 각각의 삭제 상태를 따로 저장하는 방식입니다. 따라서 한 사용자가 메시지를 삭제해도 상대방의 메시지함에는 영향을 주지 않습니다.

## 권한 정책

프로젝트 요구사항에 맞춰 권한을 다음과 같이 분리했습니다.

| 기능 | 비회원 | 로그인 사용자 |
| --- | --- | --- |
| 사용자 목록 조회 | 가능 | 가능 |
| 회원가입 | 가능 | 가능 |
| 로그인 | 가능 | 가능 |
| 사진 목록 조회 | 불가 | 가능 |
| 사진 업로드 | 불가 | 가능 |
| 사진 수정 | 불가 | 본인 사진만 가능 |
| 키워드 검색 | 불가 | 가능 |
| DM 전송 | 불가 | 가능 |
| 메시지함 조회 | 불가 | 가능 |
| 메시지 답장 | 불가 | 가능 |
| 메시지 삭제 | 불가 | 본인 관련 메시지만 가능 |

권한 처리는 Flask 백엔드의 `login_required` 데코레이터를 통해 수행합니다. 로그인하지 않은 사용자가 보호된 API에 접근하면 `401 Unauthorized` 응답을 반환합니다.

## 프로젝트 구조

```text
.
├── app.py
├── schema.sql
├── requirements.txt
├── API.md
├── README.md
├── tests/
│   └── test_app.py
├── uploads/
│   └── .gitkeep
├── docs/
│   ├── use_cases.md
│   ├── test_cases.md
│   ├── uml.md
│   └── test_report.md
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js
        ├── App.css
        ├── index.js
        └── index.css
```

## 폴더 및 파일 설명

### `app.py`

Flask 백엔드 서버의 메인 파일입니다. 모든 REST API endpoint가 이 파일에 구현되어 있습니다.

주요 역할은 다음과 같습니다.

- Flask 앱 생성
- SQLite 연결 관리
- 데이터베이스 초기화
- 회원가입/로그인/로그아웃 API
- 사용자 목록 API
- 사진 업로드/조회/수정 API
- 키워드 검색 API
- DM 전송/조회/답장/삭제 API
- 업로드 이미지 파일 제공

### `schema.sql`

SQLite 데이터베이스 스키마 정의 파일입니다.

포함된 테이블은 다음과 같습니다.

- `users`: 사용자 정보
- `photos`: 사진 게시물 정보
- `keywords`: 키워드 목록
- `photo_keywords`: 사진과 키워드의 다대다 연결
- `messages`: DM 메시지 정보

### `requirements.txt`

백엔드 실행과 테스트에 필요한 Python 패키지 목록입니다.

포함된 주요 패키지는 다음과 같습니다.

- Flask
- Flask-Cors
- pytest

### `frontend/`

React 프론트엔드 애플리케이션 폴더입니다. Create React App 구조를 사용합니다.

프론트엔드는 사용자가 실제로 조작하는 화면을 담당합니다.

주요 화면은 다음과 같습니다.

- 사용자 목록 화면
- 회원가입/로그인 화면
- 사진 갤러리 화면
- 사진 업로드 화면
- 사진 수정 모달
- 메시지함 화면

### `frontend/src/App.js`

React 애플리케이션의 핵심 화면 로직이 구현된 파일입니다.

담당 기능은 다음과 같습니다.

- 로그인 상태 관리
- 사용자 목록 조회
- 사진 목록 조회
- 사진 업로드
- 사진 수정
- 키워드 검색
- DM 전송
- 메시지 조회
- 답장 및 삭제

### `frontend/src/App.css`

전체 화면의 주요 스타일을 정의합니다. 레이아웃, 버튼, 카드, 갤러리, 메시지함, 모달 등의 디자인이 포함되어 있습니다.

### `tests/`

백엔드 자동 테스트 코드가 들어 있는 폴더입니다.

`tests/test_app.py`에서는 다음 항목을 테스트합니다.

- 로그인 성공/실패
- 비회원 접근 권한
- 사진 업로드
- 사진 검색
- 본인 사진 수정
- 타인 사진 수정 차단
- DM 전송
- 메시지 답장
- 메시지 삭제

### `docs/`

프로젝트 제출용 문서 폴더입니다.

포함 문서는 다음과 같습니다.

- `use_cases.md`: Use Case 설명
- `test_cases.md`: Test Case 목록
- `uml.md`: UML 설계 문서
- `test_report.md`: 테스트 결과 보고서

### `uploads/`

사용자가 업로드한 사진 파일이 저장되는 폴더입니다. GitHub에는 실제 업로드 이미지를 올리지 않기 위해 `.gitkeep` 파일만 포함했습니다.

### `API.md`

백엔드 API 사용법을 정리한 문서입니다. 각 endpoint의 역할, 요청 형식, 주요 기능을 확인할 수 있습니다.

### `.gitignore`

GitHub에 올리지 않을 파일을 지정합니다.

예를 들어 다음 항목은 Git 관리에서 제외됩니다.

- SQLite DB 파일
- 업로드 이미지
- `node_modules`
- React 빌드 결과
- 로그 파일
- Python cache 파일

## 데이터베이스 설계

### `users`

사용자 계정 정보를 저장합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 사용자 고유 ID |
| `username` | 로그인 아이디 |
| `password_hash` | 해시된 비밀번호 |
| `display_name` | 화면에 표시할 이름 |
| `email` | 이메일 |
| `created_at` | 가입일 |

### `photos`

업로드된 사진 정보를 저장합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 사진 고유 ID |
| `owner_id` | 업로더 사용자 ID |
| `original_filename` | 원본 파일명 |
| `stored_filename` | 서버 저장 파일명 |
| `description` | 사진 설명 |
| `photo_password_hash` | 해시된 사진 비밀번호 |
| `created_at` | 업로드 일시 |
| `updated_at` | 수정 일시 |

### `keywords`

사진 검색에 사용할 키워드를 저장합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 키워드 고유 ID |
| `name` | 키워드명 |

### `photo_keywords`

사진과 키워드의 다대다 관계를 저장합니다. 하나의 사진은 여러 키워드를 가질 수 있고, 하나의 키워드는 여러 사진에 연결될 수 있습니다.

### `messages`

사용자 간 DM 정보를 저장합니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | 메시지 고유 ID |
| `sender_id` | 보낸 사용자 ID |
| `receiver_id` | 받은 사용자 ID |
| `photo_id` | 연결된 사진 ID |
| `parent_id` | 답장 대상 메시지 ID |
| `body` | 메시지 내용 |
| `is_read` | 읽음 여부 |
| `sender_deleted` | 보낸 사람 기준 삭제 여부 |
| `receiver_deleted` | 받은 사람 기준 삭제 여부 |
| `created_at` | 전송 일시 |

## API 요약

### 사용자/인증 API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `POST` | `/api/users` | 회원가입 |
| `GET` | `/api/users` | 사용자 목록 조회 |
| `POST` | `/api/login` | 로그인 |
| `POST` | `/api/logout` | 로그아웃 |
| `GET` | `/api/me` | 현재 로그인 사용자 조회 |

### 사진 API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `GET` | `/api/photos` | 사진 목록 조회 |
| `GET` | `/api/photos?keyword=검색어` | 사진 검색 |
| `GET` | `/api/photos/<photo_id>` | 사진 상세 조회 |
| `POST` | `/api/photos` | 사진 업로드 |
| `PUT` | `/api/photos/<photo_id>` | 본인 사진 수정 |

### 메시지 API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `POST` | `/api/photos/<photo_id>/messages` | 게시물 기반 DM 전송 |
| `GET` | `/api/messages?box=all` | 전체 메시지 조회 |
| `GET` | `/api/messages?box=inbox` | 받은 메시지 조회 |
| `GET` | `/api/messages?box=sent` | 보낸 메시지 조회 |
| `POST` | `/api/messages/<message_id>/reply` | 메시지 답장 |
| `DELETE` | `/api/messages/<message_id>` | 메시지 삭제 |
| `PATCH` | `/api/messages/<message_id>/read` | 메시지 읽음 처리 |

## 실행 방법

### 1. 백엔드 실행

프로젝트 루트에서 다음 명령어를 실행합니다.

```powershell
pip install -r requirements.txt
python app.py
```

기본 백엔드 주소는 다음과 같습니다.

```text
http://127.0.0.1:5000
```

정상 실행 여부는 다음 URL에서 확인할 수 있습니다.

```text
http://127.0.0.1:5000/api/health
```

### 2. 포트 또는 SQLite 경로 변경

5000 포트가 이미 사용 중이거나 OneDrive 경로에서 SQLite 파일 쓰기 오류가 발생하면 환경 변수를 지정하여 실행할 수 있습니다.

```powershell
$env:PORT='5051'
$env:DATABASE='C:\Users\taeho\Downloads\gallery_app.db'
$env:UPLOAD_FOLDER='C:\Users\taeho\Downloads\gallery_uploads'
python app.py
```

이 경우 백엔드 주소는 다음과 같습니다.

```text
http://127.0.0.1:5051
```

### 3. 프론트엔드 실행

새 PowerShell 창에서 다음 명령어를 실행합니다.

```powershell
cd frontend
npm install
$env:REACT_APP_API_BASE_URL='http://127.0.0.1:5000'
npm start
```

백엔드를 5051 포트로 실행했다면 다음처럼 설정합니다.

```powershell
$env:REACT_APP_API_BASE_URL='http://127.0.0.1:5051'
npm start
```

프론트엔드 기본 주소는 다음과 같습니다.

```text
http://127.0.0.1:3000
```

## 테스트 방법

백엔드 테스트는 pytest로 실행합니다.

```powershell
python -m pytest -p no:cacheprovider --basetemp=.pytest_tmp tests
```

테스트 항목은 다음 요구사항을 검증합니다.

- 로그인 성공/실패
- 비회원 권한 제한
- 사진 업로드 정상 처리
- 키워드 검색 결과 검증
- 본인 사진 수정 가능
- 타인 사진 수정 차단
- DM 전송
- 메시지 답장
- 메시지 삭제

프론트엔드 빌드는 다음 명령어로 확인할 수 있습니다.

```powershell
cd frontend
npm run build
```

OneDrive 폴더에서 `build` 폴더 권한 문제가 발생하면 다음처럼 빌드 경로를 변경할 수 있습니다.

```powershell
$env:BUILD_PATH='C:\Users\taeho\Downloads\gallery_build'
npm run build
```

## 제출 문서

프로젝트 제출에 필요한 보조 문서는 `docs/` 폴더에 정리되어 있습니다.

- `docs/use_cases.md`: Use Case 문서
- `docs/test_cases.md`: Test Case 문서
- `docs/uml.md`: UML 설계 문서
- `docs/test_report.md`: 테스트 결과 보고서

API 상세 문서는 `API.md`에서 확인할 수 있습니다.

## 구현 시 주의한 점

- 비회원은 사용자 목록만 조회할 수 있도록 권한을 제한했습니다.
- 사진과 메시지 기능은 로그인 사용자만 사용할 수 있도록 구현했습니다.
- 사진 수정은 업로더 본인만 가능하도록 서버에서 검증합니다.
- 키워드 검색은 사용자 검색이 아니라 사진 설명 및 사진 키워드 검색만 수행합니다.
- 비밀번호와 사진 비밀번호는 평문 저장이 아니라 해시 저장 방식을 사용했습니다.
- 메시지 삭제는 사용자별 삭제 상태를 분리하여, 한쪽 사용자의 삭제가 상대방 메시지함에 영향을 주지 않도록 했습니다.
- SQLite foreign key를 활성화하여 데이터 관계 무결성을 유지합니다.
