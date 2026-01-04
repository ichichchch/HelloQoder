# AL Agent

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**自主编程 Agent VS Code 扩展**

*基于多模态 RAG 技术的高级 AI 编程助手，灵感来源于 [Cline](https://github.com/cline/cline)*

[English](./README.md) | 中文 | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **开发过程记录**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 功能特性

- 🤖 **智能代码 Agent** - 使用自然语言指令自主编程
- 📚 **多模态 RAG** - 基于语义搜索和图检索的增强检索
- 🔧 **工具调用** - 文件操作、代码分析、系统命令
- 🌐 **多源加载** - 从网页、GitHub 仓库和 PDF 建立索引
- 💬 **上下文感知对话** - 维护对话上下文以提供准确响应

---

## 🏗️ 架构

```
AL Agent
├── frontend-extension/    # VS Code 扩展 (TypeScript + React + Vite)
├── backend-agent/         # 推理引擎 (.NET 10 + Microsoft Agent Framework)
└── backend-rag/          # RAG 服务 (Python 3.13 + LangChain + LightRAG)
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端 | TypeScript + React + Vite | 5.0+ | VS Code 扩展 |
| Agent 后端 | .NET + Microsoft Agent Framework | 10.0 | 推理引擎 |
| RAG 后端 | Python + FastAPI + LangChain | 3.13 | 语义搜索 |
| 向量数据库 | Milvus | 2.4+ | 向量存储 |
| AI 模型 | OpenAI / DashScope | - | LLM 及 Embeddings |

---

## 🚀 快速开始

### 前置要求

- Node.js 18+
- .NET 10 SDK
- Python 3.11+ 及 uv 包管理器
- OpenAI 或 DashScope API Key
- Milvus 向量数据库（可选，用于生产环境）

### 1. 前端扩展

```bash
cd frontend-extension
npm install
npm run watch  # 开发热重载
```

调试：在 VS Code 中按 `F5` 以调试模式启动扩展。

### 2. Agent 后端 (.NET)

```bash
cd backend-agent
# 在 appsettings.json 或环境变量中设置 API Key
dotnet run --urls=http://localhost:5000
```

### 3. RAG 后端 (Python)

```bash
cd backend-rag
uv venv                    # 创建虚拟环境
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .        # 以开发模式安装

# 配置环境（复制并编辑）
cp .env.example .env
# 编辑 .env 设置 API Key (DASHSCOPE_API_KEY 或 OPENAI_API_KEY)

# 运行服务
fastapi dev app/main.py --port 8000
```

---

## 🌐 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| .NET Agent API | 5000 | 接收提示，返回工具调用 |
| Python RAG API | 8000 | 接收查询，返回代码片段 |
| VS Code 扩展 | 内部 | Webview 通信 |

---

## ⚙️ 配置

### VS Code 设置

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000",
  "alagent.openaiApiKey": ""  // 将安全存储在 VS Code secrets 中
}
```

### 环境变量

**Agent 后端 (.NET):**
- `Agent__OpenAIApiKey`: OpenAI API key（或使用 appsettings.json）
- `Agent__ModelId`: 使用的模型（默认: gpt-4o）
- `Agent__RagApiUrl`: RAG 服务 URL（默认: http://localhost:8000）

**RAG 后端 (Python):**
- `DASHSCOPE_API_KEY`: 用于 Qwen embeddings 的 DashScope API key（推荐）
- `OPENAI_API_KEY`: OpenAI API key 作为备选
- `MILVUS_HOST/MILVUS_PORT`: 向量数据库连接（默认: localhost:19530）
- `TEXT_EMBEDDING_MODEL`: Embedding 模型（默认: text-embedding-v4）
- `LIGHTRAG_QUERY_MODE`: 查询模式（naive/local/global/hybrid/mix）

---

## 📡 API 端点

**RAG 服务**: http://localhost:8000
- `/` - API 文档
- `/health` - 健康检查
- `/api/query` - 语义搜索
- `/api/index` - 索引工作区
- `/api/load/web` - 加载网页
- `/api/load/github` - 加载 GitHub 仓库
- `/api/load/pdf` - 加载 PDF
- `/api/lightrag/query` - 图检索

---

## 🧪 测试

### RAG 检索测试

```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/test/workspace
```

成功标准: Recall@5 > 0.8

---

## 📄 许可证

本项目采用 MIT 许可证。

---

<div align="center">

**Made with ❤️ using .NET 10, Python, and Vision AI**

</div>
