# ALAgent

<div align="center">

![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Agent Framework](https://img.shields.io/badge/Agent%20Framework-Preview-512BD4?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**自主编程智能体 VS Code 扩展**

*基于 [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/) + LangChain + LightRAG 架构，支持多模态 RAG 代码检索与智能编程辅助*

- **开发过程记录**: [Agent&Chat.md](./Agent&Chat.md)

</div>

---

## ✨ 功能特性

- 🤖 **智能对话** - 基于 GPT-4o 的自然语言编程交互
- 🔍 **代码检索** - 多模态 RAG 语义搜索，支持代码上下文理解
- 📁 **文件操作** - 自动读取、写入、搜索项目文件
- 🔧 **代码分析** - 语法树解析、符号提取、代码结构分析
- 🌐 **知识加载** - 支持 Web 页面、GitHub 仓库、PDF 文档索引
- 📊 **图谱检索** - LightRAG 知识图谱增强检索

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| VS Code 扩展 | TypeScript + React + Vite | 5.0+ | 前端界面 |
| 推理引擎 | .NET + Microsoft Agent Framework | 10.0 | Agent 核心 |
| RAG 服务 | Python + FastAPI + LangChain | 3.11+ | 代码检索 |
| 向量数据库 | Milvus | 2.4+ | 向量存储 |
| 知识图谱 | LightRAG | 1.4+ | 图谱增强 |
| AI 模型 | OpenAI GPT-4o / DashScope | - | 推理模型 |

---

## 🏗️ 项目结构

```
ALAgent/
├── frontend-extension/          # VS Code 扩展
│   ├── src/
│   │   ├── core/               # 核心模块
│   │   │   ├── ChatViewProvider.ts
│   │   │   └── types.ts
│   │   ├── services/           # 服务层
│   │   │   ├── AgentClient.ts
│   │   │   ├── FileSystemService.ts
│   │   │   └── TerminalService.ts
│   │   ├── webview/            # Webview UI
│   │   └── extension.ts        # 扩展入口
│   └── package.json
│
├── backend-agent/              # .NET 推理引擎
│   ├── Controllers/            # API 控制器
│   ├── Services/               # Agent 服务
│   ├── Tools/                  # 工具插件
│   │   ├── FileSystemTools.cs
│   │   └── CodeAnalysisTools.cs
│   └── Program.cs              # 应用入口
│
└── backend-rag/                # Python RAG 服务
    ├── app/
    │   ├── chunker.py          # 代码分块
    │   ├── lightrag_service.py # 图谱检索
    │   ├── loaders.py          # 文档加载器
    │   └── main.py             # FastAPI 入口
    ├── scripts/                # 评估脚本
    └── pyproject.toml          # 依赖配置
```

---

## 🚀 快速开始

### 1. 前置要求

- Node.js 18+
- .NET 10 SDK
- Python 3.11+ (推荐使用 uv 包管理器)
- OpenAI 或 DashScope API Key
- Milvus 向量数据库 (可选，生产环境)

### 2. 启动扩展前端

```bash
cd frontend-extension
npm install
npm run watch  # 开发热重载
# 按 F5 在 VS Code 中调试启动
```

### 3. 启动 Agent 后端 (.NET)

```bash
cd backend-agent
# 在 appsettings.json 中配置 API Key
dotnet run --urls=http://localhost:5000
```

### 4. 启动 RAG 服务 (Python)

```bash
cd backend-rag
uv venv && .venv\Scripts\activate  # Windows
uv pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY

# 启动服务
fastapi dev app/main.py --port 8000
```

### 5. 访问地址

- **VS Code 扩展**: 按 F5 启动调试
- **.NET Agent API**: http://localhost:5000
- **RAG API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 📡 API 接口

### Agent API (.NET - Port 5000)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送对话消息 |
| POST | `/api/chat/stream` | 流式对话 |
| GET | `/health` | 健康检查 |

### RAG API (Python - Port 8000)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/query` | 语义代码搜索 |
| POST | `/api/index` | 索引工作空间 |
| POST | `/api/load/web` | 加载 Web 页面 |
| POST | `/api/load/github` | 加载 GitHub 仓库 |
| POST | `/api/load/pdf` | 加载 PDF 文档 |
| POST | `/api/lightrag/query` | 图谱增强检索 |
| GET | `/health` | 健康检查 |

---

## ⚙️ 配置说明

### VS Code 设置

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000",
  "alagent.openaiApiKey": ""
}
```

### Agent 后端 (`appsettings.json`)

```json
{
  "Agent": {
    "OpenAIApiKey": "your-api-key",
    "ModelId": "gpt-4o",
    "RagApiUrl": "http://localhost:8000"
  }
}
```

### RAG 后端 (`.env`)

```env
DASHSCOPE_API_KEY=your_dashscope_key
OPENAI_API_KEY=your_openai_key
MILVUS_HOST=localhost
MILVUS_PORT=19530
TEXT_EMBEDDING_MODEL=text-embedding-v4
LIGHTRAG_QUERY_MODE=hybrid
```

---

## 🧪 测试与评估

### RAG 召回测试

```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/workspace
```

成功标准: Recall@5 > 0.8

---

## 📄 许可证

本项目采用 MIT 许可证。

---

<div align="center">

**Made with ❤️ using Microsoft Agent Framework, LangChain and LightRAG**

</div>
