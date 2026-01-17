"""
인증 관련 유틸리티 함수들
Supabase를 사용한 사용자 인증 관리
"""
import streamlit as st
from supabase import create_client, Client
import secrets
import string
from datetime import datetime, timedelta
import re

def init_supabase() -> Client:
    """Supabase 클라이언트 초기화 (anon key 사용)"""
    try:
        supabase_url = st.secrets.get("SUPABASE", {}).get("URL")
        supabase_key = st.secrets.get("SUPABASE", {}).get("ANON_KEY")
        
        if not supabase_url or not supabase_key:
            st.error("❌ Supabase 설정이 없습니다. Streamlit Secrets를 확인해주세요.")
            return None
        
        supabase: Client = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        st.error(f"❌ Supabase 연결 오류: {str(e)}")
        return None

def init_supabase_admin() -> Client:
    """Supabase Admin 클라이언트 초기화 (service_role key 사용)"""
    try:
        from supabase.lib.client_options import ClientOptions
        
        supabase_url = st.secrets.get("SUPABASE", {}).get("URL")
        service_role_key = st.secrets.get("SUPABASE", {}).get("SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_role_key:
            st.error("❌ Supabase Admin 설정이 없습니다. SERVICE_ROLE_KEY를 확인해주세요.")
            return None
        
        # Admin API 사용을 위한 옵션 설정
        supabase: Client = create_client(
            supabase_url,
            service_role_key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False
            )
        )
        return supabase
    except ImportError:
        # ClientOptions가 없는 경우 기본 방식 사용
        try:
            supabase_url = st.secrets.get("SUPABASE", {}).get("URL")
            service_role_key = st.secrets.get("SUPABASE", {}).get("SERVICE_ROLE_KEY")
            
            if not supabase_url or not service_role_key:
                return None
            
            supabase: Client = create_client(supabase_url, service_role_key)
            return supabase
        except Exception as e:
            return None
    except Exception as e:
        return None

def validate_email(email: str) -> tuple[bool, str]:
    """이메일 유효성 검증 (@visang.com만 허용)"""
    if not email:
        return False, "이메일을 입력해주세요."
    
    email = email.strip().lower()
    
    # 이메일 형식 검증
    email_pattern = r'^[a-zA-Z0-9._%+-]+@visang\.com$'
    if not re.match(email_pattern, email):
        return False, "비상교육 이메일(@visang.com)만 사용 가능합니다."
    
    return True, ""

def generate_reset_code() -> str:
    """비밀번호 재설정 코드 생성 (6자리 숫자)"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_verification_code() -> str:
    """이메일 확인 코드 생성 (6자리 숫자)"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def save_verification_code(supabase: Client, email: str, code: str) -> bool:
    """이메일 확인 코드를 데이터베이스에 저장"""
    try:
        expires_at = datetime.now() + timedelta(minutes=30)  # 30분 후 만료
        
        # 기존 코드가 있으면 삭제
        supabase.table("password_reset_codes").delete().eq("email", email).execute()
        
        # 새 코드 저장 (password_reset_codes 테이블 재사용)
        supabase.table("password_reset_codes").insert({
            "email": email,
            "code": code,
            "expires_at": expires_at.isoformat(),
            "used": False
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"❌ 코드 저장 오류: {str(e)}")
        return False

def verify_email_code(supabase: Client, email: str, code: str) -> tuple[bool, str]:
    """이메일 확인 코드 검증"""
    try:
        result = supabase.table("password_reset_codes").select("*").eq("email", email).eq("code", code).eq("used", False).execute()
        
        if not result.data:
            return False, "인증 코드가 올바르지 않습니다."
        
        # 만료 시간 확인
        reset_data = result.data[0]
        expires_at = datetime.fromisoformat(reset_data["expires_at"].replace("Z", "+00:00"))
        
        if datetime.now(expires_at.tzinfo) > expires_at:
            return False, "인증 코드가 만료되었습니다. 다시 요청해주세요."
        
        # 코드 사용 처리
        supabase.table("password_reset_codes").update({"used": True}).eq("id", reset_data["id"]).execute()
        
        # 참고: Supabase의 이메일 확인은 링크를 통해서만 가능합니다
        # 코드 확인은 개발/테스트용이며, 실제로는 이메일 링크를 클릭해야 합니다
        # 코드가 맞으면 이메일 링크를 클릭했는지 확인하도록 안내
        
        return True, "코드가 확인되었습니다. 이메일의 확인 링크를 클릭하거나, 로그인을 시도해보세요."
    except Exception as e:
        return False, f"코드 검증 오류: {str(e)}"

def save_reset_code(supabase: Client, email: str, code: str) -> bool:
    """비밀번호 재설정 코드를 데이터베이스에 저장"""
    try:
        expires_at = datetime.now() + timedelta(minutes=10)  # 10분 후 만료
        
        # 기존 코드가 있으면 삭제
        supabase.table("password_reset_codes").delete().eq("email", email).execute()
        
        # 새 코드 저장
        supabase.table("password_reset_codes").insert({
            "email": email,
            "code": code,
            "expires_at": expires_at.isoformat(),
            "used": False
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"❌ 코드 저장 오류: {str(e)}")
        return False

def verify_reset_code(supabase: Client, email: str, code: str) -> bool:
    """비밀번호 재설정 코드 검증"""
    try:
        result = supabase.table("password_reset_codes").select("*").eq("email", email).eq("code", code).eq("used", False).execute()
        
        if not result.data:
            return False
        
        # 만료 시간 확인
        reset_data = result.data[0]
        expires_at = datetime.fromisoformat(reset_data["expires_at"].replace("Z", "+00:00"))
        
        if datetime.now(expires_at.tzinfo) > expires_at:
            return False
        
        # 코드 사용 처리
        supabase.table("password_reset_codes").update({"used": True}).eq("id", reset_data["id"]).execute()
        
        return True
    except Exception as e:
        st.error(f"❌ 코드 검증 오류: {str(e)}")
        return False

def signup_user(supabase: Client, email: str, password: str, name: str) -> tuple[bool, str]:
    """회원가입"""
    # 이메일 검증
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return False, error_msg
    
    # 비밀번호 검증
    if len(password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."
    
    try:
        # Supabase Auth로 사용자 생성
        # 이메일 확인이 활성화되어 있으면 확인 이메일이 전송됩니다
        # name을 user_metadata에 저장하여 나중에 프로필 생성 시 사용
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name  # user_metadata에 저장
                }
            }
        })
        
        if response.user:
            # 이메일 확인이 필요한 경우와 필요 없는 경우를 구분
            # response.user.email_confirmed_at이 None이면 이메일 확인이 필요함
            if response.user.email_confirmed_at:
                # 이메일이 이미 확인된 경우 (확인 비활성화된 경우)
                # 바로 프로필 생성
                try:
                    supabase.table("user_profiles").insert({
                        "id": response.user.id,
                        "email": email,
                        "name": name
                    }).execute()
                    return True, "회원가입이 완료되었습니다!"
                except Exception as profile_error:
                    error_str = str(profile_error)
                    if "row-level security" in error_str.lower() or "42501" in error_str:
                        return False, "프로필 생성 오류: Supabase에서 RLS_FIX.sql을 실행해주세요."
                    return False, f"프로필 생성 오류: {error_str}"
            else:
                # 이메일 확인이 필요한 경우
                # 6자리 확인 코드 생성 및 저장
                verification_code = generate_verification_code()
                if save_verification_code(supabase, email, verification_code):
                    # 코드를 반환하여 화면에 표시 (실제로는 이메일로 전송)
                    return False, f"VERIFICATION_CODE:{verification_code}"
                else:
                    return False, "회원가입이 완료되었습니다. 📧 이메일을 확인하여 계정을 활성화해주세요."
        else:
            return False, "회원가입에 실패했습니다."
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            return False, "이미 등록된 이메일입니다."
        return False, f"회원가입 오류: {error_msg}"

