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

-- 이메일 확인 후 자동으로 프로필 생성하는 함수
-- user_metadata에서 name을 읽어서 프로필에 저장
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    user_name TEXT;
BEGIN
    -- 이메일이 확인된 경우에만 프로필 생성
    IF NEW.email_confirmed_at IS NOT NULL THEN
        -- user_metadata에서 name 추출 (JSONB 형식)
        user_name := COALESCE(NEW.raw_user_meta_data->>'name', '');
        
        INSERT INTO public.user_profiles (id, email, name)
        VALUES (NEW.id, NEW.email, user_name)
        ON CONFLICT (id) DO UPDATE
        SET email = EXCLUDED.email,
            name = COALESCE(EXCLUDED.name, user_profiles.name);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거: auth.users 테이블에 이메일 확인 시 프로필 자동 생성
DROP TRIGGER IF EXISTS on_auth_user_confirmed ON auth.users;
CREATE TRIGGER on_auth_user_confirmed
    AFTER UPDATE OF email_confirmed_at ON auth.users
    FOR EACH ROW
    WHEN (NEW.email_confirmed_at IS NOT NULL AND OLD.email_confirmed_at IS NULL)
    EXECUTE FUNCTION public.handle_new_user();
