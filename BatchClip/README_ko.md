# BatchClip

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**자동화 일괄 비디오 편집 도구**

*FastAPI + FFmpeg + Streamlit 아키텍처 기반, 비디오 업로드, 전처리, 러프컷 워크플로우 지원*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

- **개발 로그**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 기능

- 📤 **일괄 업로드** - MP4/MOV/AVI/MKV/WebM 등 주요 형식 지원
- 🎞️ **프록시 생성** - 빠른 미리보기를 위한 저해상도 프록시 파일 자동 생성
- ✂️ **비디오 분할** - 길이별 자동 비디오 분할
- 🎬 **클립 추출** - 특정 시간 범위 세그먼트 정확 추출
- 📋 **러프컷 구성** - 여러 클립을 러프컷 비디오로 병합
- 🤖 **자동 러프컷** - 인트로/아웃트로 지능적 보존으로 빠른 미리보기
- 📁 **자산 관리** - 비디오 자산 및 메타데이터 통합 관리
- 📊 **처리 로그** - 처리 이력 완전 기록

---

## 🛠️ 기술 스택

| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.10+ | 런타임 환경 |
| FastAPI | 0.109+ | 고성능 비동기 백엔드 API |
| Streamlit | 1.40+ | 프론트엔드 UI |
| FFmpeg | - | 비디오 처리 엔진 |
| Pydantic | v2 | 데이터 검증 및 구성 |
| aiofiles | 23.2+ | 비동기 파일 작업 |

---

## 🏗️ 프로젝트 구조

```
BatchClip/
├── backend/
│   ├── api/                    # API 라우트
│   │   ├── upload.py           # 비디오 업로드 API
│   │   ├── assets.py           # 자산 관리 API
│   │   ├── processing.py       # 전처리 API
│   │   └── editor.py           # 편집 API
│   ├── modules/                # 비즈니스 모듈
│   │   ├── dam.py              # 디지털 자산 관리
│   │   ├── upload_handler.py   # 업로드 핸들러
│   │   ├── preprocessor.py     # 비디오 전처리기
│   │   └── editor.py           # 비디오 편집기
│   ├── config.py               # 구성 관리
│   ├── main.py                 # 애플리케이션 진입점
│   └── requirements.txt        # 백엔드 의존성
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── requirements.txt        # 프론트엔드 의존성
├── start.bat                   # Windows 시작 스크립트
├── start.sh                    # Linux/Mac 시작 스크립트
└── .gitignore
```

---

## 🚀 빠른 시작

### 1. 사전 요구 사항

- Python 3.10+
- FFmpeg (설치 후 PATH에 추가 필수)

**FFmpeg 설치:**

```bash
# Windows (winget 사용)
winget install FFmpeg

# Windows (choco 사용)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2. 원클릭 시작

**Windows:**
```bash
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 3. 수동 시작

**백엔드 시작:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**프론트엔드 시작:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### 4. 접속 URL

- **프론트엔드 UI**: http://localhost:8501
- **백엔드 API**: http://localhost:8000
- **Swagger 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health

---

## 📡 API 엔드포인트

### 업로드 모듈

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/upload/single` | 단일 비디오 업로드 |
| GET | `/api/upload/list` | 업로드 목록 조회 |

### 자산 모듈

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/assets/` | 자산 목록 조회 |
| GET | `/api/assets/{asset_id}` | 자산 상세 조회 |
| GET | `/api/assets/{asset_id}/logs` | 처리 로그 조회 |
| DELETE | `/api/assets/{asset_id}` | 자산 삭제 |

### 처리 모듈

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/processing/{asset_id}/preprocess` | 전체 전처리 |
| POST | `/api/processing/{asset_id}/metadata` | 메타데이터 추출 |
| POST | `/api/processing/{asset_id}/proxy` | 프록시 파일 생성 |
| POST | `/api/processing/{asset_id}/split` | 비디오 분할 |

### 편집기 모듈

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/editor/{asset_id}/clip` | 클립 추출 |
| POST | `/api/editor/{asset_id}/rough-cut` | 러프컷 구성 |
| POST | `/api/editor/{asset_id}/auto-rough-cut` | 자동 러프컷 |

---

## ⚙️ 구성

### 환경 변수 (`backend/.env`)

```env
# 저장 경로
PROCESSING_TEMP_DIR=./temp
FINAL_OUTPUT_DIR=./output
UPLOAD_DIR=./uploads
ASSETS_DIR=./assets

# 저장 유형 (local/oss)
STORAGE_TYPE=local

# FFmpeg 경로 (PATH에 없는 경우)
FFMPEG_PATH=ffmpeg

# 서비스 구성
HOST=0.0.0.0
PORT=8000

# 처리 구성
MAX_UPLOAD_SIZE_MB=500
PROXY_RESOLUTION=720
DEFAULT_SEGMENT_DURATION=60

# 로그 레벨
LOG_LEVEL=INFO
```

---

## 🎬 사용 워크플로우

```
1. 비디오 업로드
   └─> 📤 Upload 페이지에서 MP4/MOV 등 비디오 파일 업로드

2. 전처리
   └─> ⚙️ Processing 페이지에서 프록시 생성/메타데이터 추출

3. 편집 및 클립
   └─> ✂️ Editor 페이지에서 클립 추출 또는 러프컷

4. 결과 확인
   └─> 📁 Assets 페이지에서 출력 파일 관리
```

---

## 📂 디렉토리 설명

| 디렉토리 | 용도 |
|----------|------|
| `uploads/` | 원본 업로드 파일 저장 |
| `assets/` | 자산 메타데이터 JSON 파일 |
| `temp/` | 임시 처리 파일 |
| `output/` | 최종 출력 파일 |

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다.

---

<div align="center">

**Made with ❤️ using Python, FastAPI and FFmpeg**

</div>
