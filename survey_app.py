import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import json
import base64

# 페이지 설정
st.set_page_config(
    page_title="IT개발자/데이터 전문가 기술 스택 설문 | 비상교육",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheets 인증 설정
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

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

def init_google_sheets(credentials_dict, spreadsheet_id):
    """Google Sheets 초기화"""
    try:
        # 딕셔너리인지 확인
        if not isinstance(credentials_dict, dict):
            st.error(f"❌ 잘못된 형식: 딕셔너리가 필요합니다. 현재 타입: {type(credentials_dict).__name__}")
            return None
        
        # 필수 키 확인
        required_keys = ["type", "project_id", "private_key", "client_email"]
        missing_keys = [key for key in required_keys if key not in credentials_dict]
        if missing_keys:
            st.error(f"❌ 필수 키가 누락되었습니다: {missing_keys}")
            return None
        
        # Google 인증
        creds = Credentials.from_service_account_info(credentials_dict, scopes=SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id)
        return sheet
    except Exception as e:
        st.error(f"❌ Google Sheets 연결 오류: {str(e)}")
        st.info("💡 **확인 사항**:\n1. Google Sheets에 서비스 계정 이메일이 공유되어 있는지 확인\n2. 서비스 계정에 '편집자' 권한이 있는지 확인")
        return None

def save_to_sheets(sheet, data):
    """Google Sheets에 데이터 저장"""
    try:
        worksheet = sheet.sheet1
        
        # 데이터를 문자열로 변환
        formatted_data = {}
        for key, value in data.items():
            if key in ["이름", "직군"]:
                formatted_data[key] = value
            elif isinstance(value, dict):
                # 딕셔너리 형태: {기술명: 수준}
                tech_list = [f"{tech} ({level})" for tech, level in value.items()]
                formatted_data[key] = ", ".join(tech_list) if tech_list else ""
            elif isinstance(value, list):
                formatted_data[key] = ", ".join(value) if value else ""
            else:
                formatted_data[key] = str(value) if value else ""
        
        # 헤더가 없으면 추가
        if worksheet.row_count == 0:
            headers = ["타임스탬프", "이름", "직군"] + [k for k in formatted_data.keys() if k not in ["이름", "직군"]]
            worksheet.append_row(headers)
        else:
            # 기존 헤더 읽기
            headers = worksheet.row_values(1)
            # 새로운 헤더 추가
            existing_headers = set(headers)
            new_headers = [k for k in formatted_data.keys() if k not in ["이름", "직군"] and k not in existing_headers]
            if new_headers:
                headers.extend(new_headers)
                worksheet.insert_row(headers, 1)
                worksheet.delete_rows(2)
        
        # 데이터 추가
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            formatted_data.get("이름", ""),
            formatted_data.get("직군", "")
        ]
        
        # 나머지 카테고리 데이터 추가
        for key in headers[3:]:  # 타임스탬프, 이름, 직군 제외
            value = formatted_data.get(key, "")
            row.append(value)
        
        worksheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"데이터 저장 오류: {str(e)}")
        return False

