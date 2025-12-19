# MindMates

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**心理健康 AI 伴侣平台**

*提供 7x24 小时智能心理咨询服务，基于小米 MiMo 大模型*

- **开发过程记录**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 功能特性

- ✅ 基于 MiMo 大模型的智能心理咨询对话
- ✅ RAG 增强的专业心理知识回答
- ✅ 自动危机检测与求助资源推荐
- ✅ 多轮对话上下文记忆
- ✅ 会话历史记录与管理
- ✅ JWT 用户认证体系
- ✅ Capacitor 跨平台移动端支持 (iOS/Android)
- ✅ Docker Compose 一键部署

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue + TypeScript + Vite | 3.5+ |
| UI 组件 | Element Plus + Tailwind CSS | 2.9+ / 3.4+ |
| 移动运行时 | Capacitor | 7.0+ |
| 业务后端 | .NET + Entity Framework Core | 10 |
| AI 后端 | Python + FastAPI + LangChain | 3.13 / 0.115+ |
| AI 模型 | Xiaomi MiMo-V2-Flash | - |
| 数据库 | PostgreSQL | 17 |
| 向量数据库 | Milvus | 2.4+ |
| 部署 | Docker Compose + Nginx | - |

---

## 🚀 快速开始

### 1. 前置要求

- Node.js 20+
- .NET 10 SDK
- Python 3.13+
- PostgreSQL 17

### 2. 一键启动

```bash
# Windows - 启动所有服务
.\start-all.bat

# 或分别启动
.\start-frontend.bat       # http://localhost:5173
.\start-backend-business.bat  # http://localhost:5000
.\start-backend-ai.bat     # http://localhost:8000
```

### 3. Docker 部署

```bash
# 配置环境变量
cp .env.example .env

# 启动所有服务
docker compose up -d
```

---

## 🏗️ 项目结构

```
MindMates/
├── frontend/                 # Vue 3 前端应用
│   ├── src/
│   │   ├── api/             # API 客户端
│   │   ├── views/           # 页面组件
│   │   ├── stores/          # Pinia 状态管理
│   │   └── router/          # 路由配置
│   └── capacitor.config.ts  # 移动端配置
│
├── backend-business/         # .NET 业务后端 (Clean Architecture)
│   ├── MindMates.Api/       # API 层
│   ├── MindMates.Application/ # 应用层
│   ├── MindMates.Domain/    # 领域层
│   └── MindMates.Infrastructure/ # 基础设施层
│
└── backend-ai/              # Python AI 后端
    ├── app/
    │   ├── memory/          # 对话记忆系统
    │   ├── services/        # 聊天服务
    │   ├── llm.py           # MiMo LLM 集成
    │   ├── rag.py           # RAG 检索服务
    │   └── crisis_detector.py # 危机检测
    └── main.py              # FastAPI 入口
```

---

## ⚙️ 配置说明

### 前端配置 (`frontend/.env`)

```env
VITE_API_URL=http://localhost:5000
VITE_AI_API_URL=http://localhost:8000
```

### 业务后端配置 (`backend-business/appsettings.json`)

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

### AI 后端配置 (`backend-ai/.env`)

```env
MIMO_API_KEY=your_mimo_api_key
MIMO_API_BASE=https://api.xiaomimimo.com/v1
ZHIPU_API_KEY=your_zhipu_api_key
```

---

## 📡 API 端点

### 认证 API (业务后端)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/profile` | 获取用户信息 |
| PUT | `/api/auth/profile` | 更新用户信息 |

### 聊天 API (业务后端)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/chat/sessions` | 获取会话列表 |
| POST | `/api/chat/sessions` | 创建新会话 |
| GET | `/api/chat/sessions/:id/messages` | 获取消息历史 |
| POST | `/api/chat/sessions/:id/messages` | 发送消息 |

### AI API (AI 后端)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/chat` | AI 对话接口 |
| GET | `/health` | 健康检查 |

---

## 📊 系统架构

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

## ⚠️ 心理健康提示

> 如果您正在经历严重的心理困扰，请及时寻求专业帮助。
> 
> **全国心理援助热线: 400-161-9995**

---

## 📄 许可证

本项目采用 MIT 许可证。

---

<div align="center">

**Made with ❤️ using Vue 3, .NET 10 and MiMo**

</div>
