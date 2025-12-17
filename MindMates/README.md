# MindMates - 心理健康AI伴侣平台

## 项目概述

MindMates 是一个心理咨询AI伴侣平台，采用混合架构设计：

- **前端**: Vue 3 + TypeScript + Vite + Capacitor (移动优先)
- **业务后端**: .NET 10 Web API (Clean Architecture)
- **AI后端**: Python 3.13 + FastAPI + LangChain + MiMo

## 快速开始

### 前置要求

- Node.js 20+
- .NET 10 SDK
- Python 3.13+
- PostgreSQL 17
- Redis 7 (可选)

### 启动所有服务

```bash
# Windows
.\start-all.bat

# 或分别启动
.\start-frontend.bat
.\start-backend-business.bat
.\start-backend-ai.bat
```

### 单独启动服务

#### 前端 (端口 5173)
```bash
cd frontend
npm install
npm run dev
```

#### 业务后端 (端口 5000)
```bash
cd backend-business/MindMates.Api
dotnet restore
dotnet run
```

#### AI后端 (端口 8000)
```bash
cd backend-ai
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
fastapi dev main.py
```

## 项目结构

```
MindMates/
├── frontend/                 # Vue 3 前端应用
│   ├── src/
│   │   ├── api/             # API 服务层
│   │   ├── components/      # Vue 组件
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── styles/          # 全局样式
│   │   ├── types/           # TypeScript 类型
│   │   └── views/           # 页面视图
│   ├── capacitor.config.ts  # Capacitor 配置
│   └── vite.config.ts       # Vite 配置
│
├── backend-business/         # .NET 业务后端
│   ├── MindMates.Api/       # API 层
│   ├── MindMates.Application/ # 应用层
│   ├── MindMates.Domain/    # 领域层
│   └── MindMates.Infrastructure/ # 基础设施层
│
└── backend-ai/              # Python AI 后端
    ├── app/
    │   ├── config.py        # 配置管理
    │   ├── models.py        # 数据模型
    │   ├── llm.py           # MiMo LLM 集成
    │   ├── rag.py           # RAG 检索服务
    │   ├── crisis_detector.py # 危机检测
    │   └── services/        # 业务服务
    └── main.py              # FastAPI 入口
```

## 配置说明

### 前端配置 (.env)
```env
VITE_API_URL=http://localhost:5000
VITE_AI_API_URL=http://localhost:8000
```

### 业务后端配置 (appsettings.json)
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=mindmates;..."
  },
  "Jwt": {
    "Secret": "your-secret-key",
    "Issuer": "MindMates",
    "Audience": "MindMates"
  }
}
```

### AI后端配置 (.env)
```env
MIMO_API_KEY=your_mimo_api_key
MIMO_API_BASE=https://api.xiaomimimo.com/v1
```

## 核心功能

### 1. 用户认证
- 注册/登录
- JWT Token 认证
- 个人资料管理

### 2. 心理咨询对话
- 实时AI对话
- 对话历史记录
- 多会话管理

### 3. 危机检测
- 自动检测危机关键词
- 提供紧急求助资源
- 心理援助热线推荐

### 4. 移动端支持
- Capacitor 跨平台打包
- iOS/Android 原生应用
- 响应式移动端UI

## API 端点

### 认证 API
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/profile` - 更新用户信息

### 聊天 API
- `GET /api/chat/sessions` - 获取会话列表
- `POST /api/chat/sessions` - 创建新会话
- `GET /api/chat/sessions/:id/messages` - 获取消息
- `POST /api/chat/sessions/:id/messages` - 发送消息

### AI API
- `POST /api/chat` - AI 对话接口
- `GET /health` - 健康检查

## 技术栈详情

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue | 3.5+ |
| 状态管理 | Pinia | 2.3+ |
| UI组件 | Element Plus | 2.9+ |
| CSS框架 | Tailwind CSS | 3.4+ |
| 移动运行时 | Capacitor | 7.0+ |
| 业务后端 | .NET | 10 |
| ORM | Entity Framework Core | 10 |
| AI后端 | FastAPI | 0.115+ |
| LLM集成 | LangChain | 0.3+ |
| AI模型 | Xiaomi MiMo-V2-Flash | - |
| 数据库 | PostgreSQL | 17 |
| 向量数据库 | Milvus | 2.4+ |

## 心理健康提示

> 如果您正在经历严重的心理困扰，请及时寻求专业帮助。
> 
> **全国心理援助热线: 400-161-9995**

## License

MIT License
