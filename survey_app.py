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
    page_title="V‑DNA 전사 역량 설문 | 비상교육",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 직군 목록 (1) 직군(역할) 선택 - 1-1 현재 주 직군
OTHER_ROLE_LABEL = "기타(직접 입력)"

JOB_ROLES = [
    # A. IT (세분화 유지)
    "Backend 개발자 (NCS: IT/응용소프트웨어 개발자)",
    "Frontend 개발자 (NCS: IT/응용소프트웨어 개발자)",
    "iOS 앱 개발자(네이티브) (NCS: IT/응용소프트웨어 개발자)",
    "Android 앱 개발자(네이티브) (NCS: IT/응용소프트웨어 개발자)",
    "모바일 앱 개발자(하이브리드) (NCS: IT/응용소프트웨어 개발자)",
    "DevOps 엔지니어 (NCS: IT/정보시스템 운영자)",
    "SRE 엔지니어 (NCS: IT/정보시스템 운영자)",
    "Platform Engineer (NCS: IT/정보시스템 운영자)",
    "Data Engineer (NCS: IT/데이터 전문가)",
    "Data Analyst (NCS: IT/데이터 전문가)",
    "Data Scientist (NCS: IT/데이터 전문가)",
    "LLM 개발자 (NCS: IT/데이터 전문가)",
    "MLOps (NCS: IT/정보시스템 운영자)",
    "정보보안(IT 보안 운영/기술 대응) (NCS: IT/정보보안 전문가)",
    "정보보안(보안 정책·인증·점검/증적 중심) (NCS: IT/정보보안 전문가)",
    "네트워크/시스템 개발자 (NCS: IT/네트워크 시스템 개발자)",
    "정보시스템 운영자(Infra/업무시스템 운영) (NCS: IT/정보시스템 운영자)",

    # B. 웹/서비스기획 · 상품/프로덕트 기획
    "웹/서비스 기획자 (NCS: 웹/서비스기획/기획,마케팅 사무원)",
    "상품/프로덕트 기획자 (NCS: 웹/서비스기획/상품 기획 전문가)",
    "행사/전시 기획 (NCS: 경영/지원/행사·전시 기획자)",

    # C. 마케팅
    "마케팅(브랜드/그로스/퍼포먼스 등) (NCS: 마케팅/기획,마케팅 사무원)",
    "영업·마케팅 운영/지원 (NCS: 기획/영업·마케팅 사무원)",

    # D. 영업/서비스(국내/해외 포함)
    "제품/광고 영업 (NCS: 영업/제품·광고 영업원)",
    "해외 영업 (NCS: 영업/해외 영업원)",
    "고객상담/CS/모니터링 (NCS: 경영/지원/고객상담원 및 모니터요원)",

    # E. 콘텐츠(디지털/영상/교수지원/강의 운영 포함)
    "온리원중등 콘텐츠개발자 (NCS: 콘텐츠/출판물전문가)",
    "차시(비바샘·AIDT 등) 콘텐츠개발자 (NCS: 콘텐츠/출판물전문가)",
    "영상 콘텐츠개발자 (NCS: 콘텐츠/영상·녹화·편집 기사)",
    "서책(교과서/교재) 콘텐츠개발자 (NCS: 교과서/교재개발/출판물전문가)",
    "온오프라인 연수/교육 콘텐츠개발자 (NCS: 콘텐츠/출판물전문가)",

    # F. 디자인/영상(시각·웹·미디어)
    "시각/그래픽 디자이너 (NCS: 디자인/영상/시각 디자이너)",
    "웹디자이너 (NCS: 디자인/영상/웹디자인)",
    "미디어/콘텐츠 디자이너 (NCS: 콘텐츠/미디어 콘텐츠 디자이너)",

    # G. 경영/지원(관리/스탭)
    "경영지원(일반) (NCS: 경영/지원/경영지원)",
    "경영지원 사무원 (NCS: 경영/지원/경영지원 사무원)",
    "총무 (NCS: 경영/지원/총무사무)",
    "회계 (NCS: 경영/지원/회계 사무원)",
    "법무/법률사무 (NCS: 경영/지원/법률사무)",
    "비서 (NCS: 경영/지원/비서)",
    "감사/내부통제 (NCS: 경영/지원/감사사무원)",
    "인사(사무) (NCS: 경영/지원/인사사무)",
    "인사/노무(전문) (NCS: 경영/지원/인사노무전문가)",
    "경영·진단/전략 (NCS: 경영/지원/경영·진단 전문가)",
    "자산·투자 운용 (NCS: 경영/지원/자산·투자 운용가)",
    "물류/운송·물류 사무 (NCS: 물류/운송·물류 사무원)",
    "건강/안마 (NCS: 경영/지원/안마사)",
    "People Analyst (NCS: 경영/지원/인사사무)",

    # H. 리더/임원
    "임원/경영(리더십) (NCS: 기획/기업고위임원)",

    # I. 기타
    OTHER_ROLE_LABEL,
]

