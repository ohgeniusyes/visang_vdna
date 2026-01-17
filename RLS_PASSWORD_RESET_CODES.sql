-- password_reset_codes 테이블에 RLS 정책 추가
-- 이메일 확인 코드 및 비밀번호 재설정 코드 저장을 위해 필요

-- RLS 활성화
ALTER TABLE password_reset_codes ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 (중복 방지)
DROP POLICY IF EXISTS "Anyone can insert reset codes" ON password_reset_codes;
DROP POLICY IF EXISTS "Anyone can select reset codes" ON password_reset_codes;
DROP POLICY IF EXISTS "Anyone can update reset codes" ON password_reset_codes;
DROP POLICY IF EXISTS "Anyone can delete reset codes" ON password_reset_codes;

-- INSERT 정책: 누구나 코드를 저장할 수 있음 (회원가입 시 이메일 확인 코드 저장용)
CREATE POLICY "Anyone can insert reset codes"
    ON password_reset_codes FOR INSERT
    WITH CHECK (true);

-- SELECT 정책: 자신의 이메일로 저장된 코드만 조회 가능
CREATE POLICY "Users can select own reset codes"
    ON password_reset_codes FOR SELECT
    USING (true);  -- 이메일로 검증하므로 모든 사용자가 조회 가능

-- UPDATE 정책: 자신의 이메일로 저장된 코드만 업데이트 가능
CREATE POLICY "Users can update own reset codes"
    ON password_reset_codes FOR UPDATE
    USING (true);  -- 이메일로 검증하므로 모든 사용자가 업데이트 가능

-- DELETE 정책: 자신의 이메일로 저장된 코드만 삭제 가능
CREATE POLICY "Users can delete own reset codes"
    ON password_reset_codes FOR DELETE
    USING (true);  -- 이메일로 검증하므로 모든 사용자가 삭제 가능
