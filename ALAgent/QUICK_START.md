# AL Agent

An autonomous coding agent VS Code Extension, inspired by [Cline](https://github.com/cline/cline).

## Architecture

```
AL Agent
├── frontend-extension/    # VS Code Extension (TypeScript + React)
├── backend-agent/         # Reasoning Engine (.NET + Semantic Kernel)
└── backend-rag/          # RAG Service (Python + LangChain)
```

## Quick Start

### Prerequisites

- Node.js 18+
- .NET 9 SDK
- Python 3.11+ with uv
- OpenAI API Key

### 1. Frontend Extension

```bash
cd frontend-extension
npm install
npm run watch
```

Debug: Press `F5` in VS Code to launch the extension.

### 2. Backend Agent (.NET)

```bash
cd backend-agent
# Set your OpenAI API key in appsettings.json or environment
dotnet run --urls=http://localhost:5000
```

### 3. Backend RAG (Python)

```bash
cd backend-rag
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Copy and configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run the service
fastapi dev app/main.py --port 8000
```

## Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| .NET Agent API | 5000 | Receives prompts, returns tool calls |
| Python RAG API | 8000 | Receives queries, returns code chunks |

## Configuration

### VS Code Settings

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000"
}
```

### Environment Variables

**Backend Agent (.NET):**
- `Agent__OpenAIApiKey`: OpenAI API key
- `Agent__ModelId`: Model to use (default: gpt-4o)

**Backend RAG (Python):**
- `OPENAI_API_KEY`: OpenAI API key for embeddings
- `CHROMA_PERSIST_DIRECTORY`: Path for ChromaDB storage

## Testing RAG Retrieval

```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/test/workspace
```

Success criteria: Recall@5 > 0.8
