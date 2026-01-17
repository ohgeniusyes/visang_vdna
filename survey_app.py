import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
from auth_utils import (
    init_supabase, validate_email, signup_user, login_user,
    reset_password, delete_user_account, is_admin,
    generate_reset_code, save_reset_code, verify_reset_code
)

# 페이지 설정
st.set_page_config(
    page_title="IT개발자/데이터 전문가 기술 스택 설문 | 비상교육",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheets 인증 설정 (더 이상 사용하지 않음 - Supabase로 전환)
# SCOPE = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive"
# ]

# 직군별 기술 스택 정의 (표 기준)
TECH_STACK = {
    "Backend 개발자": {
        "프로그래밍 언어": ["Java", "C#", "Python", "Go", "JavaScript", "TypeScript", "C++", "PHP", "JSP", "ASP", "SQL", "Bash", "Shell Script"],
        "프레임워크/라이브러리": ["Spring", "Spring Boot", "Thymeleaf", "JSP", "ASP.NET", ".NET", "FastAPI", "Django", "Flask", "Node.js", "Express", "Nest.js", "Koa", "Laravel", "Symfony", "CodeIgniter", "JWT", "Next.js"],
        "아키텍처": ["MSA (마이크로서비스 아키텍처)", "EDA (이벤트 기반 아키텍처)", "RESTful API", "서버리스 아키텍처"],
        "미들웨어/런타임": ["Apache", "nginx", "Tomcat", "IIS", "WebLogic", "WebSphere", "JBoss"],
        "RDB": ["MySQL", "MariaDB", "PostgreSQL", "MSSQL", "Oracle", "SQLite"],
        "NoSQL": ["MongoDB", "Redis", "DynamoDB", "Cassandra", "Elasticsearch", "OpenSearch", "Memcached"],
        "운영체제": ["Linux", "Unix", "Windows"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP", "OCI", "On-Prem", "IDC"],
        "컨테이너": ["Docker", "Kubernetes", "EKS (Elastic Kubernetes Service)", "AKS", "GKE"],
        "CI/CD": ["Jenkins", "ArgoCD", "GitHub Actions", "GitLab CI", "CI/CD 파이프라인 구축 및 운영"],
        "협업 도구": ["Jira", "Confluence", "Teams", "Slack", "Notion", "Git"],
        "프로젝트 관리": ["에자일 (Agile)", "스크럼 (Scrum)", "프로젝트 기획", "요구사항 분석", "기획 정의서 작성", "시스템 설계", "리스크 관리", "일정 관리", "교육 시스템/콘텐츠 플랫폼 기획"],
        "데이터/분석": ["데이터 파이프라인", "데이터 수집", "데이터 분석", "데이터 모델링", "데이터 시각화", "AI/ML 개발", "데이터 기반 의사결정"],
        "보안": ["웹 보안 취약점 방어", "OWASP", "보안 정책 수립"],
        "네트워크 프로토콜/Feature": ["WebSocket", "SSE", "Kafka", "RabbitMQ", "gRPC", "MQTT", "REST API", "GraphQL"]
    },
    "Frontend 개발자": {
        "프로그래밍 언어": ["JavaScript", "TypeScript", "HTML", "CSS"],
        "프레임워크/라이브러리": ["React", "Vue.js", "Vue", "Angular", "jQuery", "Next.js", "Nuxt.js", "Svelte", "Vite", "Webpack", "Babel"],
        "웹퍼블리싱": ["반응형 웹", "웹표준", "다양한 디바이스 대응", "HTML/CSS/JavaScript 능숙"],
        "운영체제": ["Windows", "macOS"],
        "클라우드": ["AWS", "GCP", "NCP", "Vercel", "Netlify"],
        "컨테이너": ["Docker (개발/배포 환경)"],
        "CI/CD": ["Jenkins", "GitHub Actions", "GitLab CI", "프론트엔드 빌드/배포 지원"],
        "UI/UX": ["UI 설계", "UX 설계", "스토리보드 작성", "프로토타이핑"],
        "프로젝트 관리": ["에자일 (Agile)", "스크럼 (Scrum)", "프로젝트 기획", "요구사항 분석", "기획 정의서 작성", "교육 시스템/콘텐츠 플랫폼 기획"],
        "네트워크 프로토콜/Feature": ["WebSocket", "REST API", "GraphQL", "WebRTC"]
    },
    "Full stack 개발자": {
        "프로그래밍 언어": ["Java", "JavaScript", "TypeScript", "Python", "SQL", "HTML", "CSS"],
        "프레임워크/라이브러리": ["Spring", "Spring Boot", "React", "Vue", "Angular", "Next.js", "Node.js", "Express"],
        "아키텍처": ["MSA (마이크로서비스 아키텍처)", "EDA (이벤트 기반 아키텍처)", "RESTful API"],
        "미들웨어/런타임": ["Apache", "nginx", "Tomcat"],
        "RDB": ["MySQL", "MSSQL", "PostgreSQL", "MariaDB", "Oracle"],
        "NoSQL": ["MongoDB", "Redis", "Elasticsearch"],
        "운영체제": ["Linux", "Unix", "Windows", "macOS"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP"],
        "컨테이너": ["Docker", "Kubernetes"],
        "CI/CD": ["Jenkins", "GitHub Actions", "GitLab CI", "ArgoCD", "CI/CD 파이프라인 구축 및 운영"],
        "협업 도구": ["Jira", "Git", "Confluence", "Teams", "Slack"],
        "프로젝트 관리": ["에자일 (Agile)", "스크럼 (Scrum)", "프로젝트 기획", "요구사항 분석"],
        "데이터/분석": ["AI/ML 개발", "데이터 분석"],
        "보안": ["웹 보안 취약점 방어", "OWASP"],
        "UI/UX": ["UI 설계", "UX 설계", "스토리보드 작성"],
        "네트워크 프로토콜/Feature": ["WebSocket", "WebRTC", "REST API", "GraphQL", "Kafka", "RabbitMQ"]
    },
    "서비스 기획자": {
        "프로그래밍 언어": ["SQL", "Python"],
        "서비스 기획": ["플랫폼 서비스 기획", "기능 설계", "서비스 구조 설계", "추천 시스템 기획", "AI 서비스 기획", "서비스 로드맵 수립"],
        "UI/UX": ["UI 설계", "UX 설계", "사용자 리서치", "사용성 검증", "스토리보드 작성", "프로토타이핑"],
        "디자인 도구": ["Figma", "Framer", "Sketch", "Adobe XD"],
        "데이터 분석": ["사용자 행동 데이터 분석", "퍼널 분석", "A/B 테스트", "트래픽 분석", "로그 분석", "데이터 수집"],
        "데이터 시각화/분석 도구": ["Tableau", "Power BI", "GA4 (Google Analytics)", "Looker Studio", "Excel"],
        "프로젝트 관리": ["JIRA", "Confluence", "프로젝트 관리", "협업", "문서 작성"],
        "기술 이해": ["웹/앱서비스 이해", "백엔드 시스템 이해", "데이터 흐름 이해", "API 이해"],
        "자격증": ["GA4", "ADsP", "DAP"]
    },
    "iOS 개발자": {
        "프로그래밍 언어": ["Swift", "Objective-C"],
        "프레임워크/라이브러리": ["UIKit", "SwiftUI", "Combine", "CoreData"],
        "RDB": ["SQLite"],
        "NoSQL": ["Realm", "Firebase"],
        "운영체제": ["macOS"],
        "클라우드": ["App Store", "CloudKit"],
        "CI/CD": ["iOS 앱 빌드/배포 지원"],
        "네트워크 프로토콜/Feature": ["REST API", "GraphQL", "WebSocket"]
    },
    "Android 개발자": {
        "프로그래밍 언어": ["Kotlin", "Java"],
        "프레임워크/라이브러리": ["Android SDK", "Jetpack Compose", "Room", "Retrofit"],
        "RDB": ["SQLite"],
        "NoSQL": ["Realm", "Firebase"],
        "운영체제": ["Windows", "macOS", "Linux"],
        "클라우드": ["Play Store", "Cloud Backend (AWS, Firebase, GCP)"],
        "CI/CD": ["Android 앱 빌드/배포 지원"],
        "네트워크 프로토콜/Feature": ["REST API", "GraphQL", "WebSocket"]
    },
    "크로스플랫폼 개발자": {
        "프로그래밍 언어": ["JavaScript", "TypeScript", "Flutter", "Dart"],
        "프레임워크/라이브러리": ["React Native", "Flutter", "Expo", "Ionic"],
        "RDB": ["SQLite"],
        "NoSQL": ["Firebase", "AsyncStorage"],
        "운영체제": ["Windows", "macOS"],
        "클라우드": ["AWS", "GCP", "Firebase"],
        "컨테이너": ["Docker (개발 환경)"],
        "CI/CD": ["크로스플랫폼 빌드/배포 지원"],
        "네트워크 프로토콜/Feature": ["REST API", "GraphQL", "WebSocket"]
    },
    "ML 엔지니어": {
        "프로그래밍 언어": ["Python", "SQL"],
        "프레임워크/라이브러리": ["TensorFlow", "PyTorch", "Transformers", "LangChain", "LlamaIndex", "Scikit-learn", "OpenCV", "Keras", "NumPy", "SciPy", "Streamlit", "RDKit"],
        "AI/ML 분야": ["자연어 처리 (NLP)", "컴퓨터 비전 (CV)", "대화형 AI (Chatbot)", "생성형 AI (Generative AI)", "LLM (Large Language Model) 활용", "예측 모델링", "분류 모델링", "최적화 모델링", "추천 시스템"],
        "미들웨어/런타임": ["Jupyter Notebook", "MLflow", "Kubeflow", "Airflow", "Spark", "Hadoop", "Kafka", "RabbitMQ", "Ray", "Dask", "FastAPI", "Flask", "Streamlit", "Docker", "Kubernetes", "Git", "DVC"],
        "RDB": ["PostgreSQL", "MySQL"],
        "NoSQL": ["Vector DB (Pinecone, Weaviate, Milvus, Qdrant, Redis)", "Elasticsearch", "OpenSearch"],
        "운영체제": ["Linux"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP", "OCI", "On-Prem"],
        "컨테이너": ["Docker", "Kubernetes"],
        "CI/CD": ["Jenkins", "ArgoCD", "데이터 파이프라인 구축 및 운영 (MLOps)", "MLOps 파이프라인 구축 및 운영"],
        "모니터링/시각화/분석 도구": ["Matplotlib", "Seaborn", "Plotly"],
        "프로젝트 관리": ["AI 프로젝트 리딩 (PL)", "모델 개발 결과 문서화", "AI/ML 서비스 설계 및 구축"],
        "네트워크 프로토콜/Feature": ["REST API", "WebSocket", "gRPC"]
    },
    "Data Engineer": {
        "프로그래밍 언어": ["Python", "Java", "SQL", "Scala"],
        "프레임워크/라이브러리": ["Apache Spark", "Airflow", "Kafka", "Hadoop", "Flink", "Storm"],
        "미들웨어/런타임": ["Docker", "Kubernetes", "Airflow", "Spark", "Hadoop", "Kafka"],
        "RDB": ["MySQL", "PostgreSQL", "MSSQL", "Oracle"],
        "NoSQL": ["MongoDB", "Cassandra", "Elasticsearch", "HBase"],
        "운영체제": ["Linux", "Unix", "Windows"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP", "On-Prem", "IDC"],
        "컨테이너": ["Docker", "Kubernetes"],
        "CI/CD": ["데이터 파이프라인 구축 및 운영", "ETL 솔루션"],
        "데이터 처리": ["정형 데이터 핸들링", "비정형 데이터 핸들링", "빅데이터 처리", "대용량 데이터 처리", "데이터 마이그레이션", "데이터 모델링"],
        "데이터 플랫폼": ["Data Lake", "Data Warehouse", "데이터 파이프라인", "데이터 포털", "데이터 카탈로그"],
        "모니터링/시각화/분석 도구": ["Grafana", "Prometheus", "Kibana"],
        "네트워크 프로토콜/Feature": ["Kafka", "REST API", "gRPC"]
    },
    "Data Scientist": {
        "프로그래밍 언어": ["Python", "R", "SQL"],
        "프레임워크/라이브러리": ["pandas", "scikit-learn", "PyTorch", "TensorFlow", "Keras", "NumPy", "SciPy", "statsmodels", "XGBoost"],
        "AI/ML 분야": ["예측 모델링", "분류 모델링", "최적화 모델링", "추천 시스템", "모델 성능 평가 및 최적화"],
        "데이터 처리": ["데이터 전처리", "피처 엔지니어링", "데이터 가공", "빅데이터 분석 및 처리", "Hadoop", "Spark"],
        "RDB": ["MySQL", "PostgreSQL", "BigQuery", "Snowflake"],
        "NoSQL": ["MongoDB", "Redis", "Elasticsearch", "OpenSearch"],
        "운영체제": ["Linux", "Windows"],
        "클라우드": ["AWS", "GCP", "Azure", "NCP", "On-Prem", "IDC"],
        "컨테이너": ["Docker"],
        "CI/CD": ["머신러닝 모델 개발 및 배포 (MLOps)", "MLOps 파이프라인 구축 및 운영", "MLflow", "Kubeflow"],
        "AI/ML 인프라": ["AI/ML 인프라 생성 및 관리", "AWS 기반 AI/ML 인프라", "클라우드 환경 모델 배포 및 운영", "분산 컴퓨팅"],
        "모니터링/시각화/분석 도구": ["Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI", "Looker Studio", "Google Data Studio", "Excel"],
        "협업 도구": ["Jira", "Confluence", "Teams"],
        "네트워크 프로토콜/Feature": ["REST API"]
    },
    "Data Analyst": {
        "프로그래밍 언어": ["SQL", "Python"],
        "프레임워크/라이브러리": ["pandas", "NumPy", "Matplotlib", "Seaborn"],
        "RDB": ["MySQL", "PostgreSQL", "BigQuery", "Snowflake", "Redshift"],
        "NoSQL": ["MongoDB", "Cassandra", "Elasticsearch", "OpenSearch"],
        "운영체제": ["Windows", "macOS"],
        "클라우드": ["AWS", "GCP", "Azure", "NCP", "On-Prem", "IDC"],
        "CI/CD": ["데이터 분석 보고서 자동화"],
        "모니터링/시각화/분석 도구": ["Tableau", "Power BI", "Looker Studio", "Google Data Studio", "Excel"],
        "네트워크 프로토콜/Feature": ["REST API"]
    },
    "People Analyst": {
        "프로그래밍 언어": ["SQL", "Python", "R"],
        "프레임워크/라이브러리": ["pandas", "statsmodels", "scikit-learn", "ggplot2", "dplyr"],
        "RDB": ["Oracle", "MSSQL", "Data Warehouse"],
        "운영체제": ["Windows", "macOS"],
        "클라우드": ["On-Prem", "Cloud (AWS, Azure)", "NCP", "IDC"],
        "CI/CD": ["인사 데이터 분석 및 시각화 (MLOps)"],
        "모니터링/시각화/분석 도구": ["Tableau", "Power BI", "Looker Studio", "Google Data Studio", "Excel"],
        "네트워크 프로토콜/Feature": ["REST API"]
    },
    "DevOps": {
        "프로그래밍 언어": ["Python", "Go", "Bash", "Shell Script", "YAML", "Groovy", "PowerShell"],
        "프레임워크/라이브러리": ["Jenkins", "GitLab Actions", "GitHub Actions", "ArgoCD", "Ansible", "CircleCI", "Travis CI", "Terraform", "Spinnaker"],
        "미들웨어/런타임": ["Apache", "nginx", "Tomcat", "IIS", "WebLogic", "WebSphere"],
        "RDB": ["PostgreSQL", "MySQL", "MSSQL", "Oracle"],
        "NoSQL": ["Redis", "Elasticsearch", "OpenSearch"],
        "운영체제": ["Linux", "Unix", "Windows"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP", "OCI", "On-Prem", "IDC"],
        "컨테이너": ["Docker", "Kubernetes", "Rancher"],
        "CI/CD": ["Jenkins", "ArgoCD", "GitHub Actions", "GitLab CI", "CI/CD 파이프라인 구축 및 운영"],
        "모니터링/시각화/분석 도구": ["Grafana", "Prometheus", "ZABBIX", "Scouter", "Kibana", "CloudWatch", "Datadog", "New Relic", "Nagios"],
        "보안/인증": ["ISMS", "CSAP", "방화벽 (F/W)", "VPN", "접근통제", "WAF", "IDS/IPS", "보안장비 운영"],
        "가상화/인프라": ["VDI", "VMware", "Hyper-V", "KVM"],
        "네트워크 프로토콜/Feature": ["HTTP/HTTPS", "SSH", "SCP", "SFTP", "DNS", "DHCP", "NTP", "SNMP", "VPN", "Load Balancer", "Firewall", "CDN"]
    },
    "MLOps": {
        "프로그래밍 언어": ["Python", "SQL", "R", "Bash", "Shell Script"],
        "프레임워크/라이브러리": ["MLflow", "Kubeflow", "Airflow", "DVC", "Weights & Biases", "Neptune.ai", "ClearML", "Sagemaker", "Vertex AI", "Argo Workflow"],
        "모델 서빙": ["Triton Inference Server", "TorchServe", "vLLM", "TensorFlow Serving", "ONNX Runtime"],
        "RDB": ["SQLite", "MySQL", "PostgreSQL"],
        "NoSQL": ["Redis", "MongoDB", "Elasticsearch", "OpenSearch", "Feature Store (Feast, Tecton)"],
        "운영체제": ["Linux", "Unix", "Windows"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP", "Databricks", "On-Prem"],
        "컨테이너": ["Docker", "Kubernetes", "KubeFlow", "Helm", "Kustomize"],
        "CI/CD": ["Jenkins", "ArgoCD", "GitOps", "Helm", "Kustomize", "ML 파이프라인 구축 및 운영", "모델 배포 자동화"],
        "인프라/자동화": ["Terraform", "IaC (Infrastructure as Code)", "GPU 클러스터", "GPU 자원 스케줄링", "Nvidia Operator", "GPU Sharing"],
        "모니터링/시각화/분석 도구": ["MLflow", "Kubeflow", "Databricks", "Weights & Biases", "TensorBoard", "Grafana", "Prometheus", "데이터 드리프트 탐지", "모델 성능 모니터링", "자동 재학습"],
        "네트워크 프로토콜/Feature": ["REST API", "gRPC", "Model Serving API"]
    },
    "Game 개발자": {
        "프로그래밍 언어": ["C#", "C++", "Java"],
        "프레임워크/라이브러리": ["Unity", "Unreal Engine", "Cocos2d-x", "Godot"],
        "RDB": ["MySQL", "MSSQL"],
        "NoSQL": ["Redis", "Firebase"],
        "운영체제": ["Windows"],
        "클라우드": ["On-Prem", "Cloud (AWS, GCP)", "NCP", "Steam", "Epic Games Store", "IDC"],
        "CI/CD": ["게임 빌드/배포 자동화"],
        "네트워크 프로토콜/Feature": ["WebSocket", "UDP", "Photon", "Mirror"]
    },
    "보안 엔지니어": {
        "프로그래밍 언어": ["Python", "C", "C++", "Java", "Go", "PowerShell", "SQL"],
        "프레임워크/라이브러리": ["Metasploit", "Nmap", "Wireshark", "Burp Suite", "OWASP ZAP", "Nessus", "OpenVAS", "Snort", "Suricata", "Zeek", "OSSEC", "Wazuh"],
        "RDB": ["MySQL", "PostgreSQL", "MSSQL"],
        "NoSQL": ["Redis", "Elasticsearch", "OpenSearch"],
        "운영체제": ["Linux", "Unix", "Windows"],
        "클라우드": ["AWS", "Azure", "GCP", "NCP", "On-Prem", "IDC"],
        "컨테이너": ["Docker", "Kubernetes"],
        "CI/CD": ["보안 테스트/취약점 자동화"],
        "모니터링/시각화/분석 도구": ["Splunk", "ELK Stack", "Grafana", "Prometheus", "SIEM", "SOAR"],
        "보안/인증": ["ISMS", "ISMS-P", "CSAP", "ISO27001", "방화벽", "WAF", "IPS", "IDS", "침해사고 대응", "취약점 관리"],
        "보안 표준/프레임워크": ["OWASP Top 10", "CWE", "CVE", "보안 아키텍처 설계"],
        "네트워크 프로토콜/Feature": ["TCP/IP", "HTTP/HTTPS", "TLS/SSL", "IPSec", "VPN", "IDS/IPS", "Firewall", "WAF", "DDoS Protection", "OSI 7계층"]
    }
}

# 직군 목록
JOB_ROLES = list(TECH_STACK.keys())

# Google Sheets 함수들 (더 이상 사용하지 않음 - Supabase로 전환)
# def init_google_sheets(credentials_dict, spreadsheet_id):
#     """Google Sheets 초기화"""
#     pass
# 
# def save_to_sheets(sheet, data):
#     """Google Sheets에 데이터 저장"""
#     pass

def main():
    # 페이지 라우팅: 세션 상태로 현재 페이지 관리
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Supabase 초기화
    supabase = init_supabase()
    
    # 페이지별 라우팅
    if st.session_state.current_page == "login":
        show_login_page(supabase)
    elif st.session_state.current_page == "signup":
        show_signup_page(supabase)
    elif st.session_state.current_page == "reset_password":
        show_reset_password_page(supabase)
    elif st.session_state.current_page == "survey":
        if st.session_state.user:
            show_survey_page(supabase)
        else:
            st.session_state.current_page = "login"
            st.rerun()
    elif st.session_state.current_page == "admin":
        if st.session_state.user and is_admin(st.session_state.user.get("email", "")):
            show_admin_page(supabase)
        else:
            st.error("❌ 관리자만 접근할 수 있습니다.")
            st.session_state.current_page = "login"
            st.rerun()
    else:
        st.session_state.current_page = "login"
        st.rerun()

def apply_common_styles():
    """공통 CSS 스타일 적용"""
    # CSS는 각 페이지에서 필요시 적용
    pass

def show_login_page(supabase):
    """로그인 페이지"""
    apply_common_styles()
    st.title("🔐 로그인")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("이메일", placeholder="example@visang.com", key="login_email")
        password = st.text_input("비밀번호", type="password", key="login_password")
        
        col_login, col_signup = st.columns(2)
        with col_login:
            if st.button("로그인", type="primary", use_container_width=True):
                if supabase:
                    success, message, user_data = login_user(supabase, email, password)
                    if success:
                        st.session_state.user = user_data
                        st.session_state.current_page = "survey"
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Supabase 연결이 필요합니다.")
        
        with col_signup:
            if st.button("회원가입", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
        
        if st.button("비밀번호 재설정", use_container_width=True):
            st.session_state.current_page = "reset_password"
            st.rerun()

def show_signup_page(supabase):
    """회원가입 페이지"""
    apply_common_styles()
    st.title("📝 회원가입")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("이메일", placeholder="example@visang.com", key="signup_email")
        password = st.text_input("비밀번호 (8자 이상)", type="password", key="signup_password")
        password_confirm = st.text_input("비밀번호 확인", type="password", key="signup_password_confirm")
        name = st.text_input("이름", key="signup_name")
        
        if st.button("회원가입", type="primary", use_container_width=True):
            if password != password_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
            elif supabase:
                success, message = signup_user(supabase, email, password, name)
                if success:
                    st.success(message)
                    st.info("로그인 페이지로 이동합니다...")
                    st.session_state.current_page = "login"
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("❌ Supabase 연결이 필요합니다.")
        
        if st.button("로그인으로 돌아가기", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

def show_reset_password_page(supabase):
    """비밀번호 재설정 페이지"""
    apply_common_styles()
    st.title("🔑 비밀번호 재설정")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("이메일", placeholder="example@visang.com", key="reset_email")
        
        if "reset_code_sent" not in st.session_state:
            st.session_state.reset_code_sent = False
        
        if not st.session_state.reset_code_sent:
            if st.button("인증 코드 전송", type="primary", use_container_width=True):
                if supabase:
                    is_valid, error_msg = validate_email(email)
                    if is_valid:
                        code = generate_reset_code()
                        if save_reset_code(supabase, email, code):
                            # 실제로는 이메일로 코드를 보내야 하지만, 여기서는 화면에 표시
                            st.session_state.reset_code = code
                            st.session_state.reset_code_sent = True
                            st.success(f"인증 코드가 생성되었습니다: {code}")
                            st.info("⚠️ 실제 운영 환경에서는 이메일로 코드가 전송됩니다.")
                        else:
                            st.error("인증 코드 생성에 실패했습니다.")
                    else:
                        st.error(error_msg)
                else:
                    st.error("❌ Supabase 연결이 필요합니다.")
        else:
            code = st.text_input("인증 코드", key="reset_code_input")
            new_password = st.text_input("새 비밀번호 (8자 이상)", type="password", key="reset_new_password")
            new_password_confirm = st.text_input("새 비밀번호 확인", type="password", key="reset_new_password_confirm")
            
            if st.button("비밀번호 재설정", type="primary", use_container_width=True):
                if new_password != new_password_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif supabase:
                    success, message = reset_password(supabase, email, code, new_password)
                    if success:
                        st.success(message)
                        st.session_state.current_page = "login"
                        st.session_state.reset_code_sent = False
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Supabase 연결이 필요합니다.")
        
        if st.button("로그인으로 돌아가기", use_container_width=True):
            st.session_state.current_page = "login"
            st.session_state.reset_code_sent = False
            st.rerun()

def show_survey_page(supabase):
    """설문 페이지 - 기존 코드는 나중에 통합 예정"""
    apply_common_styles()
    st.info("⚠️ 설문 페이지는 현재 개발 중입니다. 기존 설문 코드를 Supabase로 전환 중입니다.")
    st.markdown("---")
    
    # 로그아웃 버튼
    if st.button("로그아웃", key="logout_btn"):
        st.session_state.user = None
        st.session_state.current_page = "login"
        st.rerun()
    
    # 관리자 버튼
    if st.session_state.user and is_admin(st.session_state.user.get("email", "")):
        if st.button("관리자 페이지", key="admin_btn"):
            st.session_state.current_page = "admin"
            st.rerun()

def show_admin_page(supabase):
    """관리자 페이지 (엑셀 다운로드 기능)"""
    apply_common_styles()
    st.title("👨‍💼 관리자 페이지")
    st.markdown("---")
    
    if not supabase:
        st.error("❌ Supabase 연결이 필요합니다.")
        return
    
    # 설문 응답 조회
    try:
        from io import BytesIO
        responses = supabase.table("survey_responses").select("*").order("created_at", desc=True).execute()
        
        if responses.data:
            st.subheader(f"📊 총 {len(responses.data)}개의 응답")
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(responses.data)
            
            # 엑셀 다운로드 버튼
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Survey Responses')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 엑셀로 다운로드",
                data=excel_data,
                file_name=f"survey_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # 데이터 표시
            st.dataframe(df, use_container_width=True)
        else:
            st.info("아직 응답이 없습니다.")
    except Exception as e:
        st.error(f"❌ 데이터 조회 오류: {str(e)}")
    
    if st.button("로그아웃"):
        st.session_state.user = None
        st.session_state.current_page = "login"
        st.rerun()

if __name__ == "__main__":
    main()