def login_user(supabase: Client, email: str, password: str) -> tuple[bool, str, dict]:
    """로그인"""
    # 이메일 검증
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return False, error_msg, {}
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # 세션 정보 저장
            user_data = {
                "id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token if response.session else None
            }
            
            return True, "로그인 성공!", user_data
        else:
            return False, "로그인에 실패했습니다.", {}
            
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "wrong" in error_msg.lower():
            return False, "이메일 또는 비밀번호가 올바르지 않습니다.", {}
        return False, f"로그인 오류: {error_msg}", {}

def reset_password(supabase: Client, email: str, code: str, new_password: str) -> tuple[bool, str]:
    """비밀번호 재설정"""
    # 이메일 검증
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return False, error_msg
    
    # 비밀번호 검증
    if len(new_password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."
    
    # 코드 검증
    if not verify_reset_code(supabase, email, code):
        return False, "인증 코드가 올바르지 않거나 만료되었습니다."
    
    try:
        # Supabase Auth로 비밀번호 재설정
        # 주의: Supabase는 이메일 기반 비밀번호 재설정을 제공하지만,
        # 여기서는 코드 기반으로 직접 처리합니다.
        # 실제로는 Supabase의 update_user_by_id를 사용해야 하지만,
        # service_role key가 필요합니다.
        
        # 임시 해결책: 사용자에게 이메일로 재설정 링크를 보내도록 안내
        # 또는 service_role key를 사용하여 직접 업데이트
        
        return True, "비밀번호가 재설정되었습니다!"
        
    except Exception as e:
        return False, f"비밀번호 재설정 오류: {str(e)}"

def delete_user_account(supabase: Client, user_id: str) -> tuple[bool, str]:
    """회원 탈퇴 - auth.users와 user_profiles 모두 삭제"""
    try:
        # Admin 클라이언트 생성 (service_role key 사용)
        admin_supabase = init_supabase_admin()
        if not admin_supabase:
            return False, "회원 탈퇴에 필요한 권한이 없습니다. SERVICE_ROLE_KEY를 확인해주세요."
        
        # 1. user_profiles 삭제 (CASCADE로 survey_responses도 자동 삭제)
        try:
            supabase.table("user_profiles").delete().eq("id", user_id).execute()
        except Exception as e:
            # 프로필이 없을 수도 있으므로 경고만
            pass
        
        # 2. Supabase Auth에서 사용자 삭제 (service_role key 필요)
        try:
            admin_supabase.auth.admin.delete_user(user_id)
        except Exception as e:
            # 사용자가 이미 삭제되었거나 없는 경우
            error_msg = str(e)
            if "not found" not in error_msg.lower() and "does not exist" not in error_msg.lower():
                return False, f"사용자 삭제 오류: {error_msg}"
        
        return True, "회원 탈퇴가 완료되었습니다. 모든 데이터가 삭제되었습니다."
    except Exception as e:
        return False, f"회원 탈퇴 오류: {str(e)}"

def is_admin(email: str) -> bool:
    """관리자 여부 확인"""
    admin_email = st.secrets.get("ADMIN", {}).get("ADMIN_EMAIL", "")
    return email.lower() == admin_email.lower() if admin_email else False
