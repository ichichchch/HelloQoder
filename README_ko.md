# HelloQoder

<div align="center">

![Projects](https://img.shields.io/badge/Projects-7-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-9.0%20|%2010.0-512BD4?style=flat-square&logo=dotnet)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Qoder가 작성한 프로젝트 모음**

*AI 기반 에이전틱 코딩 실습*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

</div>

---

## 📂 프로젝트 목록

| 프로젝트 | 설명 | 기술 스택 | 상태 |
|----------|------|-----------|------|
| [ALAgent](./ALAgent/) | 자율 코딩 에이전트 VS Code 확장 | .NET 10, TypeScript, Python, LightRAG | ✅ Active |
| [Glimmer](./Glimmer/) | 데스크탑 및 모바일 AI 자동화 에이전트 | Vue 3, Python, Zhipu GLM-4V | ✅ Active |
| [CartService](./CartService/) | 이커머스 장바구니 마이크로서비스 | FastAPI, PostgreSQL, SQLAlchemy | ✅ Active |
| [NovelTTSApp](./NovelTTSApp/) | 소설을 오디오북으로 변환하는 AI 앱 | .NET 10, Zhipu GLM-TTS, NAudio | ✅ Active |
| [EpubToSplitTxt](./EpubToSplitTxt/) | Epub 전자책 챕터 분할 도구 | .NET 9, VersOne.Epub | ✅ Active |
| [MindMates](./MindMates/) | 정신 건강 AI 동반자 플랫폼 | Vue 3, .NET 10, FastAPI, MiMo | ✅ Active |
| [BatchClip](./BatchClip/) | 자동화 일괄 비디오 편집 도구 | FastAPI, Streamlit, FFmpeg | ✅ Active |

---

## 🏗️ 디렉토리 구조

```
HelloQoder/
├── ALAgent/                 # 🤖 자율 코딩 에이전트
│   ├── frontend-extension/  # VS Code 확장
│   ├── backend-agent/       # .NET 추론 엔진
│   ├── backend-rag/         # Python RAG 서비스
│   └── README.md            # 프로젝트 문서
│
├── Glimmer/                 # 🖥️ 데스크탑 AI 자동화
│   ├── Glimmer-UI/          # Vue 3 프론트엔드
│   ├── Glimmer-Web/         # Python 백엔드
│   ├── Open-AutoGLM/        # 오픈 소스 자동화 라이브러리
│   └── README.md            # 프로젝트 문서
│
├── CartService/             # 🛒 장바구니 마이크로서비스
│   ├── app/                 # 애플리케이션 코드
│   ├── alembic/             # 데이터베이스 마이그레이션
│   └── README.md            # 프로젝트 문서
│
├── NovelTTSApp/             # 🎙️ 소설 음성 변환 앱
│   ├── src/
│   │   ├── Core/            # 코어 레이어 - 도메인 엔티티 및 인터페이스
│   │   ├── Infrastructure/  # 인프라 레이어 - 구현
│   │   └── App/             # 애플리케이션 레이어 - 메인 프로그램
│   └── README.md            # 프로젝트 문서
│
├── EpubToSplitTxt/          # 📖 Epub 분할 도구
│   ├── EpubConverter.cs     # Epub 파서
│   ├── TextSplitter.cs      # 챕터 분할기
│   └── README.md            # 프로젝트 문서
│
├── MindMates/               # 🧠 정신 건강 AI 플랫폼
│   ├── frontend/            # Vue 3 프론트엔드
│   ├── backend-business/    # .NET 10 비즈니스 백엔드
│   ├── backend-ai/          # Python AI 백엔드
│   └── README.md            # 프로젝트 문서
│
├── BatchClip/               # 🎬 일괄 비디오 편집 도구
│   ├── backend/             # FastAPI 백엔드
│   ├── frontend/            # Streamlit 프론트엔드
│   └── start.bat            # 시작 스크립트
│
└── README.md                # 이 파일
```

---

## ✨ 빠른 탐색

### 🤖 ALAgent

자율 코딩 에이전트 VS Code 확장, Microsoft Agent Framework + LangChain + LightRAG 아키텍처 기반.

- **기술 스택**: TypeScript 5.0+ / .NET 10 / Python 3.11+ / LangChain / LightRAG
- **기능**: 지능형 채팅, 코드 검색, 파일 작업, 코드 분석, 지식 그래프 강화 검색
- **아키텍처**: VS Code 확장 + .NET 에이전트 + Python RAG 서비스
- **문서**: [자세히 보기](./ALAgent/README.md)

---

### 🖥️ Glimmer

데스크탑 및 모바일 AI 자동화 에이전트, Zhipu Open-AutoGLM 기반, 크로스 플랫폼 자동화 지원.

- **기술 스택**: Vue 3 / Python 3.10+ / PyAutoGUI / Zhipu GLM-4V
- **기능**: 데스크탑 자동화, 모바일 지원 (Android/iOS/HarmonyOS), AI 시각적 이해
- **아키텍처**: Vue 프론트엔드 + Python 에이전트 서비스
- **문서**: [자세히 보기](./Glimmer/README.md)

---

### 🛒 CartService

고성능 이커머스 장바구니 마이크로서비스, 장바구니 CRUD, 상품 관리, 장바구니 병합 지원.

- **기술 스택**: Python 3.10+ / FastAPI / PostgreSQL / SQLAlchemy 2.0
- **기능**: 장바구니 관리, 상품 CRUD, 장바구니 병합
- **문서**: [자세히 보기](./CartService/README.md)

---

### 🎙️ NovelTTSApp

소설 텍스트를 오디오북으로 변환하는 AI 앱, Zhipu GLM-TTS로 고품질 음성 합성.

- **기술 스택**: .NET 10 / C# 13 / Zhipu GLM-TTS / NAudio
- **기능**: 소설 텍스트 읽기, 스마트 분할, AI 음성 합성, 음성 클로닝
- **아키텍처**: Clean Architecture
- **문서**: [자세히 보기](./NovelTTSApp/README.md)

---

### 📖 EpubToSplitTxt

Epub 전자책 전처리 시스템, `.epub`을 텍스트로 변환하고 지능형 챕터 분할.

- **기술 스택**: .NET 9 / VersOne.Epub / HtmlAgilityPack
- **기능**: Epub 파싱, 챕터 인식, 스마트 분할, UTF-8 출력
- **문서**: [자세히 보기](./EpubToSplitTxt/README.md)

---

### 🧠 MindMates

정신 건강 AI 동반자 플랫폼, 24시간 지능형 심리 상담 서비스 제공.

- **기술 스택**: Vue 3 + TypeScript / .NET 10 / Python FastAPI / MiMo
- **기능**: AI 채팅, 위기 감지, RAG 강화, 모바일 지원
- **아키텍처**: 프론트엔드-백엔드 분리 + AI 마이크로서비스
- **문서**: [자세히 보기](./MindMates/README.md)

---

### 🎬 BatchClip

자동화 일괄 비디오 편집 도구, AI가 소재를 분석하고 자동으로 러프컷 비디오 생성.

- **기술 스택**: Python / FastAPI / Streamlit / FFmpeg
- **기능**: 비디오 업로드, AI 소재 분석, 자동 러프컷, 일괄 처리
- **아키텍처**: 프론트엔드-백엔드 분리
- **문서**: [자세히 보기](./BatchClip/README.md)

---

## 🔧 기술 스택 개요

| 분야 | 기술 |
|------|------|
| **백엔드 서비스** | Python, FastAPI, .NET 10 |
| **프론트엔드** | Vue 3, TypeScript, Vite |
| **AI 통합** | Zhipu GLM-TTS, Zhipu GLM-4V, Xiaomi MiMo, LangChain, LightRAG |
| **데이터베이스** | PostgreSQL, Milvus |
| **비디오 처리** | FFmpeg |
| **배포** | Docker Compose |

---

## 📋 새 프로젝트 추가

1. 루트 디렉토리에 새 프로젝트 폴더 생성
2. 프로젝트 코드와 독립적인 `README.md` 추가
3. 선택 사항: `Agent.md` 및 `Agent&Chat.md` 추가
4. 이 파일의 프로젝트 목록 업데이트

---

<div align="center">

**Made with ❤️ by Qoder**

</div>
