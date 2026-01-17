-- user_profiles 테이블에 INSERT 정책 추가
-- 회원가입 시 사용자가 자신의 프로필을 생성할 수 있도록 설정

-- 기존 정책 확인 후 필요시 삭제 (중복 방지)
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;

-- INSERT 정책 추가: 사용자가 자신의 프로필을 생성할 수 있음
CREATE POLICY "Users can insert own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- 참고: 이 정책은 회원가입 시 Supabase Auth에서 생성된 사용자 ID와
-- user_profiles에 삽입되는 id가 일치할 때만 INSERT를 허용합니다.
