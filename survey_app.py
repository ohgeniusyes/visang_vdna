import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
from auth_utils import (
    init_supabase, validate_email, signup_user, login_user,
    reset_password, delete_user_account, is_admin,
    generate_reset_code, save_reset_code, verify_reset_code,
    generate_verification_code, save_verification_code, verify_email_code
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

# 직군 목록 (기타 옵션 추가)
JOB_ROLES = list(TECH_STACK.keys()) + ["기타"]

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
    
    # URL 해시 및 쿼리 파라미터 확인 (이메일 확인 콜백 처리)
    query_params = st.query_params
    
    # 1. 쿼리 파라미터로 직접 접근한 경우 (리다이렉트 후)
    if "page" in query_params:
        if query_params["page"] == "email_verified_success":
            st.session_state.current_page = "email_verified_success"
        elif query_params["page"] == "email_verified_error":
            st.session_state.current_page = "email_verified_error"
            st.session_state.email_error = query_params.get("error", "알 수 없는 오류")
            st.session_state.email_error_desc = query_params.get("desc", "")
    
    # 2. URL 해시 확인 (이메일 확인 링크 클릭 시)
    # JavaScript로 URL 해시를 읽어서 이메일 확인 상태 확인
    if "url_hash_checked" not in st.session_state:
        st.session_state.url_hash_checked = False
    
    if not st.session_state.url_hash_checked:
        # JavaScript로 URL 해시 확인 및 페이지 리다이렉트
        # Streamlit은 페이지 로드 시 한 번만 실행되므로 즉시 실행되도록 수정
        st.markdown("""
        <script>
        (function() {
            // URL 해시 확인
            const hash = window.location.hash;
            if (hash && hash.length > 1) {
                const hashContent = hash.substring(1);
                let params = {};
                
                // 해시 파싱 (형식: #access_token=xxx&type=signup 또는 #error=xxx)
                if (hashContent.includes('=')) {
                    hashContent.split('&').forEach(function(item) {
                        const parts = item.split('=');
                        if (parts.length === 2) {
                            params[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
                        }
                    });
                }
                
                const error = params.error;
                const type = params.type;
                const access_token = params.access_token;
                
                // 이메일 확인 성공 (access_token이 있거나 type=signup이고 error가 없음)
                if ((type === 'signup' && !error) || access_token) {
                    // 성공 페이지로 리다이렉트 (해시 제거)
                    const baseUrl = window.location.origin + window.location.pathname;
                    const newUrl = baseUrl + '?page=email_verified_success';
                    window.location.href = newUrl;
                } else if (error) {
                    // 오류 페이지로 리다이렉트
                    const errorCode = params.error_code || error;
                    const errorDesc = params.error_description || '';
                    const baseUrl = window.location.origin + window.location.pathname;
                    const newUrl = baseUrl + '?page=email_verified_error&error=' + encodeURIComponent(errorCode) + '&desc=' + encodeURIComponent(errorDesc);
                    window.location.href = newUrl;
                }
            }
        })();
        </script>
        """, unsafe_allow_html=True)
        st.session_state.url_hash_checked = True
    
    # 페이지별 라우팅
    if st.session_state.current_page == "email_verified_success":
        show_email_verified_success_page(supabase)
    elif st.session_state.current_page == "email_verified_error":
        show_email_verified_error_page(supabase)
    elif st.session_state.current_page == "login":
        show_login_page(supabase)
    elif st.session_state.current_page == "signup":
        show_signup_page(supabase)
    elif st.session_state.current_page == "verify_email":
        show_verify_email_page(supabase)
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

def show_email_verified_success_page(supabase):
    """이메일 확인 성공 페이지"""
    apply_common_styles()
    
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin: 2rem 0;">
        <div style="font-size: 6rem; margin-bottom: 2rem;">🎉</div>
        <h1 style="color: white; font-size: 3rem; margin-bottom: 1.5rem; font-weight: 700;">이메일 확인 완료!</h1>
        <p style="font-size: 1.5rem; color: rgba(255,255,255,0.95); margin-bottom: 3rem; line-height: 1.8;">
            축하합니다! 이메일이 성공적으로 확인되었습니다.<br>
            이제 로그인하여 설문에 참여하실 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f0f4ff; padding: 2rem; border-radius: 16px; border-left: 4px solid #2661E8; margin: 2rem 0;">
        <h3 style="color: #2661E8; margin-bottom: 1rem;">✅ 다음 단계</h3>
        <p style="color: #1a1a1a; line-height: 1.8; font-size: 1.1rem;">
            1. 아래 "로그인하러 가기" 버튼을 클릭하세요<br>
            2. 회원가입 시 입력한 이메일과 비밀번호로 로그인하세요<br>
            3. 로그인 후 설문에 참여하실 수 있습니다
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("로그인하러 가기", type="primary", use_container_width=True, key="go_to_login"):
            st.session_state.current_page = "login"
            st.session_state.email_verified_success = True
            # URL 파라미터 제거
            st.query_params.clear()
            st.rerun()

def show_email_verified_error_page(supabase):
    """이메일 확인 오류 페이지"""
    apply_common_styles()
    
    error = st.session_state.get("email_error", "알 수 없는 오류")
    error_desc = st.session_state.get("email_error_desc", "")
    
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: #fff3cd; border-radius: 20px; margin: 2rem 0; border-left: 4px solid #ffc107;">
        <div style="font-size: 5rem; margin-bottom: 2rem;">⚠️</div>
        <h1 style="color: #856404; font-size: 2.5rem; margin-bottom: 1.5rem; font-weight: 700;">이메일 확인 오류</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.error(f"**오류**: {error}")
    if error_desc:
        st.info(f"**상세**: {error_desc}")
    
    st.markdown("""
    <div style="background: #f0f4ff; padding: 2rem; border-radius: 16px; border-left: 4px solid #2661E8; margin: 2rem 0;">
        <h3 style="color: #2661E8; margin-bottom: 1rem;">💡 해결 방법</h3>
        <ul style="color: #1a1a1a; line-height: 2; font-size: 1.1rem;">
            <li>이메일 확인 링크가 만료되었을 수 있습니다. 회원가입을 다시 시도해주세요.</li>
            <li>이메일 확인 링크를 한 번만 사용할 수 있습니다. 이미 사용한 링크는 다시 사용할 수 없습니다.</li>
            <li>문제가 계속되면 관리자에게 문의해주세요.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_retry, col_login = st.columns(2)
        with col_retry:
            if st.button("회원가입 다시 시도", use_container_width=True):
                st.session_state.current_page = "signup"
                st.query_params.clear()
                if "email_error" in st.session_state:
                    del st.session_state.email_error
                if "email_error_desc" in st.session_state:
                    del st.session_state.email_error_desc
                st.rerun()
        with col_login:
            if st.button("로그인하러 가기", type="primary", use_container_width=True):
                st.session_state.current_page = "login"
                st.query_params.clear()
                if "email_error" in st.session_state:
                    del st.session_state.email_error
                if "email_error_desc" in st.session_state:
                    del st.session_state.email_error_desc
                st.rerun()

def show_login_page(supabase):
    """로그인 페이지"""
    apply_common_styles()
    
    # 이메일 확인 성공 메시지 확인
    if "email_verified_success" in st.session_state and st.session_state.email_verified_success:
        st.success("✅ 이메일이 확인되었습니다! 이제 로그인할 수 있습니다.")
        st.session_state.email_verified_success = False
    
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
                    # VERIFICATION_CODE:로 시작하면 코드 입력 페이지로 이동
                    if message.startswith("VERIFICATION_CODE:"):
                        code = message.split(":")[1]
                        st.session_state.signup_email = email
                        st.session_state.verification_code = code
                        st.session_state.current_page = "verify_email"
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("❌ Supabase 연결이 필요합니다.")
        
        if st.button("로그인으로 돌아가기", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

def show_verify_email_page(supabase):
    """이메일 확인 코드 입력 페이지"""
    apply_common_styles()
    st.title("📧 이메일 확인")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.session_state.get("signup_email", "")
        verification_code = st.session_state.get("verification_code", "")
        
        if email:
            st.success(f"✅ **{email}**로 이메일 확인 링크가 전송되었습니다!")
            st.markdown("""
            **📧 이메일 확인 방법 (권장):**
            1. 이메일함을 확인하세요
            2. "비상교육 설문" 또는 "Confirm your signup" 제목의 이메일을 찾으세요
            3. 이메일 안의 **"Confirm your mail"** 또는 **"확인 링크"** 버튼을 클릭하세요
            4. 링크를 클릭하면 자동으로 이메일이 확인되고 로그인 페이지로 이동합니다
            """)
            
            st.markdown("---")
            st.markdown("### 🔢 6자리 코드 입력 (대안)")
            st.markdown("이메일 확인 링크를 클릭하지 못한 경우, 아래에 6자리 코드를 입력할 수 있습니다.")
            
            # 개발용: 코드 표시
            if verification_code:
                st.info(f"💡 **개발용 코드**: `{verification_code}` (실제 운영에서는 이메일로만 전송됩니다)")
            
            code_input = st.text_input("6자리 인증 코드", placeholder="000000", key="verify_code_input", max_chars=6, help="이메일로 받은 6자리 코드를 입력하세요")
            
            col_code, col_space = st.columns([2, 1])
            with col_code:
                if st.button("코드 확인", type="primary", use_container_width=True):
                    if code_input and len(code_input) == 6:
                        if supabase:
                            success, message = verify_email_code(supabase, email, code_input)
                            if success:
                                st.success(message)
                                st.info("이제 로그인할 수 있습니다! 로그인 페이지에서 로그인해주세요.")
                                st.session_state.current_page = "login"
                                # 세션 상태 정리
                                if "signup_email" in st.session_state:
                                    del st.session_state.signup_email
                                if "verification_code" in st.session_state:
                                    del st.session_state.verification_code
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("❌ Supabase 연결이 필요합니다.")
                    else:
                        st.error("6자리 코드를 입력해주세요.")
            
            st.markdown("---")
            st.markdown("**💡 참고사항:**")
            st.markdown("- ✅ 이메일 확인 링크를 클릭하는 것이 가장 빠른 방법입니다")
            st.markdown("- ✅ 링크를 클릭하면 자동으로 이메일이 확인되고 로그인할 수 있습니다")
            st.markdown("- ⏰ 코드는 30분간 유효합니다")
            st.markdown("- 📧 이메일이 보이지 않으면 스팸함을 확인해보세요")
            
        else:
            st.error("이메일 정보가 없습니다. 회원가입 페이지로 돌아가세요.")
            if st.button("회원가입 페이지로 돌아가기", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
        
        st.markdown("---")
        if st.button("로그인으로 돌아가기", use_container_width=True):
            st.session_state.current_page = "login"
            if "signup_email" in st.session_state:
                del st.session_state.signup_email
            if "verification_code" in st.session_state:
                del st.session_state.verification_code
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
    """설문 페이지"""
    apply_common_styles()
    
    if not supabase:
        st.error("❌ Supabase 연결이 필요합니다.")
        return
    
    if not st.session_state.user:
        st.session_state.current_page = "login"
        st.rerun()
        return
    
    user_id = st.session_state.user.get("id", "")
    user_email = st.session_state.user.get("email", "")
    
    # 기존 응답 확인
    existing_response_data = None
    has_existing_response = False
    try:
        existing_response = supabase.table("survey_responses").select("*").eq("user_id", user_id).execute()
        if existing_response.data and len(existing_response.data) > 0:
            existing_response_data = existing_response.data[0]
            has_existing_response = True
    except Exception as e:
        has_existing_response = False
        existing_response_data = None
    
    # V-DNA 브랜딩 이미지 표시
    try:
        # 이미지 파일이 있는 경우 표시
        import os
        image_path = "visang_logo.png"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            # 이미지가 없어도 HTML로 대체 이미지 영역 표시
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem 2rem; border-radius: 20px;">
                    <h1 style="color: white; font-size: 2.5rem; margin-bottom: 1rem;">V-DNA</h1>
                    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin-bottom: 0.5rem;">비상교육 인재</p>
                    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin-bottom: 0.5rem;">데이터 기반</p>
                    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin-bottom: 1rem;">미래 조직 설계</p>
                    <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">AI in Visang</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        pass
    
    st.title("📋 IT 개발자/데이터 전문가 기술 스택 설문")
    st.markdown("---")
    
    # 사용자 정보 표시
    st.markdown(f"**로그인된 사용자**: {user_email}")
    
    if has_existing_response:
        st.info("✅ 이미 설문에 응답하셨습니다. 아래에서 수정할 수 있습니다.")
    
    st.markdown("---")
    
    # 숙련도 설명
    st.markdown("### 📌 숙련도 안내")
    st.markdown("""
    <div style="background: #f0f4ff; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2661E8; margin: 1rem 0;">
        <h4 style="color: #2661E8; margin-bottom: 1rem;">숙련도 기준</h4>
        <ul style="color: #1a1a1a; line-height: 2; font-size: 1rem;">
            <li><strong>해당없음</strong>: 해당 기술을 사용하지 않거나 경험이 없음 (기본값)</li>
            <li><strong>초급</strong>: 기본적인 사용법을 알고 있으며, 간단한 작업을 수행할 수 있음</li>
            <li><strong>중급</strong>: 일반적인 업무를 독립적으로 수행할 수 있으며, 문제 해결 능력이 있음</li>
            <li><strong>고급</strong>: 복잡한 문제를 해결할 수 있으며, 다른 사람을 가르치거나 아키텍처 설계가 가능함</li>
        </ul>
        <p style="color: #666; margin-top: 1rem; font-size: 0.95rem;">
            💡 <strong>참고:</strong> "해당없음"이 기본값이므로, 해당 기술을 사용하지 않거나 경험이 없다면 별도로 선택하지 않아도 됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 설문 폼
    with st.form("survey_form", clear_on_submit=False):
        # 이름 입력
        name = st.text_input("이름 *", placeholder="홍길동", value=existing_response_data.get("name", "") if has_existing_response and existing_response_data else "")
        
        # 직군 선택 (버튼으로 5개씩 표시)
        st.markdown("### 직군 선택 *")
        existing_job_role = existing_response_data.get("job_role", "") if has_existing_response and existing_response_data else ""
        
        # 기존 응답에서 "기타"인 경우 확인
        other_job_role = None
        if existing_job_role and existing_job_role not in JOB_ROLES:
            other_job_role = existing_job_role
            existing_job_role = "기타"
        
        # 직군을 5개씩 그룹으로 나누기
        job_roles_without_other = [r for r in JOB_ROLES if r != "기타"]
        job_roles_groups = [job_roles_without_other[i:i+5] for i in range(0, len(job_roles_without_other), 5)]
        
        # 세션 상태로 선택된 직군 관리
        if "selected_job_role" not in st.session_state:
            st.session_state.selected_job_role = existing_job_role if existing_job_role else ""
        
        # 각 그룹별로 버튼 표시
        for group in job_roles_groups:
            cols = st.columns(5)
            for idx, role in enumerate(group):
                with cols[idx]:
                    button_type = "primary" if st.session_state.selected_job_role == role else "secondary"
                    if st.button(
                        role,
                        key=f"job_role_btn_{role}",
                        use_container_width=True,
                        type=button_type
                    ):
                        st.session_state.selected_job_role = role
                        st.rerun()
        
        # "기타" 옵션
        cols_other = st.columns(5)
        with cols_other[0]:
            button_type_other = "primary" if st.session_state.selected_job_role == "기타" else "secondary"
            if st.button(
                "기타",
                key="job_role_btn_기타",
                use_container_width=True,
                type=button_type_other
            ):
                st.session_state.selected_job_role = "기타"
                st.rerun()
        
        job_role = st.session_state.selected_job_role
        
        # 선택된 직군 표시
        if job_role:
            if job_role == "기타":
                st.markdown(f"**선택된 직군**: {other_job_role if other_job_role else '기타 (입력 필요)'}")
            else:
                st.markdown(f"**선택된 직군**: {job_role}")
        
        # "기타" 옵션 입력
        if job_role == "기타":
            other_job_role = st.text_input("직군을 입력해주세요 *", placeholder="예: QA 엔지니어", value=other_job_role if other_job_role else "")
        
        st.markdown("---")
        st.markdown("### 기술 스택 및 숙련도")
        
        # 선택된 직군의 기술 스택 가져오기
        tech_stack = TECH_STACK.get(job_role, {}) if job_role != "기타" else {}
        
        # 숙련도 옵션 (4개로 변경)
        proficiency_levels = ["해당없음", "초급", "중급", "고급"]
        
        # 응답 데이터 구조 (각 기술을 개별 항목으로 저장)
        responses = {}
        
        # 각 카테고리별로 기술 표시
        for category, technologies in tech_stack.items():
            st.markdown(f"#### {category}")
            
            # 기존 응답 불러오기
            existing_responses = existing_response_data.get("responses", {}) if has_existing_response and existing_response_data else {}
            
            # 기술을 4개씩 그룹으로 나누기
            tech_groups = [technologies[i:i+4] for i in range(0, len(technologies), 4)]
            
            for tech_group in tech_groups:
                cols = st.columns(4)
                for idx, tech in enumerate(tech_group):
                    with cols[idx]:
                        st.markdown(f"**{tech}**")
                        # 기존 숙련도 가져오기
                        existing_proficiency = existing_responses.get(tech, "해당없음") if tech in existing_responses else "해당없음"
                        proficiency_index = proficiency_levels.index(existing_proficiency) if existing_proficiency in proficiency_levels else 0
                        
                        proficiency = st.selectbox(
                            "숙련도",
                            options=proficiency_levels,
                            index=proficiency_index,
                            key=f"prof_{category}_{tech}",
                            label_visibility="collapsed"
                        )
                        
                        # 응답 저장 (각 기술을 개별 항목으로)
                        responses[tech] = proficiency
        
        st.markdown("---")
        
        # 제출 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("설문 제출", type="primary", use_container_width=True)
        
        if submitted:
            # 유효성 검사
            if not name or not name.strip():
                st.error("이름을 입력해주세요.")
            elif not job_role:
                st.error("직군을 선택해주세요.")
            elif job_role == "기타" and (not other_job_role or not other_job_role.strip()):
                st.error("직군을 입력해주세요.")
            else:
                # 최종 직군 결정
                final_job_role = other_job_role.strip() if job_role == "기타" else job_role
                
                # Supabase에 저장
                try:
                    # responses는 각 기술을 개별 항목으로 저장 (기술명: 숙련도)
                    response_data = {
                        "user_id": user_id,
                        "name": name.strip(),
                        "job_role": final_job_role,
                        "responses": responses  # {"기술명": "숙련도"} 형태
                    }
                    
                    if has_existing_response and existing_response_data:
                        # 기존 응답 업데이트
                        response_id = existing_response_data["id"]
                        supabase.table("survey_responses").update(response_data).eq("id", response_id).execute()
                        st.success("✅ 설문이 수정되었습니다!")
                    else:
                        # 새 응답 생성
                        supabase.table("survey_responses").insert(response_data).execute()
                        st.success("✅ 설문이 제출되었습니다! 감사합니다.")
                    
                    # 세션 상태 초기화
                    if "selected_job_role" in st.session_state:
                        del st.session_state.selected_job_role
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"설문 제출 오류: {str(e)}")
    
    st.markdown("---")
    
    # 사용자 설정 섹션
    col_logout, col_admin, col_delete = st.columns(3)
    
    with col_logout:
        if st.button("로그아웃", key="logout_btn", use_container_width=True):
            st.session_state.user = None
            st.session_state.current_page = "login"
            st.rerun()
    
    with col_admin:
        if is_admin(user_email):
            if st.button("관리자 페이지", key="admin_btn", use_container_width=True):
                st.session_state.current_page = "admin"
                st.rerun()
    
    with col_delete:
        if st.button("회원 탈퇴", key="delete_account_btn", use_container_width=True, type="secondary"):
            st.session_state.show_delete_confirm = True
            st.rerun()
    
    # 회원 탈퇴 확인 다이얼로그
    if st.session_state.get("show_delete_confirm", False):
        st.markdown("---")
        st.warning("⚠️ **회원 탈퇴 확인**")
        st.markdown("""
        <div style="background: #fff3cd; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ffc107; margin: 1rem 0;">
            <p style="color: #856404; line-height: 1.8; font-size: 1.1rem;">
                회원 탈퇴를 진행하시겠습니까?<br>
                탈퇴 시 모든 데이터가 삭제되며 복구할 수 없습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("탈퇴하기", key="confirm_delete", type="primary", use_container_width=True):
                if supabase:
                    if user_id:
                        success, message = delete_user_account(supabase, user_id)
                        if success:
                            st.success(message)
                            st.session_state.user = None
                            st.session_state.current_page = "login"
                            if "show_delete_confirm" in st.session_state:
                                del st.session_state.show_delete_confirm
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("사용자 정보를 찾을 수 없습니다.")
                else:
                    st.error("❌ Supabase 연결이 필요합니다.")
        
        with col_cancel:
            if st.button("취소", key="cancel_delete", use_container_width=True):
                st.session_state.show_delete_confirm = False
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
