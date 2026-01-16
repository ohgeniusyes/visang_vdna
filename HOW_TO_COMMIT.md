# GitHub에 변경사항 올리기 (초보자용)

## 방법 1: GitHub Desktop 사용 (가장 쉬움) 🖥️

### 1단계: GitHub Desktop 열기
1. GitHub Desktop 프로그램 실행
2. 왼쪽에서 `260116_visang_vdna_it` 저장소 선택

### 2단계: 변경사항 확인
1. 왼쪽 패널에서 "Changes" 탭 클릭
2. 변경된 파일들이 보일 것입니다:
   - `survey_app.py` (수정됨)
   - 기타 변경된 파일들

### 3단계: Commit (커밋)
1. 하단의 "Summary"에 메시지 입력:
   ```
   Google Sheets 연결 오류 수정
   ```
2. "Description"에 추가 설명 (선택사항):
   ```
   - Secrets 처리 로직 개선
   - TOML 딕셔너리 형식 지원
   ```
3. "Commit to main" 버튼 클릭

### 4단계: Push (푸시)
1. 상단의 "Push origin" 버튼 클릭
2. 완료! 🎉

---

## 방법 2: 터미널 사용 (명령어) 💻

### Windows PowerShell 사용

1. **폴더로 이동**
   ```powershell
   cd C:\Users\user\Desktop\cursor\260116_visang_vdna_it
   ```

2. **변경사항 확인**
   ```powershell
   git status
   ```

3. **변경된 파일 추가**
   ```powershell
   git add .
   ```
   (또는 특정 파일만: `git add survey_app.py`)

4. **커밋 (변경사항 저장)**
   ```powershell
   git commit -m "Google Sheets 연결 오류 수정"
   ```

5. **GitHub에 푸시**
   ```powershell
   git push
   ```

---

## 방법 3: GitHub 웹사이트에서 직접 수정 🌐

1. GitHub 저장소 페이지 접속
2. `survey_app.py` 파일 클릭
3. 연필 아이콘(✏️) 클릭하여 편집
4. 변경사항 입력
5. 하단에 커밋 메시지 입력
6. "Commit changes" 클릭

---

## ✅ 확인 방법

푸시가 완료되면:
1. GitHub 웹사이트에서 저장소 확인
2. Streamlit Cloud가 자동으로 재배포 시작 (몇 분 소요)
3. Streamlit Cloud 대시보드에서 배포 상태 확인

---

## 🆘 문제 해결

### "Nothing to commit" 메시지가 나올 때
- 이미 모든 변경사항이 커밋되어 있습니다
- 파일을 수정했는지 확인하세요

### "Permission denied" 오류가 나올 때
- GitHub Desktop에서 로그인 확인
- 또는 GitHub 계정으로 다시 로그인

### "Remote repository not found" 오류가 나올 때
- GitHub Desktop에서 저장소가 제대로 연결되어 있는지 확인
- "Repository" > "Repository settings" > "Remote" 확인
