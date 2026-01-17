-- user_profiles 테이블에 name 컬럼 추가 (기존 테이블이 있는 경우)
-- 이미 name 컬럼이 있으면 에러가 나지만 무시해도 됩니다

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS name TEXT;

-- 참고: 이미 테이블을 만든 경우에만 이 SQL을 실행하세요.
-- 새로 테이블을 만드는 경우 SUPABASE_SETUP_GUIDE.md의 SQL에 이미 name 컬럼이 포함되어 있습니다.
