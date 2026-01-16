# IT 개발자 기술 스택 설문 앱

Streamlit을 사용한 IT 개발자 기술 스택 설문 조사 웹 애플리케이션입니다.

## 기능

- 직군 선택 (13개 직군)
- 직군별 맞춤 기술 스택 선택 (콤보박스/멀티셀렉트)
- Google Sheets에 자동 저장
- 실시간 응답 수집

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. Google Sheets API 설정:
   - [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
   - API 및 서비스 > 라이브러리에서 "Google Sheets API" 및 "Google Drive API" 활성화
   - 서비스 계정 생성 및 JSON 키 다운로드
   - Google Sheet 생성 및 서비스 계정 이메일에 편집 권한 부여

3. Streamlit Secrets 설정:
   - `.streamlit/secrets.toml` 파일 생성
   - 다음 내용 추가:

```toml
GOOGLE_SHEETS_CREDENTIALS = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
'''

SPREADSHEET_ID = "your-google-sheet-id"
```

## 실행 방법

```bash
streamlit run survey_app.py
```

## 배포 방법

### Streamlit Cloud 배포

1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud)에서 앱 생성
3. Secrets에 위의 설정값 추가
4. 배포 완료!

### 로컬 서버 배포

```bash
streamlit run survey_app.py --server.port 8501
```

## 지원 직군

- Backend 개발자
- Frontend 개발자
- iOS 앱 개발자 (네이티브)
- Android 앱 개발자 (네이티브)
- 모바일 앱 개발자 (크로스플랫폼)
- LLM 개발자
- Data Scientist
- Data Analyst
- People Analyst
- DevOps
- MLOps
- Game 개발자
- 보안 엔지니어

## 기술 스택 카테고리

각 직군별로 다음 카테고리의 기술을 선택할 수 있습니다:

- 프로그래밍 언어
- 프레임워크/라이브러리
- RDB
- NoSQL
- 운영환경_OS
- 운영환경_Infra (IDC 포함)
- 운영환경_Container
- 운영환경_CI/CD
- 시각화/분석도구 (해당 직군)
- 네트워크_프로토콜_Feature
