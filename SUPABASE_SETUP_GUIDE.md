# Supabase 설정 가이드

이 가이드는 비상교육 설문 앱을 Supabase로 전환하기 위한 단계별 설정 방법입니다.

## 📋 목차
1. [Supabase 프로젝트 생성](#1-supabase-프로젝트-생성)
2. [데이터베이스 테이블 생성](#2-데이터베이스-테이블-생성)
3. [인증 설정](#3-인증-설정)
4. [API 키 확인](#4-api-키-확인)
5. [Streamlit Secrets 설정](#5-streamlit-secrets-설정)

---

## 1. Supabase 프로젝트 생성

### 1-1. Supabase 회원가입
1. https://supabase.com 접속
2. 우측 상단 "Start your project" 클릭
3. GitHub 계정으로 로그인 (또는 이메일로 회원가입)

### 1-2. 새 프로젝트 생성
1. 대시보드에서 "New Project" 클릭
2. 프로젝트 정보 입력:
   - **Name**: `visang-survey` (원하는 이름)
   - **Database Password**: 강력한 비밀번호 입력 (나중에 필요하니 기록해두세요!)
   - **Region**: `Northeast Asia (Seoul)` 선택 (한국에서 가장 가까운 지역)
   - **Pricing Plan**: Free 플랜 선택
3. "Create new project" 클릭
4. 프로젝트 생성 완료까지 1-2분 대기

---

## 2. 데이터베이스 테이블 생성

### 2-1. SQL Editor 열기
1. 좌측 메뉴에서 "SQL Editor" 클릭
2. "New query" 클릭

### 2-2. 테이블 생성 SQL 실행

아래 SQL 코드를 복사해서 SQL Editor에 붙여넣고 "Run" 버튼을 클릭하세요:

```sql
-- 1. 사용자 정보 테이블 (Supabase Auth와 연동)
-- 주의: 이 테이블은 Supabase Auth가 자동으로 생성하므로 별도로 만들지 않습니다.
-- 대신 user_profiles 테이블을 만들어 추가 정보를 저장합니다.

-- 2. 사용자 프로필 테이블
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    name TEXT,  -- 사용자 이름 (회원가입 시 입력)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 설문 응답 테이블
CREATE TABLE IF NOT EXISTS survey_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    job_role TEXT NOT NULL,
    responses JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 비밀번호 재설정 코드 테이블
CREATE TABLE IF NOT EXISTS password_reset_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 인덱스 생성 (검색 속도 향상)
CREATE INDEX IF NOT EXISTS idx_survey_responses_user_id ON survey_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_created_at ON survey_responses(created_at);
CREATE INDEX IF NOT EXISTS idx_password_reset_codes_email ON password_reset_codes(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_codes_code ON password_reset_codes(code);

-- 6. Row Level Security (RLS) 정책 설정
-- 사용자는 자신의 데이터만 볼 수 있도록 설정

-- user_profiles 테이블 RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = id);

-- survey_responses 테이블 RLS
ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own responses"
    ON survey_responses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own responses"
    ON survey_responses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 관리자는 모든 데이터를 볼 수 있도록 설정 (나중에 관리자 페이지에서 사용)
-- 주의: 실제 관리자 이메일로 변경해야 합니다!
CREATE POLICY "Admin can view all responses"
    ON survey_responses FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.email = 'admin@visang.com'  -- 관리자 이메일로 변경!
        )
    );

-- 7. 함수 생성: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 8. 트리거 생성: updated_at 자동 업데이트
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_survey_responses_updated_at
    BEFORE UPDATE ON survey_responses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2-3. 실행 확인
- SQL 실행 후 에러가 없으면 성공입니다!
- 좌측 메뉴 "Table Editor"에서 테이블이 생성되었는지 확인하세요.

---

## 3. 인증 설정

### 3-1. 이메일 확인 설정 (중요! ⭐)
**보안을 위해 이메일 확인은 필수입니다. 다른 사람의 이메일로 가입하는 것을 방지합니다.**

1. Supabase 대시보드에서 좌측 메뉴 **"Authentication"** 클릭
2. 왼쪽 메뉴에서 **"Providers"** 클릭
3. **"Email"** 섹션을 찾아서 클릭 (또는 "Email" 토글을 열기)
4. 아래 설정을 확인:
   - ✅ **"Enable email signup"** 체크되어 있어야 함 (이메일로 회원가입 허용)
   - ✅ **"Confirm email"** 또는 **"Require email confirmation"** 체크 유지 (보안을 위해 필수!)
5. 하단 **"Save"** 또는 **"Update"** 버튼 클릭

**📧 이메일 확인 프로세스:**
- 회원가입 시 이메일로 확인 링크가 전송됩니다
- 사용자가 이메일의 확인 링크를 클릭하면 계정이 활성화됩니다
- 확인 후 로그인 페이지에서 로그인할 수 있습니다

**⚠️ 보안:**
- 이메일 확인을 통해 실제 이메일 소유자만 가입할 수 있습니다
- 1000명의 임직원이 있으므로 다른 사람의 이메일로 가입하는 것을 방지합니다

### 3-2. 이메일 템플릿 설정 (선택사항)
1. "Authentication" → "Email Templates" 클릭
2. 비밀번호 재설정 이메일 템플릿을 커스터마이징할 수 있습니다.

---

## 4. API 키 확인 (중요! ⭐)

### 4-1. 프로젝트 설정에서 API 키 확인
1. Supabase 대시보드에서 좌측 메뉴 맨 아래에 있는 **"Settings"** (⚙️ 톱니바퀴 아이콘) 클릭
2. 왼쪽 메뉴에서 **"API"** 클릭
3. 화면에 여러 정보가 표시됩니다. 다음 3가지를 찾아서 복사해두세요:

   **📍 Project URL 찾기:**
   - 화면 상단에 **"Project URL"** 또는 **"URL"** 이라고 적혀있는 섹션을 찾으세요
   - 또는 **"Configuration"** 섹션에서 찾을 수 있습니다
   - 형식: `https://[프로젝트ID].supabase.co`
   - 예시: `https://vjqobilsymvbnhzfrmvw.supabase.co` (프로젝트 ID는 각자 다릅니다)
   - ⚠️ **주의**: `https://supabase.com/dashboard/project/...` 형식은 **아닙니다!**
   - 반드시 `https://[프로젝트ID].supabase.co` 형식이어야 합니다
   - 이 전체 주소를 복사하세요
   
   **📍 anon public key 찾기:**
   - "Project API keys" 섹션에서 찾을 수 있습니다
   - "anon" 또는 "public" 이라고 적혀있는 키입니다
   - "Reveal" 버튼을 클릭하면 전체 키가 보입니다
   - 예시: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI5MCwiZXhwIjoxOTU0NTQzMjkwfQ.abcdefghijklmnopqrstuvwxyz1234567890`
   - 이 긴 문자열 전체를 복사하세요
   
   **📍 service_role key 찾기:**
   - 같은 "Project API keys" 섹션에서 찾을 수 있습니다
   - "service_role" 이라고 적혀있는 키입니다
   - ⚠️ **주의**: 이 키는 매우 중요합니다! 다른 사람에게 공개하면 안 됩니다!
   - "Reveal" 버튼을 클릭하면 전체 키가 보입니다
   - 예시: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjM4OTY3MjkwLCJleHAiOjE5NTQ1NDMyOTB9.abcdefghijklmnopqrstuvwxyz1234567890`
   - 이 긴 문자열 전체를 복사하세요

### 4-2. 각 키의 역할 설명
- **Project URL**: Supabase 프로젝트의 주소입니다. 앱이 어느 Supabase 프로젝트에 연결할지 알려줍니다.
- **anon public key**: 일반 사용자가 사용하는 공개 키입니다. 로그인, 회원가입, 설문 응답 저장 등에 사용됩니다.
- **service_role key**: 관리자 권한이 있는 키입니다. 관리자 페이지에서 모든 데이터를 조회할 때 사용됩니다. ⚠️ 절대 공개하면 안 됩니다!

### 4-2. 데이터베이스 비밀번호 확인
1. "Settings" → "Database" 클릭
2. "Connection string" 섹션에서 비밀번호 확인
   - 또는 프로젝트 생성 시 입력한 비밀번호 사용

---

## 5. Streamlit Secrets 설정

### 5-1. Streamlit Cloud에서 Secrets 설정
1. https://share.streamlit.io 접속
2. 프로젝트 선택 → "Settings" → "Secrets" 클릭
3. 아래 형식으로 입력:

```toml
[SUPABASE]
URL = "여기에_4-1에서_복사한_Project_URL_붙여넣기"
ANON_KEY = "여기에_4-1에서_복사한_anon_public_key_붙여넣기"
SERVICE_ROLE_KEY = "여기에_4-1에서_복사한_service_role_key_붙여넣기"

[ADMIN]
ADMIN_EMAIL = "실제_관리자_이메일@visang.com"
```

**📝 예시:**
```toml
[SUPABASE]
URL = "https://abcdefghijklmnop.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI5MCwiZXhwIjoxOTU0NTQzMjkwfQ.abcdefghijklmnopqrstuvwxyz1234567890"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjM4OTY3MjkwLCJleHAiOjE5NTQ1NDMyOTB9.abcdefghijklmnopqrstuvwxyz1234567890"

[ADMIN]
ADMIN_EMAIL = "admin@visang.com"
```

**⚠️ 주의사항:**
- `URL`, `ANON_KEY`, `SERVICE_ROLE_KEY`는 모두 따옴표(`"`) 안에 넣어야 합니다
- 각 키는 한 줄에 모두 입력해야 합니다 (줄바꿈 없이)
- `ADMIN_EMAIL`은 실제 관리자 이메일 주소로 변경하세요

### 5-2. 로컬 테스트용 (선택사항)
프로젝트 폴더의 `.streamlit/secrets.toml` 파일에 동일한 내용 입력

---

## ✅ 완료!

이제 Supabase 설정이 완료되었습니다. 다음 단계는 Streamlit 앱 코드 수정입니다.

---

## 🔍 문제 해결

### Q: SQL 실행 시 에러가 발생해요
A: 
- 에러 메시지를 확인하세요
- "IF NOT EXISTS" 구문 때문에 이미 존재하는 테이블은 건너뜁니다
- 특정 에러가 있으면 개발자에게 문의하세요

### Q: API 키를 잃어버렸어요
A: 
- Settings → API에서 다시 확인할 수 있습니다
- service_role key는 한 번만 보여주므로 안전하게 보관하세요

### Q: 이메일 도메인 제한을 어떻게 하나요?
A: 
- Streamlit 앱 코드에서 `@visang.com` 도메인만 허용하도록 검증합니다
- Supabase에서는 모든 이메일을 허용하고, 앱 레벨에서 필터링합니다

---

## 📝 다음 단계

1. ✅ Supabase 프로젝트 생성 완료
2. ✅ 데이터베이스 테이블 생성 완료
3. ✅ API 키 확인 완료
4. ⏳ Streamlit 앱 코드 수정 (개발자가 진행)
