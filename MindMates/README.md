# MindMates

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Mental Health AI Companion Platform**

*Providing 24/7 intelligent psychological counseling services, powered by Xiaomi MiMo LLM*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Development Log**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Features

- ✅ Intelligent psychological counseling dialogue based on MiMo LLM
- ✅ RAG-enhanced professional mental health knowledge responses
- ✅ Automatic crisis detection and help resource recommendations
- ✅ Multi-turn conversation context memory
- ✅ Session history records and management
- ✅ JWT user authentication system
- ✅ Capacitor cross-platform mobile support (iOS/Android)
- ✅ Docker Compose one-click deployment

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend Framework | Vue + TypeScript + Vite | 3.5+ |
| UI Components | Element Plus + Tailwind CSS | 2.9+ / 3.4+ |
| Mobile Runtime | Capacitor | 7.0+ |
| Business Backend | .NET + Entity Framework Core | 10 |
| AI Backend | Python + FastAPI + LangChain | 3.13 / 0.115+ |
| AI Model | Xiaomi MiMo-V2-Flash | - |
| Database | PostgreSQL | 17 |
| Vector Database | Milvus | 2.4+ |
| Deployment | Docker Compose + Nginx | - |

---

## 🚀 Quick Start

### 1. Prerequisites

- Node.js 20+
- .NET 10 SDK
- Python 3.13+
- PostgreSQL 17

### 2. One-Click Start

```bash
# Windows - Start all services
.\start-all.bat

# Or start separately
.\start-frontend.bat       # http://localhost:5173
.\start-backend-business.bat  # http://localhost:5000
.\start-backend-ai.bat     # http://localhost:8000
```

### 3. Docker Deployment

```bash
# Configure environment variables
cp .env.example .env

# Start all services
docker compose up -d
```

---

## 🏗️ Project Structure

```
MindMates/
├── frontend/                 # Vue 3 Frontend App
│   ├── src/
│   │   ├── api/             # API Client
│   │   ├── views/           # Page Components
│   │   ├── stores/          # Pinia State Management
│   │   └── router/          # Route Config
│   └── capacitor.config.ts  # Mobile Config
│
├── backend-business/         # .NET Business Backend (Clean Architecture)
│   ├── MindMates.Api/       # API Layer
│   ├── MindMates.Application/ # Application Layer
│   ├── MindMates.Domain/    # Domain Layer
│   └── MindMates.Infrastructure/ # Infrastructure Layer
│
└── backend-ai/              # Python AI Backend
    ├── app/
    │   ├── memory/          # Conversation Memory System
    │   ├── services/        # Chat Services
    │   ├── llm.py           # MiMo LLM Integration
    │   ├── rag.py           # RAG Retrieval Service
    │   └── crisis_detector.py # Crisis Detection
    └── main.py              # FastAPI Entry
```

---

## ⚙️ Configuration

### Frontend Config (`frontend/.env`)

```env
VITE_API_URL=http://localhost:5000
VITE_AI_API_URL=http://localhost:8000
```

### Business Backend Config (`backend-business/appsettings.json`)

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

### AI Backend Config (`backend-ai/.env`)

```env
MIMO_API_KEY=your_mimo_api_key
MIMO_API_BASE=https://api.xiaomimimo.com/v1
ZHIPU_API_KEY=your_zhipu_api_key
```

---

## 📡 API Endpoints

### Auth API (Business Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User Registration |
| POST | `/api/auth/login` | User Login |
| GET | `/api/auth/profile` | Get User Info |
| PUT | `/api/auth/profile` | Update User Info |

### Chat API (Business Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/sessions` | Get Session List |
| POST | `/api/chat/sessions` | Create New Session |
| GET | `/api/chat/sessions/:id/messages` | Get Message History |
| POST | `/api/chat/sessions/:id/messages` | Send Message |

### AI API (AI Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | AI Chat Interface |
| GET | `/health` | Health Check |

---

## 📊 System Architecture

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

## ⚠️ Mental Health Notice

> If you are experiencing serious psychological distress, please seek professional help promptly.
> 
> **National Mental Health Hotline (US): 988**
> **Crisis Text Line: Text HOME to 741741**

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Made with ❤️ using Vue 3, .NET 10 and MiMo**

</div>
