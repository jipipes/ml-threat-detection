# ML Threat Detection System

> 엔드포인트 네트워크 이벤트를 실시간으로 분석하여 보안 위협을 자동 탐지하는 ML 기반 시스템

## 프로젝트 개요

보안 관제 환경에서 수백만 건의 네트워크 이벤트 중 공격을 자동으로 판별하는 AI 탐지 시스템입니다.
룰 기반 탐지가 알려진 패턴만 잡는다면, 이 시스템은 ML 모델로 이상 행위와 미지의 공격 패턴까지 포착합니다.
탐지 결과는 Gemini API를 통해 보안 분석가가 읽기 쉬운 언어로 자동 요약됩니다.

## 주요 기능

- **이상탐지**: Isolation Forest 기반 비지도 이상탐지
- **악성 분류**: XGBoost 기반 이진 분류 (정상/공격)
- **자동 요약**: Gemini API를 활용한 탐지 결과 자동 요약
- **REST API 서빙**: FastAPI 기반 예측 엔드포인트
- **컨테이너화**: Docker 기반 배포 환경 구성

## 시스템 아키텍처

네트워크 이벤트 → 전처리(스케일링/인코딩) → ML 모델(XGBoost) → FastAPI → Gemini 요약

## 모델 성능

| 모델 | F1 Score | 비고 |
|---|---|---|
| Isolation Forest | 0.542 | 비지도학습 baseline |
| **XGBoost** | **0.922** | 메인 모델 채택 |

- 정확도: 90%
- 오탐(FP): 1,094건
- 미탐(FN): 16,403건
- 핵심 피처: `sttl`(Source TTL) — 공격 트래픽의 비정상적 TTL 값이 주요 탐지 신호

## 데이터셋

**UNSW-NB15** (Australian Centre for Cyber Security)
- Train: 82,332건 / Test: 175,341건 / 피처: 42개
- 9가지 공격 유형: Generic, Exploits, Fuzzers, DoS, Reconnaissance 등
- 클래스 불균형 없음 (정상 45% : 공격 55%)
- 선택 이유: 보안 ML 분야 표준 벤치마크 데이터셋. 실제 운영에서는 EDR 텔레메트리 데이터로 대체 예정

```bash
kaggle datasets download -d mrwellsdavid/unsw-nb15 -p data/raw --unzip
```

## 기술 스택

| 분류 | 기술 |
|---|---|
| ML | scikit-learn, XGBoost |
| 데이터 처리 | Pandas, NumPy |
| API 서빙 | FastAPI, Uvicorn |
| LLM | Gemini API (google-generativeai) |
| 컨테이너 | Docker |
| 버전 관리 | Git, GitHub |

## 프로젝트 구조

ml-threat-detection/
├── data/
│   ├── raw/          # UNSW-NB15 원본 데이터
│   └── processed/    # 전처리된 데이터 (스케일러 포함)
├── notebooks/
│   ├── 01_EDA.ipynb          # 탐색적 데이터 분석
│   ├── 02_preprocessing.ipynb # 전처리 및 피처 엔지니어링
│   └── 03_model.ipynb         # 모델 학습 및 평가
├── src/
│   └── main.py       # FastAPI 서빙 코드
├── models/           # 학습된 모델 파일
├── Dockerfile
└── requirements.txt

## 실행 방법

### 로컬 실행

```bash
# 환경 설정
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 데이터 다운로드
kaggle datasets download -d mrwellsdavid/unsw-nb15 -p data/raw --unzip

# 노트북 순서대로 실행
# 01_EDA.ipynb → 02_preprocessing.ipynb → 03_model.ipynb

# API 서버 실행
uvicorn src.main:app --reload
```

### Docker 실행

```bash
docker build -t ml-threat-detection .
docker run -p 8000:8000 --env-file .env ml-threat-detection
```

### API 테스트

http://127.0.0.1:8000/docs

## 환경 변수

KAGGLE_API_TOKEN=your_kaggle_api_token
GEMINI_API_KEY=your_gemini_api_key

## 한계 및 개선 방향

- 2015년 데이터셋 기반으로 최신 공격 패턴 반영 한계 → 실시간 EDR 데이터 연동 필요
- 미탐(16,403건) 개선을 위한 threshold 조정 및 앙상블 고도화 필요
- Kafka 기반 실시간 스트리밍 파이프라인 연동 예정
- MITRE ATT&CK 자동 매핑 기능 추가 예정

## MITRE ATT&CK 연관 기법

| 탐지 대상 | MITRE ATT&CK |
|---|---|
| 비정상 TTL 패킷 | T1095 (Non-Standard Port) |
| DoS 트래픽 패턴 | T1499 (Endpoint Denial of Service) |
| 포트스캔 행위 | T1046 (Network Service Discovery) |