def main():
    # 비상교육 웹사이트 스타일 CSS 적용
    st.markdown("""
    <style>
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 전체 배경 - 깔끔한 흰색 */
    .stApp {
        background: #ffffff;
        background-attachment: fixed;
    }
    
    /* 흐르는 텍스트 애니메이션 */
    @keyframes slide {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    
    .marquee {
        display: flex;
        overflow: hidden;
        white-space: nowrap;
    }
    
    .marquee-content {
        display: inline-flex;
        animation: slide 20s linear infinite;
    }
    
    /* 메인 컨테이너 - 전체 너비, 패딩 제거 */
    .main .block-container {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
        padding-bottom: 0;
        max-width: 100%;
    }
    
    /* 헤더 스타일 - 흰색 배경 */
    .visang-header {
        background: white;
        padding: 1.5rem 4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e0e0e0;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        width: 100%;
        box-sizing: border-box;
    }
    
    .visang-header-left {
        display: flex;
        align-items: center;
        flex: 0 0 auto;
    }
    
    .visang-header-right {
        display: flex;
        align-items: center;
        flex: 0 0 auto;
        color: #1a1a1a;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .visang-logo {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2661E8;
        letter-spacing: -0.5px;
    }
    
    /* 히어로 섹션 */
    .hero-section {
        background: #ffffff;
        padding: 4rem 4rem 3rem 4rem;
        min-height: auto;
        display: flex;
        align-items: center;
        position: relative;
    }
    
    .hero-content {
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
    }
    
    .hero-text {
        color: #1a1a1a;
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.3;
        margin-bottom: 1.5rem;
        letter-spacing: -1.5px;
    }
    
    .hero-subtext {
        color: #666;
        font-size: 1.5rem;
        font-weight: 400;
        line-height: 1.8;
        margin-bottom: 2rem;
        letter-spacing: -0.3px;
    }
    
    /* 설문 컨테이너 - 깔끔한 흰색 */
    .survey-container {
        background: #ffffff;
        border-radius: 0;
        padding: 3rem 5rem;
        margin: 0 auto;
        max-width: 1200px;
        position: relative;
        z-index: 10;
        border: none;
    }
    
    /* 기술 수준 버튼 스타일 */
    .level-buttons {
        display: flex;
        gap: 0.75rem;
        margin-top: 0.5rem;
    }
    
    .level-btn {
        flex: 1;
        padding: 0.75rem 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        background: white;
        color: #666;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .level-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .level-btn.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    }
    
    .level-btn.입문.selected {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-color: #f5576c;
        box-shadow: 0 4px 16px rgba(245, 87, 108, 0.4);
    }
    
    .level-btn.초급.selected {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-color: #4facfe;
        box-shadow: 0 4px 16px rgba(79, 172, 254, 0.4);
    }
    
    .level-btn.중급.selected {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        border-color: #43e97b;
        box-shadow: 0 4px 16px rgba(67, 233, 123, 0.4);
    }
    
    .level-btn.고급.selected {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-color: #fa709a;
        box-shadow: 0 4px 16px rgba(250, 112, 154, 0.4);
    }
    
    /* 기술 수준 선택 버튼 스타일 */
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"] {
        font-size: 0.75rem !important;
        padding: 0.4rem 0.5rem !important;
        min-height: auto !important;
    }
    
    /* 해당없음 버튼이 선택된 경우 (기본값) - 회색 그라데이션 */
    button[data-testid="baseButton-primary"][aria-label*="_level_해당없음"] {
        background: linear-gradient(135deg, #b0b0b0 0%, #d0d0d0 100%) !important;
        border: 2px solid #999 !important;
        color: #333 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
    }
    
    /* 모든 primary 버튼 중 해당없음 텍스트를 포함하는 버튼 */
    button[data-testid="baseButton-primary"] {
        position: relative;
    }
    
    /* 입문 버튼이 선택된 경우 */
    button[data-testid="baseButton-primary"][aria-label*="_level_입문"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* 초급 버튼이 선택된 경우 */
    button[data-testid="baseButton-primary"][aria-label*="_level_초급"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* 중급 버튼이 선택된 경우 */
    button[data-testid="baseButton-primary"][aria-label*="_level_중급"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* 고급 버튼이 선택된 경우 */
    button[data-testid="baseButton-primary"][aria-label*="_level_고급"] {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* 제목 스타일 */
    h1 {
        color: #2661E8;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }
    
    h3 {
        color: #1a1a1a;
        font-size: 1.6rem;
        font-weight: 600;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #2661E8;
    }
    
    h4 {
        color: #1a1a1a;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2661E8;
        box-shadow: 0 0 0 4px rgba(38, 97, 232, 0.1);
        outline: none;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #2661E8;
        box-shadow: 0 0 0 4px rgba(38, 97, 232, 0.1);
        outline: none;
    }
    
    /* Textarea 스타일 */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #2661E8;
        box-shadow: 0 0 0 4px rgba(38, 97, 232, 0.1);
        outline: none;
    }
    
    /* 버튼 스타일 - 흰색 둥근 버튼 (비상 스타일) */
    .stButton > button {
        background: white;
        color: #2661E8;
        border: 2px solid white;
        border-radius: 50px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: #f8f9fa;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* 제출 버튼 - 파란색 */
    .submit-button > button {
        background: #2661E8;
        color: white;
        border: 2px solid #2661E8;
        border-radius: 50px;
        padding: 1.2rem 3rem;
        font-weight: 600;
        font-size: 1.2rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(38, 97, 232, 0.3);
    }
    
    .submit-button > button:hover {
        background: #1e4fc7;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(38, 97, 232, 0.4);
    }
    
    /* 멀티셀렉트 스타일 */
    .stMultiSelect > div > div {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: #2661E8;
        box-shadow: 0 0 0 4px rgba(38, 97, 232, 0.1);
    }
    
    /* 정보 박스 */
    .stInfo {
        background: #f0f4ff;
        border-left: 4px solid #2661E8;
        border-radius: 12px;
        padding: 1.5rem;
        color: #1a1a1a;
    }
    
    .stWarning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 12px;
        padding: 1.5rem;
        color: #856404;
    }
    
    .stSuccess {
        background: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 12px;
        padding: 2rem;
        color: #155724;
        text-align: center;
    }
    
    /* 구분선 */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
        margin: 3rem 0;
    }
    
    /* 라벨 */
    label {
        color: #1a1a1a;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2661E8;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1e4fc7;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 비상 브랜드 헤더
    import os
    if os.path.exists("visang_logo.png"):
        with open("visang_logo.png", "rb") as f:
            logo_data = f.read()
            logo_base64 = base64.b64encode(logo_data).decode()
            logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="visang" style="height: 2.5rem; width: auto; display: block;">'
    else:
        logo_html = '<div class="visang-logo" style="font-size: 1.8rem; font-weight: 600; color: #23a6d5; letter-spacing: -0.5px;">visang</div>'
    
    st.markdown(f"""
    <div class="visang-header">
        <div class="visang-header-left">
            {logo_html}
        </div>
        <div class="visang-header-right">
            IT개발자/데이터 전문가 기술 스택 설문
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 히어로 섹션
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-text">안녕하세요, CP님.<br>설문에 응해주셔서 감사합니다.</div>
            <div class="hero-subtext">비상교육 IT/Data 분야 전문가분들의 기술 스택을 체계적으로 파악하여<br>조직 내 기술 역량에 대한 이해도를 제고하고자, 관련 설문을 시작하겠습니다.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    if st.session_state.submitted:
        st.markdown("""
        <div style="background: #d4edda; 
                    padding: 4rem 3rem; 
                    border-radius: 20px; 
                    border-left: 4px solid #28a745;
                    text-align: center;
                    margin: 2rem 0;">
            <h2 style="color: #155724; margin: 0 0 1.5rem 0; font-size: 2.2rem; font-weight: 700;">✅ 설문이 성공적으로 제출되었습니다!</h2>
            <p style="color: #155724; font-size: 1.3rem; margin: 0 0 2rem 0;">감사합니다. 🙏</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 새 설문 작성하기", type="primary", use_container_width=True):
                st.session_state.submitted = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)  # 설문 컨테이너 닫기
        return
    
    # Google Sheets 초기화 (연결 실패해도 설문은 진행 가능)
    sheet = None
    sheets_error = None
    
    try:
        if 'GOOGLE_SHEETS_CREDENTIALS' in st.secrets and 'SPREADSHEET_ID' in st.secrets:
            creds_value = st.secrets['GOOGLE_SHEETS_CREDENTIALS']
            spreadsheet_id = st.secrets['SPREADSHEET_ID']
            
            # Secrets에서 가져온 값이 딕셔너리인 경우 (TOML이 자동 파싱한 경우)
            if isinstance(creds_value, dict):
                # 이미 딕셔너리이므로 그대로 사용
                credentials_dict = creds_value
            elif isinstance(creds_value, str):
                # 문자열인 경우 JSON 파싱
                try:
                    credentials_dict = json.loads(creds_value.strip())
                except json.JSONDecodeError:
                    sheets_error = "JSON 파싱 실패: Secrets의 GOOGLE_SHEETS_CREDENTIALS 형식을 확인해주세요."
            else:
                sheets_error = f"잘못된 형식: {type(creds_value).__name__}"
            
            if sheets_error is None:
                sheet = init_google_sheets(credentials_dict, spreadsheet_id)
                if sheet is None:
                    sheets_error = "Google Sheets 연결 실패"
        else:
            sheets_error = "Secrets에 GOOGLE_SHEETS_CREDENTIALS 또는 SPREADSHEET_ID가 설정되지 않았습니다."
    except Exception as e:
        sheets_error = f"설정 오류: {str(e)}"
    
    # Google Sheets 연결 실패 시 경고만 표시 (설문은 계속 진행)
    if sheets_error:
        st.markdown(f"""
        <div style="background: #fff3cd; 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    border-left: 4px solid #ffc107;
                    margin-bottom: 2rem;">
            <strong style="color: #856404; font-size: 1.1rem;">⚠️ Google Sheets 연결 오류:</strong> 
            <span style="color: #856404;">{sheets_error}</span><br>
            <small style="color: #856404;">💡 참고: 설문은 진행할 수 있지만, 응답이 저장되지 않을 수 있습니다.</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 설문 컨테이너 시작 (안내 메시지와 함께)
    st.markdown('<div class="survey-container">', unsafe_allow_html=True)
    
    # 안내 메시지
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                padding: 2rem; 
                border-radius: 16px; 
                border: 2px solid rgba(102, 126, 234, 0.3);
                margin-bottom: 3rem;
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);">
        <h4 style="color: #667eea; margin: 0 0 1rem 0; font-size: 1.3rem; font-weight: 700;">💡 안내</h4>
        <p style="margin: 0; color: #1a1a1a; line-height: 1.8; font-size: 1.05rem;">
            본 설문은 비상교육 IT 개발자들의 기술력을 파악하기 위한 것입니다.<br>
            성실하게 응답해주시면 감사하겠습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 이름 입력
    st.markdown("### 0️⃣ 이름 입력")
    name = st.text_input(
        "귀하의 이름을 입력해주세요:",
        key="name",
        placeholder="홍길동",
        label_visibility="visible"
    )
    
    if not name or name.strip() == "":
        st.info("👆 위에 이름을 입력해주세요.")
        st.stop()
    
    st.markdown("---")
    
    # 직군 선택
    st.markdown("### 1️⃣ 직군 선택")
    role_options = [""] + JOB_ROLES + ["기타"]
    selected_role = st.selectbox(
        "귀하의 직군을 선택해주세요:",
        options=role_options,
        key="job_role",
        label_visibility="visible"
    )
    
    # 기타 선택 시 주관식 입력
    other_role = ""
    if selected_role == "기타":
        other_role = st.text_input(
            "직군을 입력해주세요:",
            key="other_role",
            placeholder="예: QA 엔지니어, 인프라 엔지니어 등",
            label_visibility="visible"
        )
        if not other_role or other_role.strip() == "":
            st.info("👆 기타 직군을 입력해주세요.")
            st.stop()
        selected_role = f"기타 ({other_role.strip()})"
    
    if not selected_role or selected_role == "":
        st.info("👆 위에서 직군을 선택해주세요.")
        st.stop()
    
    st.markdown("---")
    
    # 기술 수준 기준 설명
    st.markdown("### 2️⃣ 기술 스택 및 숙련도 선택")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%); 
                padding: 2.5rem; 
                border-radius: 20px; 
                margin-bottom: 3rem;
                border: 2px solid rgba(102, 126, 234, 0.2);
                box-shadow: 0 8px 24px rgba(102, 126, 234, 0.1);">
        <h4 style="color: #667eea; margin: 0 0 2rem 0; font-size: 1.4rem; font-weight: 700;">📊 기술 숙련도 기준</h4>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
            <div style="background: #e0e0e0; padding: 1.75rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                <strong style="color: #666; font-size: 1.2rem; display: block; margin-bottom: 0.75rem;">➖ 해당없음</strong>
                <p style="margin: 0; color: #666; line-height: 1.7; font-size: 0.95rem;">
                    해당 기술을 사용하지 않거나 다루지 않는 경우 (기본값)
                </p>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.75rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(245, 87, 108, 0.3);">
                <strong style="color: white; font-size: 1.2rem; display: block; margin-bottom: 0.75rem;">🔰 입문</strong>
                <p style="margin: 0; color: rgba(255,255,255,0.95); line-height: 1.7; font-size: 0.95rem;">
                    기본 문법과 개념을 이해하고, 간단한 예제나 튜토리얼을 따라할 수 있는 수준
                </p>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.75rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(79, 172, 254, 0.3);">
                <strong style="color: white; font-size: 1.2rem; display: block; margin-bottom: 0.75rem;">📚 초급</strong>
                <p style="margin: 0; color: rgba(255,255,255,0.95); line-height: 1.7; font-size: 0.95rem;">
                    기본 기능을 활용하여 간단한 프로젝트를 독립적으로 개발할 수 있는 수준
                </p>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;">
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.75rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(67, 233, 123, 0.3);">
                <strong style="color: white; font-size: 1.2rem; display: block; margin-bottom: 0.75rem;">⚙️ 중급</strong>
                <p style="margin: 0; color: rgba(255,255,255,0.95); line-height: 1.7; font-size: 0.95rem;">
                    복잡한 기능 구현이 가능하고, 문제 해결을 위해 공식 문서나 커뮤니티 자료를 참고하여 해결할 수 있는 수준
                </p>
            </div>
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.75rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(250, 112, 154, 0.3);">
                <strong style="color: white; font-size: 1.2rem; display: block; margin-bottom: 0.75rem;">🏆 고급</strong>
                <p style="margin: 0; color: rgba(255,255,255,0.95); line-height: 1.7; font-size: 0.95rem;">
                    심화 기능과 최적화를 다룰 수 있고, 다른 팀원들에게 멘토링이나 기술 공유가 가능한 수준
                </p>
            </div>
        </div>
        <p style="margin: 2rem 0 0 0; color: #667eea; font-size: 1rem; font-weight: 600; text-align: center;">
            💡 각 기술에 대해 본인의 숙련도 수준을 클릭하여 선택해주세요
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 직군별 기술 스택 가져오기 (기타인 경우 빈 딕셔너리)
    if selected_role.startswith("기타"):
        tech_data = {}
        st.info("💡 기타 직군을 선택하셨습니다. 아래에서 사용하시는 기술 스택을 직접 입력해주세요.")
        custom_tech = st.text_area(
            "사용하시는 기술 스택을 입력해주세요:",
            key="custom_tech",
            placeholder="예: Java (중급), Python (초급), Docker (입문) 등",
            height=100,
            help="기술명과 숙련도를 함께 입력해주세요."
        )
        form_data = {"이름": name.strip(), "직군": selected_role, "기술 스택": custom_tech if custom_tech else ""}
    else:
        # selected_role이 TECH_STACK에 있는지 확인
        original_role = selected_role
        if original_role not in TECH_STACK:
            # "기타 (입력내용)" 형식이 아닌 경우에만 처리
            tech_data = {}
            st.warning(f"⚠️ '{original_role}' 직군에 대한 기술 스택 정보가 없습니다.")
        else:
            tech_data = TECH_STACK[original_role]
        
        form_data = {"이름": name.strip(), "직군": selected_role}
        
        # 각 카테고리별로 기술 선택
        if tech_data:
            for category, options in tech_data.items():
                st.markdown(f"#### 📌 {category}")
                
                # 각 기술에 대해 5단계 선택 (버튼 형태)
                category_data = {}
                for tech in options:
                    # 기술명을 더 크게 표시
                    st.markdown(f"<div style='margin-bottom: 1.5rem;'><strong style='font-size: 1.6rem; color: #1a1a1a; font-weight: 700;'>{tech}</strong></div>", unsafe_allow_html=True)
                    
                    # 세션 상태에서 현재 선택된 레벨 가져오기
                    level_key = f"{selected_role}_{category}_{tech}_level"
                    if level_key not in st.session_state:
                        st.session_state[level_key] = "해당없음"  # 기본값
                    
                    # 5개 버튼을 옆으로 나열
                    cols = st.columns(5)
                    levels = ["해당없음", "입문", "초급", "중급", "고급"]
                    level_icons = ["➖", "🔰", "📚", "⚙️", "🏆"]
                    level_colors = [
                        "linear-gradient(135deg, #b0b0b0 0%, #d0d0d0 100%)",  # 해당없음 - 회색 그라데이션
                        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",  # 입문 - 핑크
                        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",  # 초급 - 블루
                        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",  # 중급 - 그린
                        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"   # 고급 - 핑크-옐로우
                    ]
                    
                    selected_level = st.session_state[level_key]
                    selected_idx = levels.index(selected_level) if selected_level in levels else 0
                    selected_color = level_colors[selected_idx]
                    
                    # 버튼 렌더링
                    for idx, (level, icon, color) in enumerate(zip(levels, level_icons, level_colors)):
                        with cols[idx]:
                            is_selected = selected_level == level
                            button_label = f"{icon} {level}"
                            
                            if st.button(
                                button_label,
                                key=f"{level_key}_{level}",
                                use_container_width=True,
                                type="primary" if is_selected else "secondary"
                            ):
                                st.session_state[level_key] = level
                                st.rerun()
                    
                    # 선택된 내용 텍스트로 표시
                    selected_icon = level_icons[selected_idx]
                    if selected_level == "해당없음":
                        status_text = f'<div style="margin-top: 0.75rem; padding: 0.75rem 1rem; background: #f5f5f5; border-radius: 8px; border-left: 4px solid #999;"><span style="color: #666; font-size: 0.95rem;">선택됨: <strong>{selected_icon} {selected_level}</strong></span></div>'
                    else:
                        status_text = f'<div style="margin-top: 0.75rem; padding: 0.75rem 1rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 8px; border-left: 4px solid #667eea;"><span style="color: #667eea; font-size: 0.95rem;">✓ 선택됨: <strong>{selected_icon} {selected_level}</strong></span></div>'
                    st.markdown(status_text, unsafe_allow_html=True)
                    
                    current_level = st.session_state[level_key]
                    if current_level != "해당없음":
                        category_data[tech] = current_level
                    
                    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
                
                if category_data:
                    form_data[category] = category_data
                
                st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 제출 버튼
    st.markdown("<div style='margin-top: 3rem; margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("📤 설문 제출하기", type="primary", use_container_width=True, key="submit_btn")
    
    # 설문 컨테이너 닫기
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 제출 버튼 클릭 시 처리
    if submit_button:
        # 데이터 검증
        if selected_role.startswith("기타"):
            if not form_data.get("기술 스택", "").strip():
                st.warning("⚠️ 기술 스택을 입력해주세요.")
            else:
                # Google Sheets에 저장 시도
                if sheet is not None:
                    if save_to_sheets(sheet, form_data):
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error("❌ 저장 중 오류가 발생했습니다. 다시 시도해주세요.")
                else:
                    st.error("❌ Google Sheets 연결이 되어 있지 않아 응답을 저장할 수 없습니다.")
                    st.info("💡 **해결 방법**: Streamlit Cloud Secrets 설정을 확인해주세요.")
        else:
            # 기술 스택이 하나라도 선택되었는지 확인
            has_selection = False
            for key, value in form_data.items():
                if key not in ["이름", "직군"] and value:
                    if isinstance(value, dict) and len(value) > 0:
                        has_selection = True
                        break
            
            if not has_selection:
                st.warning("⚠️ 최소 하나 이상의 기술을 선택해주세요.")
            else:
                # Google Sheets에 저장 시도
                if sheet is not None:
                    if save_to_sheets(sheet, form_data):
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error("❌ 저장 중 오류가 발생했습니다. 다시 시도해주세요.")
                else:
                    st.error("❌ Google Sheets 연결이 되어 있지 않아 응답을 저장할 수 없습니다.")
                    st.info("💡 **해결 방법**: Streamlit Cloud Secrets 설정을 확인해주세요.")
    
    # 푸터
    st.markdown("""
    <div style="background: white; padding: 3rem 4rem; margin-top: 4rem; text-align: center; border-top: 1px solid #e0e0e0;">
        <div style="color: #2661E8; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">visang</div>
        <div style="color: #666; font-size: 0.9rem;">© 2024 Visang Education. All rights reserved.</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
