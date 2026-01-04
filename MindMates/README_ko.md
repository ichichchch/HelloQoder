# MindMates

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**정신 건강 AI 동반자 플랫폼**

*Xiaomi MiMo LLM 기반의 24시간 지능형 심리 상담 서비스 제공*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

- **개발 로그**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 기능

- ✅ MiMo LLM 기반 지능형 심리 상담 대화
- ✅ RAG 강화된 전문 정신 건강 지식 응답
- ✅ 자동 위기 감지 및 도움 리소스 추천
- ✅ 다중 턴 대화 컨텍스트 메모리
- ✅ 세션 기록 및 관리
- ✅ JWT 사용자 인증 시스템
- ✅ Capacitor 크로스 플랫폼 모바일 지원 (iOS/Android)
- ✅ Docker Compose 원클릭 배포

---

## 🛠️ 기술 스택

| 레이어 | 기술 | 버전 |
|--------|------|------|
| 프론트엔드 프레임워크 | Vue + TypeScript + Vite | 3.5+ |
| UI 컴포넌트 | Element Plus + Tailwind CSS | 2.9+ / 3.4+ |
| 모바일 런타임 | Capacitor | 7.0+ |
| 비즈니스 백엔드 | .NET + Entity Framework Core | 10 |
| AI 백엔드 | Python + FastAPI + LangChain | 3.13 / 0.115+ |
| AI 모델 | Xiaomi MiMo-V2-Flash | - |
| 데이터베이스 | PostgreSQL | 17 |
| 벡터 데이터베이스 | Milvus | 2.4+ |
| 배포 | Docker Compose + Nginx | - |

---

## 🚀 빠른 시작

### 1. 사전 요구 사항

- Node.js 20+
- .NET 10 SDK
- Python 3.13+
- PostgreSQL 17

### 2. 원클릭 시작

```bash
# Windows - 모든 서비스 시작
.\start-all.bat

# 또는 개별 시작
.\start-frontend.bat       # http://localhost:5173
.\start-backend-business.bat  # http://localhost:5000
.\start-backend-ai.bat     # http://localhost:8000
```

### 3. Docker 배포

```bash
# 환경 변수 구성
cp .env.example .env

# 모든 서비스 시작
docker compose up -d
```

---

## 🏗️ 프로젝트 구조

```
MindMates/
├── frontend/                 # Vue 3 프론트엔드 앱
│   ├── src/
│   │   ├── api/             # API 클라이언트
│   │   ├── views/           # 페이지 컴포넌트
│   │   ├── stores/          # Pinia 상태 관리
│   │   └── router/          # 라우트 구성
│   └── capacitor.config.ts  # 모바일 구성
│
├── backend-business/         # .NET 비즈니스 백엔드 (Clean Architecture)
│   ├── MindMates.Api/       # API 레이어
│   ├── MindMates.Application/ # 애플리케이션 레이어
│   ├── MindMates.Domain/    # 도메인 레이어
│   └── MindMates.Infrastructure/ # 인프라 레이어
│
└── backend-ai/              # Python AI 백엔드
    ├── app/
    │   ├── memory/          # 대화 메모리 시스템
    │   ├── services/        # 채팅 서비스
    │   ├── llm.py           # MiMo LLM 통합
    │   ├── rag.py           # RAG 검색 서비스
    │   └── crisis_detector.py # 위기 감지
    └── main.py              # FastAPI 진입점
```

---

## ⚙️ 구성

### 프론트엔드 구성 (`frontend/.env`)

```env
VITE_API_URL=http://localhost:5000
VITE_AI_API_URL=http://localhost:8000
```

### 비즈니스 백엔드 구성 (`backend-business/appsettings.json`)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=mindmates;Username=..."
  },
  "Jwt": {
    "Secret": "your-secret-key-at-least-32-characters",
    "Issuer": "MindMates",
    "Audience": "MindMates"
  }
}
```

### AI 백엔드 구성 (`backend-ai/.env`)

```env
MIMO_API_KEY=your_mimo_api_key
MIMO_API_BASE=https://api.xiaomimimo.com/v1
ZHIPU_API_KEY=your_zhipu_api_key
```

---

## 📡 API 엔드포인트

### 인증 API (비즈니스 백엔드)

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/api/auth/register` | 사용자 등록 |
| POST | `/api/auth/login` | 사용자 로그인 |
| GET | `/api/auth/profile` | 사용자 정보 조회 |
| PUT | `/api/auth/profile` | 사용자 정보 업데이트 |

### 채팅 API (비즈니스 백엔드)

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| GET | `/api/chat/sessions` | 세션 목록 조회 |
| POST | `/api/chat/sessions` | 새 세션 생성 |
| GET | `/api/chat/sessions/:id/messages` | 메시지 기록 조회 |
| POST | `/api/chat/sessions/:id/messages` | 메시지 전송 |

### AI API (AI 백엔드)

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/api/chat` | AI 채팅 인터페이스 |
| GET | `/health` | 헬스 체크 |

---

## 📊 시스템 아키텍처

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend  │────▶│  Backend-Business │────▶│   Backend-AI    │
│  Vue 3 SPA  │     │   .NET 10 API    │     │ FastAPI + MiMo  │
└─────────────┘     └──────────────────┘     └─────────────────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────┐         ┌─────────────┐
                    │  PostgreSQL  │         │   Milvus    │
                    └──────────────┘         └─────────────┘
```

---

## ⚠️ 정신 건강 안내

> 심각한 심리적 고통을 겪고 계신다면, 즉시 전문적인 도움을 받으세요.
> 
> **정신건강 위기상담전화: 1577-0199**

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다.

---

<div align="center">

**Made with ❤️ using Vue 3, .NET 10 and MiMo**

</div>
