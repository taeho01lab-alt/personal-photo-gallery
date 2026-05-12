# Photo Gallery Backend API

Flask + SQLite 기반 개인 사진 갤러리 API입니다.

## Auth

- `POST /api/users`
  - 회원가입
  - JSON: `{"username":"alice","password":"pass1234","display_name":"Alice","email":"alice@example.com"}`
- `GET /api/users`
  - 사용자 목록 조회
  - 비회원 접근 가능
- `POST /api/login`
  - 로그인
  - JSON: `{"username":"alice","password":"pass1234"}`
- `POST /api/logout`
  - 로그아웃
- `GET /api/me`
  - 현재 로그인 사용자 조회

## Photos

사진 관련 API는 로그인 사용자만 접근할 수 있습니다.

- `GET /api/photos`
  - 전체 사진 조회
- `GET /api/photos?keyword=travel`
  - 키워드/설명 기반 검색
- `POST /api/photos`
  - 사진 업로드
  - `multipart/form-data`
  - fields: `photo`, `description`, `keywords`, `photo_password`
- `PUT /api/photos/<photo_id>`
  - 본인 사진 설명/키워드/사진 비밀번호 수정
  - JSON: `{"description":"new text","keywords":"travel,summer","photo_password":"new-pass"}`

## Messages

메시지 API는 로그인 사용자만 접근할 수 있습니다.

- `POST /api/photos/<photo_id>/messages`
  - 게시물 업로더에게 DM 전송
  - JSON: `{"body":"Nice photo!"}`
- `GET /api/messages?box=all`
  - 받은 메시지와 보낸 메시지 전체 조회
- `GET /api/messages?box=inbox`
  - 받은 메시지 조회
- `GET /api/messages?box=sent`
  - 보낸 메시지 조회
- `POST /api/messages/<message_id>/reply`
  - 메시지 답장
  - JSON: `{"body":"Thank you!"}`
- `DELETE /api/messages/<message_id>`
  - 메시지 삭제
- `PATCH /api/messages/<message_id>/read`
  - 받은 메시지 읽음 처리
