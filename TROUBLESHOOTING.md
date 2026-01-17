# 문제 해결 가이드

## 문제 1: 회원가입 후 Authentication → Users에 보이지 않음

### 원인
- 이메일 확인이 완료되지 않아서 계정이 활성화되지 않았습니다
- Supabase는 이메일 확인이 완료된 사용자만 활성화합니다

### 해결 방법
1. **이메일 확인 링크 클릭**: 회원가입 시 받은 이메일의 확인 링크를 클릭하세요
2. **Users에서 확인**: Authentication → Users에서 "unconfirmed" 상태의 사용자를 확인할 수 있습니다
3. **수동 확인 (관리자)**: Supabase 대시보드에서 직접 이메일을 확인할 수도 있습니다

### 확인 방법
- Supabase 대시보드 → Authentication → Users
- "Email confirmed" 컬럼이 "No"인 경우 이메일 확인이 필요합니다
- 확인 링크를 클릭하면 "Yes"로 변경됩니다

---

## 문제 2: 회원 탈퇴 후에도 로그인이 됨

### 원인
- `SERVICE_ROLE_KEY`가 설정되지 않았거나 잘못되었을 수 있습니다
- 회원 탈퇴 시 `auth.users`에서도 삭제해야 하는데, 이는 `service_role` 키가 필요합니다

### 해결 방법
1. **Streamlit Secrets 확인**: `SERVICE_ROLE_KEY`가 올바르게 설정되어 있는지 확인하세요
2. **Supabase에서 확인**: Settings → API → service_role key 복사
3. **재시도**: 회원 탈퇴를 다시 시도하세요

### 확인 방법
- Streamlit Cloud → Manage app → Secrets
- `[SUPABASE]` 섹션에 `SERVICE_ROLE_KEY`가 있는지 확인
- 키가 올바른지 확인 (Supabase 대시보드의 키와 일치하는지)

---

## 문제 3: 이메일 확인 링크가 localhost:3000으로 리다이렉트됨

### 원인
- Supabase의 리다이렉트 URL이 설정되지 않았습니다

### 해결 방법
1. Supabase 대시보드 → Authentication → URL Configuration
2. Site URL: `https://visangvdna.streamlit.app`
3. Redirect URLs에 추가: `https://visangvdna.streamlit.app/**`
4. Save 클릭

---

## 문제 4: 회원 탈퇴 시 오류 발생

### 가능한 오류
- "회원 탈퇴에 필요한 권한이 없습니다"
- "SERVICE_ROLE_KEY를 확인해주세요"

### 해결 방법
1. Streamlit Secrets에 `SERVICE_ROLE_KEY` 추가
2. Supabase 대시보드에서 service_role key 복사
3. Streamlit Cloud Secrets에 붙여넣기
4. 앱 재시작 (Reboot app)
