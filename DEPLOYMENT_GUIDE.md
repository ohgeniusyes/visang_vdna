# 🚀 설문 앱 배포 가이드 (초보자용)

안녕하세요! 이 가이드는 IT 개발을 처음 접하시는 분들을 위해 매우 친절하게 작성되었습니다. 
걱정하지 마세요, 차근차근 따라하시면 됩니다! 😊

## 📋 전체 흐름 요약

1. **Google Sheets 준비** → 설문 응답이 저장될 구글 시트 만들기
2. **Google Cloud 설정** → 구글 시트에 자동으로 저장할 수 있게 권한 설정
3. **GitHub에 코드 올리기** → 코드를 인터넷에 올려서 공유
4. **Streamlit Cloud에 배포** → 웹사이트로 만들어서 직원들에게 링크 보내기

---

## 1단계: Google Sheets 준비하기 📊

### 1-1. 구글 시트 만들기
1. [Google Sheets](https://sheets.google.com)에 접속
2. 새 스프레드시트 만들기
3. 시트 이름을 "IT 개발자 기술 스택 설문" 등으로 변경
4. **중요**: 시트 URL을 복사해두세요
   - 예: `https://docs.google.com/spreadsheets/d/1ABC123xyz.../edit`
   - 이 URL에서 `/d/` 뒤부터 `/edit` 앞까지가 **시트 ID**입니다
   - 예: `1ABC123xyz...` ← 이 부분을 나중에 사용합니다!

---

## 2단계: Google Cloud 설정하기 ☁️

이 단계는 "구글 시트에 자동으로 데이터를 저장할 수 있는 권한"을 만드는 과정입니다.

### 2-1. Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 구글 계정으로 로그인 (비상교육 계정 사용 가능)

### 2-2. 새 프로젝트 만들기
1. 상단의 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 클릭
3. 프로젝트 이름 입력 (예: "visang-survey")
4. "만들기" 클릭
5. 프로젝트가 만들어지면 선택

### 2-3. API 활성화
1. 왼쪽 메뉴에서 "API 및 서비스" > "라이브러리" 클릭
2. 검색창에 "Google Sheets API" 입력 후 선택
3. "사용 설정" 클릭
4. 다시 "라이브러리"로 돌아가서 "Google Drive API" 검색
5. "Google Drive API"도 "사용 설정" 클릭

### 2-4. 서비스 계정 만들기
1. 왼쪽 메뉴에서 "API 및 서비스" > "사용자 인증 정보" 클릭
2. 상단의 "+ 사용자 인증 정보 만들기" 클릭
3. "서비스 계정" 선택
4. 서비스 계정 이름 입력 (예: "survey-service")
5. "만들기" 클릭
6. 역할은 "편집자" 선택 (또는 그냥 건너뛰기)
7. "완료" 클릭

### 2-5. 서비스 계정 키 다운로드
1. 방금 만든 서비스 계정 클릭
2. "키" 탭 클릭
3. "키 추가" > "새 키 만들기" 클릭
4. 키 유형: "JSON" 선택
5. "만들기" 클릭
6. **중요**: JSON 파일이 자동으로 다운로드됩니다! 이 파일을 안전한 곳에 보관하세요.

### 2-6. 구글 시트에 권한 부여
1. 다운로드한 JSON 파일을 메모장으로 열기
2. `"client_email"` 부분을 찾기 (예: `"client_email": "survey-service@...iam.gserviceaccount.com"`)
3. 이 이메일 주소를 복사
4. 만든 구글 시트로 돌아가기
5. 우측 상단의 "공유" 버튼 클릭
6. 복사한 이메일 주소 붙여넣기
7. 권한을 "편집자"로 설정
8. "완료" 또는 "전송" 클릭

---

## 3단계: GitHub에 코드 올리기 📤

GitHub는 코드를 인터넷에 올려서 공유하는 곳입니다. (무료입니다!)

### 3-1. GitHub 계정 만들기
1. [GitHub](https://github.com) 접속
2. "Sign up" 클릭하여 계정 만들기 (무료)

### 3-2. 새 저장소(Repository) 만들기
1. GitHub에 로그인
2. 우측 상단의 "+" 버튼 클릭 > "New repository" 선택
3. Repository name 입력 (예: "visang-it-survey")
4. "Public" 선택 (무료로 사용 가능)
5. "Add a README file" 체크 해제 (이미 파일이 있으므로)
6. "Create repository" 클릭

### 3-3. GitHub Desktop 설치 (가장 쉬운 방법)
1. [GitHub Desktop 다운로드](https://desktop.github.com)
2. 설치 후 실행
3. GitHub 계정으로 로그인

### 3-4. 코드를 GitHub에 올리기
1. GitHub Desktop에서 "File" > "Add Local Repository" 클릭
2. `260116_visang_vdna_it` 폴더 선택
3. 왼쪽에서 변경사항 확인
4. 하단에 커밋 메시지 입력 (예: "Initial commit")
5. "Commit to main" 클릭
6. "Publish repository" 클릭
7. Repository name 확인 후 "Publish repository" 클릭

**또는 웹에서 직접 올리기:**
1. GitHub 저장소 페이지에서 "uploading an existing file" 클릭
2. `260116_visang_vdna_it` 폴더의 모든 파일을 드래그 앤 드롭
3. 하단에 커밋 메시지 입력
4. "Commit changes" 클릭

---

## 4단계: Streamlit Cloud에 배포하기 🌐

Streamlit Cloud는 무료로 웹사이트를 만들어주는 서비스입니다!

### 4-1. Streamlit Cloud 가입
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. "Sign up" 클릭
3. GitHub 계정으로 로그인 (권장)

### 4-2. 앱 만들기
1. Streamlit Cloud 대시보드에서 "New app" 클릭
2. **Repository**: 방금 만든 GitHub 저장소 선택
3. **Branch**: `main` 선택
4. **Main file path**: `survey_app.py` 입력
5. **App URL**: 원하는 URL 이름 입력 (예: `visang-it-survey`)

### 4-3. Secrets 설정 (가장 중요!)
1. "Advanced settings" 클릭
2. "Secrets" 섹션 클릭
3. 다음 내용을 입력:

```toml
GOOGLE_SHEETS_CREDENTIALS = '''
{
  여기에 다운로드한 JSON 파일의 전체 내용을 붙여넣기
  (중괄호 { } 포함해서 전체 복사)
}
'''

SPREADSHEET_ID = "구글 시트 ID"
```

**JSON 파일 내용 복사 방법:**
- 다운로드한 JSON 파일을 메모장으로 열기
- 전체 내용 복사 (Ctrl+A, Ctrl+C)
- 위의 `'''` 사이에 붙여넣기

**시트 ID 확인 방법:**
- 구글 시트 URL: `https://docs.google.com/spreadsheets/d/1ABC123xyz.../edit`
- `/d/` 뒤부터 `/edit` 앞까지가 시트 ID

4. "Save" 클릭

### 4-4. 배포 완료!
1. "Deploy!" 클릭
2. 몇 분 기다리면 웹사이트가 만들어집니다!
3. 생성된 URL을 복사해서 직원들에게 보내면 됩니다!

---

## ✅ 체크리스트

배포 전 확인사항:
- [ ] 구글 시트 만들기 완료
- [ ] Google Cloud에서 서비스 계정 만들기 완료
- [ ] JSON 키 파일 다운로드 완료
- [ ] 구글 시트에 서비스 계정 이메일 권한 부여 완료
- [ ] GitHub에 코드 올리기 완료
- [ ] Streamlit Cloud에서 Secrets 설정 완료
- [ ] 앱 배포 완료

---

## 🆘 문제 해결

### "Google Sheets 연결 오류"가 나올 때
- JSON 파일 내용이 제대로 복사되었는지 확인
- 시트 ID가 정확한지 확인
- 서비스 계정 이메일에 시트 권한이 부여되었는지 확인

### "데이터 저장 오류"가 나올 때
- 서비스 계정이 시트의 "편집자" 권한을 가지고 있는지 확인
- 시트가 삭제되거나 이동되지 않았는지 확인

### 앱이 실행되지 않을 때
- Streamlit Cloud의 로그 확인 (오류 메시지 확인)
- Secrets 설정이 올바른지 다시 확인

---

## 📞 추가 도움이 필요하시면

- Streamlit 공식 문서: https://docs.streamlit.io
- Google Sheets API 문서: https://developers.google.com/sheets/api

---

## 🎉 완료!

이제 직원들에게 웹 링크를 보내서 설문을 받으실 수 있습니다!
응답은 자동으로 구글 시트에 저장됩니다.
