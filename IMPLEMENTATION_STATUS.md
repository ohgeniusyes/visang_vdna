# Supabase 전환 구현 현황

## ✅ 완료된 작업

1. **Supabase 설정 가이드 작성**
   - `SUPABASE_SETUP_GUIDE.md` 파일 생성
   - 단계별 설정 방법 상세 설명

2. **인증 유틸리티 함수 작성**
   - `auth_utils.py` 파일 생성
   - 회원가입, 로그인, 비밀번호 재설정, 회원 탈퇴 함수 구현
   - @visang.com 이메일 검증 기능

3. **기본 페이지 라우팅 구조**
   - 로그인 페이지
   - 회원가입 페이지
   - 비밀번호 재설정 페이지
   - 설문 페이지 (개발 중)
   - 관리자 페이지 (기본 구조 완료)

4. **requirements.txt 업데이트**
   - supabase 라이브러리 추가
   - openpyxl 추가 (엑셀 다운로드용)

## 🔄 진행 중인 작업

1. **설문 페이지 통합**
   - 기존 설문 코드를 `show_survey_page` 함수로 이동 필요
   - Google Sheets 저장 로직을 Supabase로 변경 필요

2. **데이터 저장 함수 수정**
   - `save_to_sheets` 함수를 `save_to_supabase`로 변경 필요

## 📝 다음 단계

### 1. Supabase 프로젝트 설정 (사용자가 직접 진행)
   - `SUPABASE_SETUP_GUIDE.md` 파일 참고
   - Supabase 프로젝트 생성
   - 데이터베이스 테이블 생성
   - API 키 확인

### 2. Streamlit Secrets 설정
   ```toml
   [SUPABASE]
   URL = "https://xxxxx.supabase.co"
   ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

   [ADMIN]
   ADMIN_EMAIL = "admin@visang.com"
   ```

### 3. 설문 페이지 완성
   - 기존 설문 코드를 `show_survey_page` 함수로 이동
   - 데이터 저장을 Supabase로 변경

### 4. 테스트
   - 회원가입 테스트
   - 로그인 테스트
   - 설문 응답 저장 테스트
   - 관리자 페이지 엑셀 다운로드 테스트

## ⚠️ 주의사항

1. **비밀번호 재설정 기능**
   - 현재는 코드를 화면에 표시하는 방식 (개발용)
   - 실제 운영 환경에서는 이메일로 코드 전송 필요
   - Supabase의 이메일 기능을 사용하거나, 별도 이메일 서비스 연동 필요

2. **관리자 페이지**
   - 엑셀 다운로드 기능은 기본 구조만 완료
   - 데이터 변환 로직 추가 필요

3. **기존 Google Sheets 코드**
   - 현재는 주석 처리되지 않음
   - Supabase로 완전 전환 후 제거 필요

## 🔧 수정이 필요한 부분

1. `show_survey_page` 함수
   - 기존 main 함수의 설문 코드를 여기로 이동
   - Google Sheets 저장 로직을 Supabase로 변경

2. `save_to_sheets` 함수
   - `save_to_supabase` 함수로 변경
   - Supabase에 설문 응답 저장

3. 이메일 코드 전송
   - 실제 이메일 전송 기능 구현 필요
   - 또는 Supabase의 이메일 기능 활용
