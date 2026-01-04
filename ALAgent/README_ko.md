# AL Agent

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**자율 코딩 에이전트 VS Code 확장**

*[Cline](https://github.com/cline/cline)에서 영감을 받은 멀티모달 RAG 기술 기반의 고급 AI 코딩 어시스턴트*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

- **개발 로그**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 기능

- 🤖 **지능형 코드 에이전트** - 자연어 명령으로 자율 코딩
- 📚 **멀티모달 RAG** - 시맨틱 검색 및 그래프 기반 쿼리를 통한 향상된 검색
- 🔧 **도구 호출** - 파일 작업, 코드 분석, 시스템 명령
- 🌐 **다중 소스 로딩** - 웹 페이지, GitHub 저장소, PDF에서 인덱싱
- 💬 **컨텍스트 인식 채팅** - 정확한 응답을 위한 대화 컨텍스트 유지

---

## 🏗️ 아키텍처

```
AL Agent
├── frontend-extension/    # VS Code 확장 (TypeScript + React + Vite)
├── backend-agent/         # 추론 엔진 (.NET 10 + Microsoft Agent Framework)
└── backend-rag/          # RAG 서비스 (Python 3.13 + LangChain + LightRAG)
```

---

## 🛠️ 기술 스택

| 계층 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 프론트엔드 | TypeScript + React + Vite | 5.0+ | VS Code 확장 |
| 에이전트 백엔드 | .NET + Microsoft Agent Framework | 10.0 | 추론 엔진 |
| RAG 백엔드 | Python + FastAPI + LangChain | 3.13 | 시맨틱 검색 |
| 벡터 DB | Milvus | 2.4+ | 임베딩 저장 |
| AI 모델 | OpenAI / DashScope | - | LLM 및 임베딩 |

---

## 🚀 빠른 시작

### 사전 요구 사항

- Node.js 18+
- .NET 10 SDK
- Python 3.11+ 및 uv 패키지 관리자
- OpenAI 또는 DashScope API Key
- Milvus 벡터 데이터베이스 (선택 사항, 프로덕션용)

### 1. 프론트엔드 확장

```bash
cd frontend-extension
npm install
npm run watch  # 개발용 핫 리로드
```

디버그: VS Code에서 `F5`를 눌러 디버그 모드로 확장 실행.

### 2. 에이전트 백엔드 (.NET)

```bash
cd backend-agent
# appsettings.json 또는 환경 변수에서 API 키 설정
dotnet run --urls=http://localhost:5000
```

### 3. RAG 백엔드 (Python)

```bash
cd backend-rag
uv venv                    # 가상 환경 생성
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .        # 개발 모드로 설치

# 환경 구성 (복사 및 편집)
cp .env.example .env
# .env에 API 키 설정 (DASHSCOPE_API_KEY 또는 OPENAI_API_KEY)

# 서비스 실행
fastapi dev app/main.py --port 8000
```

---

## 🌐 포트 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| .NET Agent API | 5000 | 프롬프트 수신, 도구 호출 반환 |
| Python RAG API | 8000 | 쿼리 수신, 코드 청크 반환 |
| VS Code 확장 | 내부 | Webview 통신 |

---

## ⚙️ 구성

### VS Code 설정

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000",
  "alagent.openaiApiKey": ""  // VS Code secrets에 안전하게 저장됨
}
```

### 환경 변수

**에이전트 백엔드 (.NET):**
- `Agent__OpenAIApiKey`: OpenAI API 키 (또는 appsettings.json 사용)
- `Agent__ModelId`: 사용할 모델 (기본값: gpt-4o)
- `Agent__RagApiUrl`: RAG 서비스 URL (기본값: http://localhost:8000)

**RAG 백엔드 (Python):**
- `DASHSCOPE_API_KEY`: Qwen 임베딩용 DashScope API 키 (권장)
- `OPENAI_API_KEY`: 대체용 OpenAI API 키
- `MILVUS_HOST/MILVUS_PORT`: 벡터 데이터베이스 연결 (기본값: localhost:19530)
- `TEXT_EMBEDDING_MODEL`: 임베딩 모델 (기본값: text-embedding-v4)
- `LIGHTRAG_QUERY_MODE`: 쿼리 모드 (naive/local/global/hybrid/mix)

---

## 📡 API 엔드포인트

**RAG 서비스**: http://localhost:8000
- `/` - API 문서
- `/health` - 헬스 체크
- `/api/query` - 시맨틱 검색
- `/api/index` - 워크스페이스 인덱싱
- `/api/load/web` - 웹 페이지 로드
- `/api/load/github` - GitHub 저장소 로드
- `/api/load/pdf` - PDF 로드
- `/api/lightrag/query` - 그래프 기반 검색

---

## 🧪 테스트

### RAG 검색 테스트

```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/test/workspace
```

성공 기준: Recall@5 > 0.8

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다.

---

<div align="center">

**Made with ❤️ using .NET 10, Python, and Vision AI**

</div>
