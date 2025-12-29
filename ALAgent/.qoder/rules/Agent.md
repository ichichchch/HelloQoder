---
trigger: always_on
---
# AL Agent Project Rules

## Project Overview
**AL Agent** is an autonomous coding agent VS Code Extension, inspired by the architecture of [Cline](https://github.com/cline/cline).
- **Frontend (Host/Body)**: VS Code Extension handling UI, File System Access, and Terminal Execution using **TypeScript**.
- **Agent Backend (Brain)**: Reasoning engine using **.NET 10** and **Microsoft Agent Framework**, responsible for planning and tool invocation strategy.
- **RAG Backend (Memory)**: Context retrieval service using **Python 3.13** & **LangChain**, with a strict focus on retrieval quality (Recall/Precision).

## I. Codebase & Structure

### `/frontend-extension` (VS Code)
- **Framework**: TypeScript + Vite + React (Webview).
- **Architecture**: Follows [Cline's Source Structure](https://github.com/cline/cline/tree/main/src):
  - `src/core`: Core logic for `webview <-> extension` message passing.
  - `src/services`: Interfaces for FileSystem and Terminal (Implementation similar to MCP).
- **Role**: Handles UI rendering and acts as the **Tool Executor** for the .NET Agent (e.g., physically writing files or running shell commands).

### `/backend-agent` (Reasoning Core)
- **Language**: C# 14 (.NET 10).
- **Framework**: Microsoft Agent Framework.
- **Role**:
  - Receives `User Prompt` + `Context` from Frontend.
  - Decides which tool to use (e.g., `list_files`, `read_file`, `execute_command`).
  - Returns structured "Thought" and "Call" payloads back to the Frontend.

### `/backend-rag` (Knowledge Service)
- **Language**: Python 3.13.
- **Framework**: FastAPI + LangChain.
- **Key Feature**: **Evaluation-Driven Development**.
- **Role**: Indexes the user's workspace code and documentation. Provides relevant context chunks to the .NET Agent based on semantic queries.

## II. Dependencies

### Frontend (TypeScript)
- `vscode`: Official Extension API.
- `@vscode/webview-ui-toolkit`: Native VS Code look-and-feel.
- `react`, `react-dom`: Webview UI rendering.
- `zod`: Strict type validation for JSON-RPC messages between Webview and .NET/Host.
- `axios`: For HTTP communication with local .NET/Python servers.

### Backend Agent (.NET)
- `Microsoft.SemanticKernel`: Core Agent orchestration and planning.
- `Microsoft.SemanticKernel.Connectors.OpenAI`: LLM connectivity.
- `Refit`: Type-safe REST client for communicating with the Python RAG service.
- `System.CommandLine`: For robust CLI argument handling.

### Backend RAG (Python)
- `fastapi`, `uvicorn`: High-performance API Server.
- `langchain`: Retrieval logic and chain orchestration.
- `ragas`: **Mandatory** framework for testing Retrieval Recall and Precision.
- `pymilvus`: Milvus Vector Store client.
- `tree-sitter`: For AST-based code chunking (superior to regex/text splitting).
- **Data Loaders**:
  - `beautifulsoup4`, `playwright`: Web page crawling (static and JS-rendered).
  - `pygithub`, `gitpython`: GitHub repository loading.
  - `pypdf`, `pdfplumber`: PDF document extraction.

## III. Config & Secrets

### Frontend
- **Config**: VS Code `settings.json` (Namespace: `clinenet.*`).
- **Secrets**: Use `context.secrets` API to store sensitive data (e.g., OpenAI Key). Pass these to backends via secure headers or initialization payloads.

### Backend Agent
- **Config**: `appsettings.json`.
- **Rule**: Map User Options from VS Code settings directly to .NET `IOptions<AgentSettings>`.

### Backend RAG
- **Config**: `.env`.
- **Required Variables**:
  - `OPENAI_API_KEY`: Required for embedding generation.
  - `EVALUATION_DATASET`: Path to the golden dataset for recall testing.
  - `GITHUB_TOKEN`: (Optional) For accessing private GitHub repositories.
  - `MILVUS_HOST`, `MILVUS_PORT`: Milvus vector database connection.

## IV. Backing Services

- **Vector Database**: Milvus (Running as a standalone service or via Docker).
- **Communication Bus**:
  - **Frontend -> .NET**: HTTP (Localhost) or WebSocket.
  - **.NET -> Python**: gRPC (Preferred) or HTTP.

## V. Build & Run

### Frontend
- **Dev**: `npm run watch` (Watches both Webview and Extension host).
- **Debug**: Press `F5` in VS Code (Launch Extension).

### Backend Agent
- **Run**: `dotnet run --urls=http://localhost:5000`
- **Architecture Note**: In production, this service should be packaged as a self-contained executable bundled within the extension VSIX.

### Backend RAG
- **Setup**: `uv venv` -> `source .venv/bin/activate`.
- **Run**: `fastapi dev main.py --port 8000`.
- **Test Recall**: `python scripts/evaluate_recall.py`
  - **Success Criteria**: Recall@5 > 0.8 (Must recall at least 80% of relevant code context).

## VI. Port Binding

- **5000**: .NET Agent API (Receives prompts, returns tool calls).
- **8000**: Python RAG API (Receives queries, returns code chunks).
- **Webview**: Internal VS Code mechanism (No external port exposed).

## VII. Coding Conventions

### Frontend (Cline Style)
- **Message Protocol**: Use a strictly typed `Message` discriminated union for all communication.
  ```typescript
  type Message = { type: 'ask', payload: string } | { type: 'say', text: string };
  - **State Management**: Implement a distinct State Machine (e.g., `Idle`, `Thinking`, `Executing`, `Error`) to drive UI updates.
- **Sandboxing**: The Webview **must not** contain business logic. It strictly displays data. The Extension Host process handles actual logic and system access.

### Agent (.NET)
- **Tool Definitions**: Define capabilities using the `[KernelFunction]` attribute.
- **Output Parsing**: Ensure the Agent produces strictly structured output (JSON) so the Frontend can reliably parse and execute commands.

### RAG (Python)
- **Recall Testing**:
  - Every Pull Request involving changes to the chunking strategy **MUST** run the evaluation script.
  - Use `ragas` to generate synthetic test data from the codebase to benchmark retrieval quality.
- **Chunking Strategy**: Prioritize logical boundaries (Class/Function) using `tree-sitter` over arbitrary fixed character counts.
- **Data Sources**: Support multiple data sources for knowledge ingestion:
  - **Code Workspace**: Local code files indexed with AST-based chunking.
  - **Web Pages**: Crawl and convert HTML to markdown.
  - **GitHub Repos**: Clone and index repository contents.
  - **PDF Documents**: Extract text and tables from PDFs.
```