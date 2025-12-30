# AL Agent - Quick Start Guide

An advanced autonomous coding agent VS Code Extension, inspired by [Cline](https://github.com/cline/cline) and powered by multi-modal RAG technology.

## 🏗️ Architecture

```
AL Agent
├── frontend-extension/    # VS Code Extension (TypeScript + React + Vite)
├── backend-agent/         # Reasoning Engine (.NET 10 + Semantic Kernel)
└── backend-rag/          # RAG Service (Python 3.13 + LangChain + LightRAG)
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- .NET 10 SDK
- Python 3.11+ with uv package manager
- OpenAI or DashScope API Key
- Milvus Vector Database (optional, for production)

### 1. Frontend Extension

```bash
cd frontend-extension
npm install
npm run watch  # Hot reload for development
```

Debug: Press `F5` in VS Code to launch the extension in debug mode.

### 2. Backend Agent (.NET)

```bash
cd backend-agent
# Set your API key in appsettings.json or environment variables
dotnet run --urls=http://localhost:5000
```

### 3. Backend RAG (Python)

```bash
cd backend-rag
uv venv                    # Create virtual environment
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
uv pip install -e .        # Install in development mode

# Configure environment (copy and edit)
cp .env.example .env
# Edit .env with your API keys (DASHSCOPE_API_KEY or OPENAI_API_KEY)

# Run the service
fastapi dev app/main.py --port 8000
```

## 🌐 Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| .NET Agent API | 5000 | Receives prompts, returns tool calls |
| Python RAG API | 8000 | Receives queries, returns code chunks |
| VS Code Extension | Internal | Webview communication |

## ⚙️ Configuration

### VS Code Settings

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000",
  "alagent.openaiApiKey": ""  // Will be stored securely in VS Code secrets
}
```

### Environment Variables

**Backend Agent (.NET):**
- `Agent__OpenAIApiKey`: OpenAI API key (or use appsettings.json)
- `Agent__ModelId`: Model to use (default: gpt-4o)
- `Agent__RagApiUrl`: RAG service URL (default: http://localhost:8000)

**Backend RAG (Python):**
- `DASHSCOPE_API_KEY`: DashScope API key for Qwen embeddings (recommended)
- `OPENAI_API_KEY`: OpenAI API key as fallback
- `MILVUS_HOST/MILVUS_PORT`: Vector database connection (default: localhost:19530)
- `TEXT_EMBEDDING_MODEL`: Embedding model (default: text-embedding-v4)
- `LIGHTRAG_QUERY_MODE`: Query mode (naive/local/global/hybrid/mix)

### Environment Variable Priority

⚠️ **Important**: System environment variables have higher priority than `.env` files.
- If `.env` changes don't take effect, check system environment variables
- After modifying system environment variables, restart your terminal

## 🧪 Testing & Evaluation

### RAG Retrieval Testing
```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/test/workspace
```

Success criteria: Recall@5 > 0.8

### Available Endpoints

**RAG Service**: http://localhost:8000
- `/` - API documentation
- `/health` - Health check
- `/api/query` - Semantic search
- `/api/index` - Index workspace
- `/api/load/web` - Load web pages
- `/api/load/github` - Load GitHub repos
- `/api/load/pdf` - Load PDFs
- `/api/lightrag/query` - Graph-based retrieval
