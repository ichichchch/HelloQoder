# AL Agent RAG Backend

RAG Backend for AL Agent - Code Context Retrieval Service using LightRAG and Milvus.

## Features

- **LightRAG**: Graph-based retrieval with entity-relationship extraction
- **Multi-source Data Loading**: Support for web pages, GitHub repos, and PDFs
- **Milvus Vector Store**: High-performance vector similarity search
- **Multiple Query Modes**: naive, local, global, hybrid, mix

## Quick Start

1. Copy `.env.example` to `.env` and configure your API keys
2. Install dependencies: `uv sync`
3. Start the server: `uv run fastapi dev app/main.py --port 8228`

## API Endpoints

- `POST /api/lightrag/insert` - Insert documents with KG extraction
- `POST /api/lightrag/query` - Query with graph-enhanced retrieval
- `POST /api/query` - Traditional vector search
- `POST /api/load/web` - Load web pages
- `POST /api/load/github` - Load GitHub repositories
- `POST /api/load/pdf` - Load PDF documents