# 설문 문항(2)~(15) 정의 - 텍스트만 정의하고 Q 번호는 코드에서 자동 부여
RAW_QUESTION_SECTIONS = [
    {
        "section_id": "2",
        "title": "2) IT 개발·운영 활동 수행 수준(전사 공통)",
        "description": "이 문항이 필요한 이유: “내가 직접 개발을 하느냐”가 아니라, 시스템/데이터/AI 관련 업무에서 어느 수준의 책임을 맡을 수 있는지를 표준화해 파악하기 위함입니다.",
        "columns": 1,
        "questions": [
            "요구사항 분석/정의는 어느 수준까지 할 수 있습니까? (e.g. 목표/범위/우선순위/성공기준을 문서로 정리해 합의)",
            "설계(아키텍처/DB/API)는 어느 수준까지 할 수 있습니까? (e.g. 흐름/데이터 항목/권한/예외 케이스를 정의하고 설계에 반영)",
            "구현(개발/스크립팅/자동화)은 어느 수준까지 할 수 있습니까? (e.g. 기능 구현 또는 반복 작업을 줄이기 위한 자동화/스크립팅)",
            "테스트/품질은 어느 수준까지 할 수 있습니까? (e.g. 정상·예외 케이스 기준을 만들고 결과를 검증)",
            "배포/릴리즈는 어느 수준까지 할 수 있습니까? (e.g. 배포 체크리스트, 영향 범위, 롤백 기준을 준비/확인)",
            "운영/장애 대응은 어느 수준까지 할 수 있습니까? (e.g. 현상/재현 조건/시간대/영향 범위를 정리해 원인 분석과 복구에 기여)",
            "성능 최적화는 어느 수준까지 할 수 있습니까? (e.g. 병목 구간을 특정하거나 개선 방향을 제안/적용)",
            "비용 최적화는 어느 수준까지 할 수 있습니까? (e.g. 리소스 사용을 줄이는 대안을 제안/적용)",
            "보안 대응은 어느 수준까지 할 수 있습니까? (e.g. 권한/접근 통제, 개인정보 처리 기준을 점검/적용)",
            "문서화/표준화는 어느 수준까지 할 수 있습니까? (e.g. 운영 절차/가이드/FAQ를 작성하고 최신화)",
            "코드리뷰/산출물 리뷰는 어느 수준까지 할 수 있습니까? (e.g. 코드 또는 산출물의 기준 준수 여부를 리뷰)",
            "리딩/조율(오너십)은 어느 수준까지 할 수 있습니까? (e.g. 일정/리스크/이해관계자 조율, 의사결정 촉진)",
        ],
    },
    {
        "section_id": "3",
        "title": "3) 협업·개발 기본기(공통)",
        "description": "이 문항이 필요한 이유: 실제 프로젝트 성공은 “기술”뿐 아니라 협업 방식/품질 관리/문서화/문제 해결 방식에 크게 좌우됩니다.",
        "columns": 1,
        "questions": [
            "Git 사용은 어느 수준까지 할 수 있습니까? (e.g. 변경 이력 관리, 충돌 해결, revert/cherry-pick)",
            "이슈/업무 관리는 어느 수준까지 할 수 있습니까? (e.g. 티켓 기반으로 업무를 쪼개고 우선순위를 관리)",
            "디버깅/트러블슈팅은 어느 수준까지 할 수 있습니까? (e.g. 증상→원인 가설→검증→조치의 방식으로 원인을 추적)",
            "리팩토링/기술부채 관리는 어느 수준까지 할 수 있습니까? (e.g. 반복 문제를 구조적으로 개선하고 재발을 줄임)",
            "기술 커뮤니케이션은 어느 수준까지 할 수 있습니까? (e.g. 구조/리스크/대안을 문서나 회의에서 명확히 전달)",
        ],
    },
    {
        "section_id": "4",
        "title": "4) 프로그래밍 & 스크립팅 역량",
        "description": "이 문항이 필요한 이유: 언어 역량은 즉시 투입 가능성(백필 포함)과 교육 우선순위 산정의 기초 데이터입니다.",
        "columns": 3,
        "questions": [
            "ASP (e.g. 레거시 ASP 유지보수)",
            "Bash (e.g. 운영/배포 스크립트)",
            "C (e.g. 성능 민감 모듈)",
            "C# (e.g. .NET 서비스/툴)",
            "C++ (e.g. 게임/성능 최적화)",
            "CSS (e.g. 반응형 스타일)",
            "Dart (e.g. Flutter)",
            "Go (e.g. 서버/툴)",
            "Groovy (e.g. Jenkins 스크립트)",
            "HTML (e.g. 마크업)",
            "Java (e.g. 백엔드)",
            "JavaScript (e.g. 프론트/Node)",
            "JSP (e.g. 레거시 Java 웹)",
            "Kotlin (e.g. Android/서버)",
            "Objective‑C (e.g. 레거시 iOS)",
            "PHP (e.g. 레거시 웹)",
            "PowerShell (e.g. Windows 자동화)",
            "Python (e.g. 데이터/백엔드/자동화)",
            "R (e.g. 통계 분석)",
            "Scala (e.g. Spark)",
            "SQL (e.g. 쿼리 작성/기본 튜닝)",
            "Shell Script (e.g. 서버 자동화)",
            "Swift (e.g. iOS)",
            "TypeScript (e.g. 대규모 프론트/Node)",
            "YAML (e.g. K8s/CI 설정)",
            "Rust (e.g. 성능/안정성 모듈)",
            "Ruby (e.g. 스크립트/레거시)",
            "Lua (e.g. 게임 스크립팅)",
            "Markdown (e.g. 기술 문서/Runbook)",
            "정규표현식(Regex) (e.g. 패턴 매칭/파싱/필터링)",
        ],
    },
    {
        "section_id": "5",
        "title": "5) 애플리케이션 개발 프레임워크/SDK/게임엔진 역량",
        "description": "이 문항이 필요한 이유: 프레임워크/SDK 경험은 실제 생산성과 즉시 투입 가능성을 좌우합니다.",
        "columns": 3,
        "questions": [
            ".NET (e.g. 서버/윈도우 앱)",
            "ASP.NET (e.g. Web API/MVC)",
            "Android SDK (e.g. 네이티브 Android)",
            "Angular (e.g. 프론트 SPA)",
            "Cocos2d‑x (e.g. 게임)",
            "CodeIgniter (e.g. PHP 레거시)",
            "Django (e.g. Python 백엔드)",
            "Expo (e.g. RN 워크플로)",
            "Express (e.g. Node 백엔드)",
            "FastAPI (e.g. Python API)",
            "Flask (e.g. Python 서버)",
            "Flutter (e.g. 크로스플랫폼)",
            "Godot (e.g. 게임)",
            "Ionic (e.g. 하이브리드)",
            "Jetpack Compose (e.g. Android UI)",
            "Koa (e.g. Node)",
            "Laravel (e.g. PHP)",
            "Nest.js (e.g. TS 백엔드)",
            "Next.js (e.g. React SSR)",
            "Node.js (e.g. 런타임/서버)",
            "Nuxt.js (e.g. Vue SSR)",
            "React (e.g. 프론트)",
            "React Native (e.g. 모바일)",
            "Spring (e.g. Java 백엔드)",
            "Spring Boot (e.g. Java 백엔드)",
            "Svelte (e.g. 프론트)",
            "SwiftUI (e.g. iOS UI)",
            "Symfony (e.g. PHP)",
            "UIKit (e.g. iOS UI)",
            "Unity (e.g. 게임)",
            "Unreal Engine (e.g. 게임)",
            "Vue (e.g. 프론트)",
            "jQuery (e.g. 레거시 프론트)",
            "Vite (e.g. 프론트 빌드)",
            "Webpack (e.g. 번들 최적화)",
            "Storybook (e.g. UI 문서화)",
            "Electron (e.g. 데스크톱 앱)",
            "Gradle (e.g. Android/Java 빌드)",
            "Maven (e.g. Java 빌드)",
            "CocoaPods (e.g. iOS 의존성)",
            "SPM(Swift Package Manager) (e.g. iOS 의존성)",
            "RxJS (e.g. 스트림 처리)",
            "GraphQL Client(Apollo 등) (e.g. GraphQL 연동)",
        ],
    },
    {
        "section_id": "6",
        "title": "6) 소프트웨어 품질/테스트 역량",
        "description": "이 문항이 필요한 이유: 테스트/품질 역량은 장애/리워크를 줄여 일정과 운영 안정성을 개선합니다.",
        "columns": 2,
        "questions": [
            "단위 테스트(Unit Test) (e.g. JUnit/Jest/XCTest 작성)",
            "통합 테스트(Integration Test) (e.g. DB 포함 시나리오 검증)",
            "E2E 테스트 (e.g. Cypress/Playwright UI 자동화)",
            "계약 테스트(Contract Test) (e.g. API 스펙 기반 호환성)",
            "테스트 더블/모킹(Mock/Stub) (e.g. 외부 API 모킹)",
            "테스트 자동화 설계 (e.g. CI 자동 실행/리포트)",
            "코드 커버리지 관리 (e.g. 기준선 운영)",
            "성능 테스트/부하 테스트 (e.g. 부하/지연 측정)",
        ],
    },
    {
        "section_id": "7",
        "title": "7) 데이터 엔지니어링 & 데이터 플랫폼 역량",
        "description": "이 문항이 필요한 이유: 데이터 파이프라인/저장소 역량은 전사 분석/AI 품질의 기반이며 인력 계획에 필수입니다.",
        "columns": 2,
        "questions": [
            "데이터 파이프라인 구축 및 운영 (e.g. 배치/재처리)",
            "ETL 솔루션 구축 및 운영 (e.g. ELT 포함)",
            "Apache Airflow (e.g. DAG)",
            "Apache Spark (e.g. 분산 처리)",
            "Kafka (e.g. 스트리밍)",
            "Hadoop (e.g. 레거시)",
            "Dask (e.g. 병렬)",
            "Ray (e.g. 분산)",
            "대용량 데이터 처리 (e.g. 파티셔닝)",
            "데이터 마이그레이션 (e.g. 이관/검증)",
            "정형 데이터 핸들링 (e.g. 모델링)",
            "비정형 데이터 핸들링 (e.g. 로그/텍스트)",
            "Data Lake (e.g. 객체 스토리지)",
            "Data Warehouse (e.g. 분석 스키마)",
            "데이터 카탈로그 (e.g. 메타데이터)",
            "데이터 포털 (e.g. 셀프서브)",
            "MySQL / PostgreSQL / MSSQL / Oracle / SQLite / MariaDB / Redshift / Snowflake / BigQuery (e.g. DB/DW)",
            "MongoDB / Redis / Cassandra / DynamoDB / Elasticsearch/OpenSearch / HBase / Firebase (e.g. NoSQL/검색)",
            "Feature Store(Feast, Tecton) (e.g. 피처 서빙)",
            "Vector DB(Pinecone, Weaviate, Milvus, Qdrant 등) (e.g. 임베딩 검색)",
            "데이터 품질 관리(Data Quality) (e.g. 정합성/이상치)",
            "데이터 검증/테스트 (e.g. 규칙 기반 검증)",
            "데이터 리니지/추적 (e.g. 영향도)",
            "CDC(Change Data Capture) (e.g. 변경분 스트리밍)",
            "스트리밍 처리 설계 (e.g. 중복/재처리)",
            "데이터 권한/접근제어 (e.g. 권한)",
            "개인정보/민감정보 처리(데이터) (e.g. 마스킹/토큰화)",
        ],
    },
    {
        "section_id": "8",
        "title": "8) AI / ML 모델링 역량",
        "description": "이 문항이 필요한 이유: 생성형 AI 포함 AI 역량의 실제 분포를 파악해 교육/채용/프로젝트 배치를 정교화합니다.",
        "columns": 2,
        "questions": [
            "AI/ML 모델 개발 (e.g. 학습 파이프라인)",
            "예측 모델링 (e.g. 수요/점수 예측)",
            "분류 모델링 (e.g. 스팸/카테고리)",
            "최적화 모델링 (e.g. 스케줄 최적화)",
            "추천 시스템 구축 (e.g. 개인화 추천)",
            "자연어 처리(NLP) (e.g. 분류/요약)",
            "컴퓨터 비전(CV) (e.g. 검출/분류)",
            "대화형 AI(Chatbot) (e.g. 상담/학습봇)",
            "생성형 AI(Generative AI) (e.g. 콘텐츠 생성)",
            "LLM 활용 (e.g. API 연동 기능)",
            "모델 성능 평가 및 최적화 (e.g. 지표/튜닝)",
            "데이터 라벨링/학습데이터 구축 (e.g. 라벨 가이드)",
            "피처 엔지니어링 (e.g. 누수 방지)",
            "실험 설계/재현성 관리 (e.g. seed/버전 고정)",
            "LLM 프롬프트 엔지니어링 (e.g. few-shot)",
            "RAG 설계/구현 (e.g. 청킹/리트리벌)",
            "LLM 평가(Evals) (e.g. eval set/휴먼 평가)",
            "AI 안전/가드레일 (e.g. PII 필터/환각 대응)",
            "비용/지연 최적화(LLM) (e.g. 캐시/모델 라우팅)",
        ],
    },
    {
        "section_id": "9",
        "title": "9) MLOps & 모델 운영 역량",
        "description": "이 문항이 필요한 이유: 모델을 “서비스로 운영”하는 역량(배포/모니터링/재학습 등)을 파악하기 위함입니다.",
        "columns": 2,
        "questions": [
            "MLOps 파이프라인 구축 및 운영 (e.g. 학습→배포 자동화)",
            "ML 파이프라인 구축 및 운영 (e.g. 데이터→학습→평가)",
            "Kubeflow (e.g. 파이프라인)",
            "MLflow (e.g. 실험/레지스트리)",
            "DVC (e.g. 데이터/모델 버전)",
            "모델 배포 자동화 (e.g. CI로 배포)",
            "모델 모니터링 및 자동 재학습 구성 (e.g. 성능 저하 감지)",
            "AI/ML 인프라 생성 및 관리 (e.g. 학습/서빙 클러스터)",
            "AWS 기반 AI/ML 인프라 (e.g. EKS/SageMaker)",
            "분산 컴퓨팅 (e.g. 분산 학습)",
            "GPU 클러스터 운영 (e.g. 드라이버/노드)",
            "GPU 자원 스케줄링 (e.g. 큐/우선순위)",
            "GPU Sharing (e.g. MIG 공유)",
            "Nvidia Operator (e.g. GPU 오퍼레이터)",
            "ONNX Runtime / TensorFlow Serving / TorchServe / Triton Inference Server / vLLM (e.g. 추론/서빙)",
            "모델 레지스트리/승인 프로세스 (e.g. staging→prod)",
            "데이터/모델 드리프트 감지 (e.g. 입력 분포 변화)",
            "온라인 A/B 테스트(모델) (e.g. 신규 모델 실험)",
            "추론 성능 최적화 (e.g. 배치/quantization)",
            "프롬프트/체인 버전관리(LLM) (e.g. 프롬프트 이력)",
            "LLM Observability (e.g. 품질/비용/실패율)",
        ],
    },
    {
        "section_id": "10",
        "title": "10) 인프라 · 클라우드 · 컨테이너(Runtime) 역량",
        "description": "이 문항이 필요한 이유: 운영 안정성과 비용/보안에 직결되는 인프라 역량 분포를 파악하기 위함입니다.",
        "columns": 2,
        "questions": [
            "Linux / Unix / Windows / macOS (e.g. 시스템 운영)",
            "AWS / Azure / GCP / NCP / OCI / On‑Prem / IDC / Databricks (e.g. 환경 운영)",
            "Docker / Kubernetes / EKS / GKE / AKS / Helm / Kustomize / Rancher (e.g. 컨테이너)",
            "네트워크 기본 (e.g. DNS/TCP/TLS)",
            "IAM/권한 설계 (e.g. 최소권한)",
            "로드밸런서/리버스 프록시 (e.g. ALB/Nginx)",
            "스토리지/백업/복구 (e.g. 스냅샷/DR)",
            "컨테이너 이미지 운영 (e.g. 이미지 스캔/레지스트리)",
            "서비스 메시(Service Mesh) (e.g. Istio)",
            "Ingress 설계 (e.g. TLS termination)",
        ],
    },
    {
        "section_id": "11",
        "title": "11) DevOps · CI/CD · 자동화 역량",
        "description": "이 문항이 필요한 이유: 자동화 성숙도는 배포 속도·품질·안정성을 결정하는 핵심 지표입니다.",
        "columns": 2,
        "questions": [
            "CI/CD 파이프라인 구축 및 운영 (e.g. 빌드→테스트→배포 자동화)",
            "GitOps / ArgoCD (e.g. 선언형 배포)",
            "GitHub Actions / GitLab CI / Jenkins (e.g. 파이프라인)",
            "프론트/모바일/게임 빌드·배포 자동화 (e.g. 릴리즈 자동화)",
            "데이터 분석 보고서 자동화 (e.g. 정기 리포트)",
            "보안 테스트/취약점 자동화 (e.g. SAST/DAST 자동 실행)",
            "IaC(Infrastructure as Code) (e.g. Terraform/CloudFormation)",
            "배포 전략 (e.g. Blue‑Green/Canary)",
            "아티팩트/패키지 관리 (e.g. Nexus/사설 레지스트리)",
            "비밀정보 관리 (e.g. Vault/Secret Manager)",
            "릴리즈/체인지 관리 (e.g. 승인/릴리즈 노트)",
        ],
    },
    {
        "section_id": "12",
        "title": "12) 시스템 아키텍처 & 실시간 통신 역량",
        "description": "이 문항이 필요한 이유: 설계 역량은 확장성/장애 대응/운영 난이도를 좌우해 핵심 인력 식별에 중요합니다.",
        "columns": 2,
        "questions": [
            "마이크로서비스 아키텍처(MSA) (e.g. 서비스 분리/독립 배포)",
            "이벤트 기반 아키텍처(EDA) (e.g. 비동기 이벤트 처리)",
            "RESTful API 설계 (e.g. 버저닝/에러 규격)",
            "서버리스 아키텍처 (e.g. 함수 기반 구성)",
            "WebSocket (e.g. 양방향 실시간 메시지/상태 동기화)",
            "WebRTC (e.g. 실시간 음성/영상/화면공유)",
            "gRPC (e.g. 내부 서비스 고성능 통신)",
            "GraphQL (e.g. 필요한 데이터만 질의)",
            "SSE (e.g. 서버→클라이언트 단방향 스트림)",
            "모놀리식→MSA 분리/전환 (e.g. 점진적 분리 전략)",
            "캐시/세션 전략 (e.g. Redis 세션/캐시 무효화)",
            "데이터 일관성/사가(Saga) (e.g. 분산 트랜잭션 대안)",
            "메시지 큐/브로커 설계 (e.g. 중복/재처리)",
            "장애 격리/회복탄력성 (e.g. timeout/retry/circuit breaker)",
            "API 게이트웨이 (e.g. 인증/레이트리밋)",
            "Rate Limiting/Quota (e.g. 과호출 방어)",
        ],
    },
    {
        "section_id": "13",
        "title": "13) 관측성(Observability) & 운영성 역량",
        "description": "이 문항이 필요한 이유: 운영 가능한 역량을 구분하는 핵심이며 장애 대응/MTTR/운영 백필에 필수입니다.",
        "columns": 2,
        "questions": [
            "로그 수집/분석 (e.g. 중앙 로그/검색/대시보드)",
            "메트릭 모니터링 (e.g. CPU/Latency 대시보드)",
            "분산 트레이싱 (e.g. 요청 추적)",
            "알람/온콜 운영 (e.g. 심각도 기준/프로세스)",
            "SLI/SLO 정의 (e.g. error rate/p95 목표)",
            "Runbook/장애 회고(Postmortem) (e.g. 재발 방지)",
        ],
    },
    {
        "section_id": "14A",
        "title": "14-A) 정보보안 역량 - IT 보안 운영/기술 대응",
        "description": "이 문항이 필요한 이유: 전사 리스크(사고/감사/규제)에 직결되므로, IT 보안 운영 역량을 정확히 파악하기 위함입니다.",
        "columns": 2,
        "questions": [
            "WAF 구축 및 운영은 어느 수준까지 할 수 있습니까? (e.g. 룰 적용/튜닝, 오탐·미탐 대응)",
            "Firewall 구축 및 운영은 어느 수준까지 할 수 있습니까? (e.g. 정책/포트/대역 관리)",
            "IDS/IPS 구축 및 운영은 어느 수준까지 할 수 있습니까? (e.g. 탐지/차단 정책 운영)",
            "VPN 구성 및 운영은 어느 수준까지 할 수 있습니까? (e.g. 원격 접속 보안 구성)",
            "접근통제 시스템 운영은 어느 수준까지 할 수 있습니까? (e.g. 계정·권한 운영, 접근 승인/회수)",
            "보안장비 운영은 어느 수준까지 할 수 있습니까? (e.g. 장비 로그/정책 관리)",
            "웹 보안 취약점 방어 구현은 어느 수준까지 할 수 있습니까? (e.g. XSS/CSRF/SQLi 방어 구현)",
            "취약점 관리는 어느 수준까지 할 수 있습니까? (e.g. 진단→조치→재점검, 우선순위 관리)",
            "침해사고 대응은 어느 수준까지 할 수 있습니까? (e.g. 탐지→분석→격리→복구→재발방지)",
            "OWASP는 어느 수준까지 이해/적용할 수 있습니까? (e.g. 웹 취약점 분류 체계 이해)",
            "OWASP Top 10은 어느 수준까지 이해/적용할 수 있습니까? (e.g. Top10 기반 점검/개선)",
            "CVE는 어느 수준까지 활용할 수 있습니까? (e.g. 공지 확인 및 영향도 판단)",
            "CWE는 어느 수준까지 활용할 수 있습니까? (e.g. 약점 유형 기반 재발 방지)",
            "정적분석(SAST)은 어느 수준까지 운영할 수 있습니까? (e.g. 코드 스캔 파이프라인/룰)",
            "동적분석(DAST)은 어느 수준까지 운영할 수 있습니까? (e.g. 스테이징 점검/리포트)",
            "비밀정보 노출 방지는 어느 수준까지 할 수 있습니까? (e.g. 키/토큰 유출 방지, 스캔/차단)",
            "취약점 패치/패치관리는 어느 수준까지 할 수 있습니까? (e.g. 패치 계획/배포/검증)",
            "개인정보/민감정보 마스킹/암호화는 어느 수준까지 할 수 있습니까? (e.g. 컬럼 암호화/토큰화)",
            "접근 로그/감사로그 설계는 어느 수준까지 할 수 있습니까? (e.g. 추적성 확보, 로그 보존 정책)",
        ],
    },
    {
        "section_id": "14B",
        "title": "14-B) 정보보안 역량 - 보안 정책·인증·규정 준수",
        "description": "이 문항이 필요한 이유: 정책/인증·점검 운영 역량을 구분해 정확히 파악하기 위함입니다.",
        "columns": 2,
        "questions": [
            "보안 정책 수립은 어느 수준까지 할 수 있습니까? (e.g. 계정/권한/로그/비밀번호 정책)",
            "보안 아키텍처(통제 체계) 설계는 어느 수준까지 할 수 있습니까? (e.g. 관리적·기술적·물리적 통제 정리)",
            "한국 개인정보보호법(PIPA) 대응은 어느 수준까지 할 수 있습니까? (e.g. 수집·이용·보관·파기 기준/점검)",
            "GDPR 대응은 어느 수준까지 할 수 있습니까? (e.g. 처리기록/권리 대응 프로세스)",
            "CCPA/CPRA 대응은 어느 수준까지 할 수 있습니까? (e.g. 고지/요청 처리 체계)",
            "ISMS 대응은 어느 수준까지 할 수 있습니까? (e.g. 통제 항목 운영, 점검표, 증적 관리)",
            "ISMS-P 대응은 어느 수준까지 할 수 있습니까? (e.g. 개인정보 통제/점검/증적)",
            "CSAP 대응은 어느 수준까지 할 수 있습니까? (e.g. 요구사항 점검/증적/개선조치)",
            "ISO27001 대응은 어느 수준까지 할 수 있습니까? (e.g. 심사 준비, 문서/증적, 개선조치)",
        ],
    },
    {
        "section_id": "15",
        "title": "15) 인증(SSO) · 결제 경험 + 레거시/전환 리스크 경험",
        "description": "이 문항이 필요한 이유: 도메인 경험과 고위험 전환 경험은 즉시 투입·백필 판단에 강한 신호입니다.",
        "columns": 2,
        "questions": [
            "SSO 연동 개발 경험 (Google/Apple/Azure AD/사내 계정 등) (e.g. OIDC 연동/콜백 처리)",
            "인증 시스템 구현 경험 (JWT/OAuth2/세션 등) (e.g. Access/Refresh 토큰)",
            "권한/역할(Role) 구조 설계 경험 (e.g. RBAC)",
            "결제 시스템 연동 개발 경험 (PG사 API 등) (e.g. 승인/취소/검증)",
            "정기결제/구독 결제 구현 경험 (e.g. 실패 재시도/유예기간)",
            "환불/정산/결제 장애 처리 경험 (e.g. 대사/재처리)",
            "계정 통합/휴면/탈퇴 처리 (e.g. 계정 병합/탈퇴 데이터 처리)",
            "MFA/2FA 적용 (e.g. OTP/SMS/Authenticator)",
            "결제 보안/부정결제 대응 (e.g. 리스크 룰/차단)",
            "청구서/영수증/세금계산서 처리(해당 시) (e.g. B2B 정산)",
            "구독 상태 머신 설계 (e.g. trial→paid→grace→cancel)",
            "레거시 코드 리팩토링 (e.g. 테스트 없는 코드 개선)",
            "프레임워크/런타임 업그레이드 (e.g. Spring/Node 메이저 업그레이드)",
            "DB 마이그레이션 (e.g. 스키마 변경/검증)",
            "데이터 대량 마이그레이션 (e.g. 정합성 검증)",
            "모니터링/알람 신규 구축 (e.g. 알람 폭주/누락 방지)",
            "보안 취약점 대량 조치 (e.g. 전사 패치)",
        ],
    },
]

