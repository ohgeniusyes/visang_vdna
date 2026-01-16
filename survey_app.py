import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import json
import base64

# 페이지 설정
st.set_page_config(
    page_title="IT 개발자 기술 스택 설문",
    page_icon="📋",
    layout="wide"
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
        
        # 헤더가 없으면 추가
        if worksheet.row_count == 0:
            headers = ["타임스탬프", "이름", "직군"] + [k for k in data.keys() if k not in ["이름", "직군"]]
            worksheet.append_row(headers)
        else:
            # 기존 헤더 읽기
            headers = worksheet.row_values(1)
        
        # 데이터 추가
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            data.get("이름", ""),
            data.get("직군", "")
        ]
        
        # 나머지 카테고리 데이터 추가
        for key in headers[3:]:  # 타임스탬프, 이름, 직군 제외
            value = data.get(key, "")
            if isinstance(value, list):
                value = ", ".join(value)
            row.append(value)
        
        worksheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"데이터 저장 오류: {str(e)}")
        return False

def main():
    st.title("📋 IT 개발자 기술 스택 설문")
    st.markdown("---")
    st.info("💡 **안내**: 본 설문은 비상교육 IT 개발자들의 기술력을 파악하기 위한 것입니다. 성실하게 응답해주시면 감사하겠습니다.")
    st.markdown("---")
    
    # 세션 상태 초기화
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    if st.session_state.submitted:
        st.success("✅ 설문이 성공적으로 제출되었습니다! 감사합니다.")
        if st.button("새 설문 작성하기"):
            st.session_state.submitted = False
            st.rerun()
        return
    
    # Google Sheets 설정 (Streamlit Secrets 사용)
    if 'GOOGLE_SHEETS_CREDENTIALS' not in st.secrets or 'SPREADSHEET_ID' not in st.secrets:
        st.warning("⚠️ Google Sheets 설정이 필요합니다.")
        st.info("""
        **설정 방법:**
        1. Google Cloud Console에서 서비스 계정 생성
        2. 서비스 계정 JSON 키 다운로드
        3. Streamlit Secrets에 추가:
           - `.streamlit/secrets.toml` 파일 생성
           - `GOOGLE_SHEETS_CREDENTIALS`에 JSON 내용 추가
           - `SPREADSHEET_ID`에 Google Sheet ID 추가
        """)
        return
    
    # Google Sheets 초기화
    try:
        creds_value = st.secrets['GOOGLE_SHEETS_CREDENTIALS']
        spreadsheet_id = st.secrets['SPREADSHEET_ID']
    except KeyError as e:
        st.error(f"Secrets에 필요한 키가 없습니다: {e}")
        return
    
    # Secrets에서 가져온 값이 딕셔너리인 경우 (TOML이 자동 파싱한 경우)
    if isinstance(creds_value, dict):
        # 이미 딕셔너리이므로 그대로 사용
        credentials_dict = creds_value
    elif isinstance(creds_value, str):
        # 문자열인 경우 JSON 파싱
        try:
            credentials_dict = json.loads(creds_value.strip())
        except json.JSONDecodeError:
            st.error("❌ JSON 파싱 실패: Secrets의 GOOGLE_SHEETS_CREDENTIALS 형식을 확인해주세요.")
            st.info("💡 **해결 방법**: Streamlit Cloud Secrets에서 JSON을 삼중 따옴표(''')로 감싸서 입력하세요.")
            return
    else:
        st.error(f"❌ 잘못된 형식: {type(creds_value).__name__}")
        return
    
    sheet = init_google_sheets(credentials_dict, spreadsheet_id)
    
    if sheet is None:
        return
    
    # 이름 입력
    st.subheader("0️⃣ 이름 입력")
    name = st.text_input(
        "귀하의 이름을 입력해주세요:",
        key="name",
        placeholder="홍길동"
    )
    
    if not name or name.strip() == "":
        st.info("👆 위에 이름을 입력해주세요.")
        return
    
    st.markdown("---")
    
    # 직군 선택
    st.subheader("1️⃣ 직군 선택")
    selected_role = st.selectbox(
        "귀하의 직군을 선택해주세요:",
        options=[""] + JOB_ROLES,
        key="job_role"
    )
    
    if not selected_role:
        st.info("👆 위에서 직군을 선택해주세요.")
        return
    
    st.markdown("---")
    
    # 선택한 직군의 기술 스택 표시
    st.subheader(f"2️⃣ 기술 스택 선택 ({selected_role})")
    st.caption("💡 각 카테고리에서 본인이 다룰 수 있는 기술을 모두 선택해주세요. (복수 선택 가능)")
    
    tech_data = TECH_STACK[selected_role]
    form_data = {"이름": name.strip(), "직군": selected_role}
    
    # 각 카테고리별로 멀티셀렉트 박스 생성
    for category, options in tech_data.items():
        selected = st.multiselect(
            f"**{category}** (복수 선택 가능):",
            options=options,
            key=f"{selected_role}_{category}",
            help=f"{category} 관련 기술 중 본인이 다룰 수 있는 항목을 모두 선택해주세요."
        )
        form_data[category] = selected
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button = st.button("📤 설문 제출하기", type="primary", use_container_width=True)
    
    if submit_button:
        # 데이터 검증
        total_selected = sum(len(v) if isinstance(v, list) else 0 for v in form_data.values() if v not in [name.strip(), selected_role])
        
        if total_selected == 0:
            st.warning("⚠️ 최소 하나 이상의 기술을 선택해주세요.")
        else:
            # Google Sheets에 저장
            if save_to_sheets(sheet, form_data):
                st.session_state.submitted = True
                st.rerun()
            else:
                st.error("❌ 저장 중 오류가 발생했습니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()
