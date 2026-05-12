# Test Report

## Scope
- Flask API 단위/통합 테스트
- 세션 기반 권한 처리
- 사진 업로드, 검색, 수정
- DM 전송, 답장, 삭제

## Automated Tests
- `tests/test_app.py`
- 실행 명령: `python -m pytest -p no:cacheprovider --basetemp=.pytest_tmp tests`

## Manual Check List
- 비회원 상태에서 사용자 목록만 접근되는지 확인
- 회원가입 후 자동 로그인 흐름 확인
- 사진 업로드 시 설명, 키워드, 사진 비밀번호 누락 검증 확인
- 본인 사진 수정 버튼 표시 확인
- 다른 사용자 사진에서 DM 전송 확인
- 메시지함에서 답장 및 삭제 확인

## Result
- `python -m pytest -p no:cacheprovider --basetemp=.pytest_tmp tests`
- Result: 5 passed
- `REACT_APP_API_BASE_URL=http://127.0.0.1:5051 npm run build`
- Result: Create React App production build succeeded