# RAW_QUESTION_SECTIONS를 기반으로 Q1, Q2, ... 번호를 전역 순서로 자동 부여
QUESTION_SECTIONS = []
_q_counter = 1
for _section in RAW_QUESTION_SECTIONS:
    _qs = []
    for _text in _section["questions"]:
        _qs.append(
            {
                "id": f"Q{_q_counter}",
                "text": _text,
            }
        )
        _q_counter += 1
    QUESTION_SECTIONS.append(
        {
            "section_id": _section["section_id"],
            "title": _section["title"],
            "description": _section.get("description", ""),
            "columns": _section.get("columns", 2),
            "questions": _qs,
        }
    )

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
    
    # 이미지 배치: visang_logo.png 왼쪽 위, vdna_banner.png 메인 배너
    col_logo, col_banner = st.columns([1, 3])
    
    with col_logo:
        try:
            # visang_logo.png 왼쪽 위에 작게 배치
            st.image("visang_logo.png", width=150, output_format="PNG")
        except:
            pass
    
    with col_banner:
        try:
            # vdna_banner.png 메인 배너로 배치 (사이즈 조정)
            st.image("vdna_banner.png", width=600, output_format="PNG")
        except:
            # 이미지가 없거나 로드 실패 시 HTML로 대체 이미지 영역 표시
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
    
    # 설문 제목 및 인삿말/안내
    st.markdown("""
    <h1 style="font-size: 2rem; margin-bottom: 1rem;">📋 V‑DNA 전사 역량 설문 (최종 배포본)</h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    안녕하세요. 비상교육 V‑DNA 설문에 참여해 주셔서 감사합니다.
    본 설문은 전사 구성원의 역할/경험/역량을 공통 기준으로 파악하여, 교육·배치·채용 및 데이터 기반 의사결정에 활용하기 위해 진행합니다.
    
    **설문 목적**
    - 역량 파악 → 교육 로드맵/리스킬링 추천
    - 부서 간 프로젝트 매칭
    - 채용·인원 계획 및 백필(대체 인력) 탐색
    - 머신러닝/딥러닝 기반 인재 모델 학습 데이터(Feature)로 활용
    
    **응답 방법(공통)**  
    - 모든 문항은 동일한 5단계로 응답합니다: **해당없음 / 생초보 / 초급 / 중급 / 고급**
    - 업무와 무관하거나 경험이 없으면 **‘해당없음’(기본값)**을 그대로 두고 넘어가시면 됩니다.
    
    **수준 판단 가이드(권장)**  
    - **생초보**: 용어/개념을 아는 정도, 따라해본 경험  
    - **초급**: 일부 수행/보조 가능(가이드/리뷰 필요)  
    - **중급**: 독립 수행 가능(표준 문제 해결 가능)  
    - **고급**: 설계/표준화/리딩 가능(복잡한 문제 해결·최적화 포함)
    """)
    
    st.markdown("---")
    
    # 사용자 정보 표시
    st.markdown(f"**로그인된 사용자**: {user_email}")
    
    if has_existing_response:
        st.info("✅ 이미 설문에 응답하셨습니다. 아래에서 수정할 수 있습니다.")
    
    st.markdown("---")
    
    # 직군 선택 (폼 밖에서 처리)
    st.markdown("### 1) 직군(역할) 선택")
    existing_job_role = existing_response_data.get("job_role", "") if has_existing_response and existing_response_data else ""
    
    # 기존 응답에서 기타(직접 입력)인 경우 확인
    other_job_role = None
    if existing_job_role and existing_job_role not in JOB_ROLES:
        other_job_role = existing_job_role
        existing_job_role = OTHER_ROLE_LABEL
    
    # 직군을 5개씩 그룹으로 나누기 (기타는 마지막에 별도로 표시)
    job_roles_without_other = [r for r in JOB_ROLES if r != OTHER_ROLE_LABEL]
    job_roles_groups = [job_roles_without_other[i:i+5] for i in range(0, len(job_roles_without_other), 5)]
    
    # 세션 상태로 선택된 직군 관리
    if "selected_job_role" not in st.session_state:
        st.session_state.selected_job_role = existing_job_role if existing_job_role else ""
    
    # 각 그룹별로 버튼 표시 (폼 밖)
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
    
    # "기타(직접 입력)" 옵션
    cols_other = st.columns(5)
    with cols_other[0]:
        button_type_other = "primary" if st.session_state.selected_job_role == OTHER_ROLE_LABEL else "secondary"
        if st.button(
            OTHER_ROLE_LABEL,
            key="job_role_btn_기타",
            use_container_width=True,
            type=button_type_other
        ):
            st.session_state.selected_job_role = OTHER_ROLE_LABEL
            st.rerun()
    
    job_role = st.session_state.selected_job_role
    
    # 선택된 직군 표시
    if job_role:
        if job_role == OTHER_ROLE_LABEL:
            st.markdown(f"**선택된 직군(주 직군)**: {other_job_role if other_job_role else '기타(직접 입력) (입력 필요)'}")
        else:
            st.markdown(f"**선택된 직군(주 직군)**: {job_role}")
    
    # "기타" 옵션 입력 (폼 밖)
    if job_role == OTHER_ROLE_LABEL:
        other_job_role = st.text_input("직군을 입력해주세요 *", placeholder="예: QA 엔지니어", value=other_job_role if other_job_role else "", key="other_job_role_input")
    
    # 1-2. 부 직군 선택 (선택, 최대 2개) - 주 직군과 동일 목록에서 멀티 선택 (기타 제외)
    st.markdown("#### 1-2. 부 직군이 있습니까? (선택, 최대 2개)")
    secondary_roles_existing = existing_response_data.get("secondary_roles", []) if has_existing_response and existing_response_data else []
    secondary_role_options = [r for r in JOB_ROLES if r != OTHER_ROLE_LABEL]
    secondary_roles = st.multiselect(
        "부 직군 선택 (최대 2개)",
        options=secondary_role_options,
        default=secondary_roles_existing,
        key="secondary_roles_multiselect",
        max_selections=2,
        label_visibility="collapsed",
        help="현재는 웹/서비스 기획자지만 과거 Frontend 개발자 경험이 있는 경우와 같이, 추가로 경험이 있는 직군을 선택해주세요."
    )
    
    # 숙련도 설명 (직군 선택 바로 밑으로 이동)
    st.markdown("### 📌 숙련도 안내")
    st.markdown("""
    <div style="background: #f0f4ff; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2661E8; margin: 1rem 0;">
        <h4 style="color: #2661E8; margin-bottom: 1rem;">숙련도 기준</h4>
        <ul style="color: #1a1a1a; line-height: 2; font-size: 1rem;">
            <li><strong>해당없음</strong>: 해당 기술을 사용하지 않거나 경험이 없음</li>
            <li><strong>생초보</strong>: 사용 경험은 있으나 실무에 독립적으로 활용하기 어려움</li>
            <li><strong>초급</strong>: 기본적인 사용법을 알고 있으며, 간단한 작업을 수행할 수 있음</li>
            <li><strong>중급</strong>: 일반적인 업무를 독립적으로 수행할 수 있으며, 문제 해결 능력이 있음</li>
            <li><strong>고급</strong>: 복잡한 문제 해결 및 아키텍처 설계, 타인 교육 가능</li>
        </ul>
        <p style="color: #666; margin-top: 1rem; font-size: 0.95rem;">
            💡 <strong>참고:</strong> "해당없음"이 기본값이므로, 해당 기술을 사용하지 않거나 경험이 없다면 별도로 선택하지 않아도 됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 설문 폼 (2) ~ (15) 문항
    with st.form("survey_form", clear_on_submit=False):
        # 숙련도 옵션 (5단계)
        proficiency_levels = ["해당없음", "생초보", "초급", "중급", "고급"]

        # 기존 응답 불러오기 (Q1, Q2, ...)
        existing_responses = existing_response_data.get("responses", {}) if has_existing_response and existing_response_data else {}

        # 새 응답을 저장할 딕셔너리
        responses = {}

        # 2) ~ 15) 섹션 렌더링
        for section in QUESTION_SECTIONS:
            st.markdown("---")
            st.markdown(f"### {section['title']}")
            if section.get("description"):
                st.markdown(section["description"])

            cols_per_row = section.get("columns", 2)
            questions = section["questions"]

            for i in range(0, len(questions), cols_per_row):
                row_qs = questions[i:i+cols_per_row]
                cols = st.columns(len(row_qs))
                for col, q in zip(cols, row_qs):
                    with col:
                        q_id = q["id"]
                        label = q["text"]

                        # 기존 숙련도 가져오기 (없으면 기본값: 해당없음)
                        existing_proficiency = existing_responses.get(q_id, "해당없음")

                        # 세션 상태 키
                        proficiency_key = f"prof_{q_id}"
                        if proficiency_key not in st.session_state:
                            st.session_state[proficiency_key] = existing_proficiency

                        current_proficiency = st.session_state.get(proficiency_key, existing_proficiency)
                        proficiency_index = proficiency_levels.index(current_proficiency) if current_proficiency in proficiency_levels else 0

                        # 문항 제목 (Q번호 + 질문)
                        st.markdown(f"**{q_id}. {label}**")

                        # 숙련도 선택 드롭다운
                        proficiency = st.selectbox(
                            "숙련도",
                            options=proficiency_levels,
                            index=proficiency_index,
                            key=proficiency_key,
                            label_visibility="collapsed",
                        )

                        if proficiency != st.session_state.get(proficiency_key):
                            st.session_state[proficiency_key] = proficiency

                        responses[q_id] = proficiency
        
        st.markdown("---")
        
        # 제출 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("설문 제출", type="primary", use_container_width=True)
        
        if submitted:
            # 유효성 검사
            if not job_role:
                st.error("직군을 선택해주세요.")
            elif job_role == OTHER_ROLE_LABEL and (not other_job_role or not other_job_role.strip()):
                st.error("직군을 입력해주세요.")
            else:
                # 최종 직군 결정
                final_job_role = other_job_role.strip() if job_role == OTHER_ROLE_LABEL else job_role

                # user_profiles에서 이름 가져오기
                try:
                    user_profile = supabase.table("user_profiles").select("name").eq("id", user_id).execute()
                    user_name = user_profile.data[0].get("name", "") if user_profile.data else ""
                except:
                    user_name = ""

                # Supabase에 저장
                try:
                    # responses는 각 문항(Q번호)을 개별 항목으로 저장 (Q번호: 숙련도)
                    response_data = {
                        "user_id": user_id,
                        "name": user_name,  # user_profiles에서 가져온 이름 사용
                        "job_role": final_job_role,
                        "secondary_roles": secondary_roles,
                        "responses": responses,  # {"Q1": "중급"} 형태
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
