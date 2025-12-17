---
trigger: always_on
---
# MindMates Project Rules

## Project Overview
**MindMates** is a psychological counseling AI companion platform using a hybrid architecture.
- **Frontend**: Mobile-first Web App packaged for iOS/Android using **Vue 3** & **Capacitor**.
- **Business Backend**: Core business logic and API gateway using **.NET 10**.
- **AI Backend**: RAG service utilizing **Python 3.13**, **LangChain**, and Xiaomi MiMo-V2-Flash.

## I. Codebase & Structure

### /frontend (Mobile App)
- **Framework**: Vue 3 + TypeScript + Vite
- **Native Runtime**: Capacitor 7 (Bridges web code to iOS/Android)
- **UI Library**: Element Plus (with Custom Mobile Adaptation)
- **CSS Utility**: Tailwind CSS (Recommended for responsive layout)
- **State Management**: Pinia

### /backend-business (Core API)
- **Language**: C# 14 (Preview/Latest)
- **Framework**: .NET 10 Web API
- **Architecture**: Clean Architecture

### /backend-ai (RAG Service)
- **Language**: Python 3.13
- **Framework**: FastAPI
- **Orchestration**: LangChain (Core logic for RAG and Agents)
- **Model Provider**: Xiaomi MiMo-V2-Flash
- **Docs**: [https://platform.xiaomimimo.com/#/docs/welcome](https://platform.xiaomimimo.com/#/docs/welcome)

## II. Dependencies

### Frontend
- `element-plus`: Core UI Library
- `@element-plus/icons-vue`: Icons
- `@capacitor/core`, `@capacitor/ios`, `@capacitor/android`: Native build tools
- `axios`: Networking
- `vue-router`: Navigation

### Backend Business (.NET)
- `Microsoft.EntityFrameworkCore`: ORM (PostgreSQL)
- `Yarp.ReverseProxy`: (Optional) If forwarding requests to Python directly
- `OpenTelemetry`: Observability for .NET 10
- `Microsoft.AspNetCore.Authentication.JwtBearer`: Security

### Backend AI (Python)
- `fastapi` & `uvicorn`: Web Server
- `langchain`: Main framework for chains and retrieval
- `langchain-community`: Community integrations
- `pymilvus`: Vector Store client
- `httpx`: Async requests for MiMo API

## III. Config & Secrets

### Frontend
- Config: `.env`
- **Rule**: Use `import.meta.env.VITE_API_URL`.
- **UI Rule**: Since Element Plus is desktop-first, strictly use `<el-row>` and `<el-col>` for mobile responsiveness, or override styles with media queries.

### Backend Business
- Config: `appsettings.json`
- **Rule**: Use .NET 10 `Options` pattern for configuration injection.

### Backend AI
- Config: `.env`
- **Required Vars**:
  - `MIMO_API_KEY`: API Key for Xiaomi MiMo
  - `MIMO_API_BASE`: Endpoint URL
  - `VECTOR_DB_URI`: Connection string for Vector DB

## IV. Backing Services

- **Main Database**: PostgreSQL 17 (Managed by .NET)
- **Vector Database**: Milvus 2.4+ (Managed by Python/LangChain)
- **Cache**: Redis 7 (Shared)

## V. Build & Run

### Frontend
- Web Dev: `npm run dev`
- **Native Sync**: `npx cap sync`
- iOS Run: `npx cap open ios`
- Android Run: `npx cap open android`

### Backend Business
- Run: `dotnet run --framework net10.0`
- Watch: `dotnet watch`

### Backend AI
- Setup: `uv venv` (Recommended for Python 3.13+) or `python -m venv .venv`
- Install: `pip install -r requirements.txt`
- Run: `fastapi dev main.py`

## VI. Port Binding

- **5173**: Frontend (Vite Default)
- **5000**: .NET Business API (Gateway/Auth)
- **8000**: Python AI Service (Internal RAG)

## VII. Coding Conventions

- **Frontend (Element Plus)**:
  - Use `AutoImport` and `Components` resolvers in Vite config to avoid manual imports.
  - **Mobile Adaptation**: Force inputs and buttons to be larger on mobile via global CSS overrides.
  
- **LangChain Usage**:
  - Use `LCEL` (LangChain Expression Language).
  - Implement custom `Retriever` for the psychological knowledge base.
  
- **Mental Health Context**:
  - **Crisis Detection**: The Python service must classify intent. If `intent == "crisis"`, return immediate help resources.
  - **Tone**: Empathetic, calm, and non-judgmental.
