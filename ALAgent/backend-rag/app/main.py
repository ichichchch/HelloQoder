"""
Main FastAPI application for the RAG service.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.models import (
    QueryRequest, QueryResponse,
    IndexRequest, IndexResponse,
    HealthResponse,
    WebCrawlRequest, GitHubRepoRequest, PDFLoadRequest, URLLoadRequest, LoadResponse,
)
from app.vector_store import get_vector_store
from app.loaders import WebPageLoader, GitHubRepoLoader, PDFLoader, URLLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting RAG service...")
    settings = get_settings()
    logger.info(f"Milvus connection: {settings.milvus_host}:{settings.milvus_port}")
    yield
    logger.info("Shutting down RAG service...")


app = FastAPI(
    title="AL Agent RAG Service",
    description="Code context retrieval service using semantic search",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    store = get_vector_store()
    return HealthResponse(
        status="healthy",
        chroma_connected=store.is_healthy()  # Keep property name for compatibility
    )


@app.post("/api/query", response_model=QueryResponse)
async def query_context(request: QueryRequest):
    """
    Query for relevant code context.
    
    This endpoint performs semantic search over the indexed codebase
    and returns the most relevant code chunks.
    """
    try:
        store = get_vector_store()
        settings = get_settings()
        
        top_k = request.top_k or settings.default_top_k
        
        chunks = store.query(
            query=request.query,
            workspace_path=request.workspace_path,
            top_k=top_k,
        )
        
        return QueryResponse(chunks=chunks)
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index", response_model=IndexResponse)
async def index_workspace(request: IndexRequest):
    """
    Index a workspace for semantic search.
    
    This endpoint processes all code files in the specified workspace,
    chunks them using Tree-sitter, and stores embeddings in ChromaDB.
    """
    try:
        store = get_vector_store()
        
        files_indexed, chunks_created = store.index_workspace(
            workspace_path=request.workspace_path,
            force_reindex=request.force_reindex,
        )
        
        return IndexResponse(
            success=True,
            message=f"Successfully indexed {files_indexed} files",
            files_indexed=files_indexed,
            chunks_created=chunks_created,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AL Agent RAG Service",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "query": "POST /api/query",
            "index_workspace": "POST /api/index",
            "load_web": "POST /api/load/web",
            "load_github": "POST /api/load/github",
            "load_pdf": "POST /api/load/pdf",
            "load_url": "POST /api/load/url",
        }
    }


# ==================== Loader Endpoints ====================

@app.post("/api/load/web", response_model=LoadResponse)
async def load_web_pages(request: WebCrawlRequest):
    """
    Crawl and index web pages.
    
    - Supports static HTML and JavaScript-rendered pages (via Playwright)
    - Can follow links up to specified depth
    - Supports sitemap.xml for discovering all pages
    - Converts HTML to clean markdown for indexing
    """
    try:
        store = get_vector_store()
        settings = get_settings()
        
        loader = WebPageLoader(
            urls=request.urls,
            use_playwright=request.use_playwright,
            max_depth=request.max_depth,
            same_domain_only=request.same_domain_only,
            use_sitemap=request.use_sitemap,
            sitemap_url=request.sitemap_url,
        )
        
        documents_loaded = 0
        chunks_created = 0
        sources = []
        
        for doc in loader.load():
            # Index each document
            count = store.index_document(
                content=doc.content,
                source=doc.source,
                source_type=doc.source_type,
                metadata=doc.metadata,
            )
            documents_loaded += 1
            chunks_created += count
            sources.append(doc.source)
        
        return LoadResponse(
            success=True,
            message=f"Successfully loaded {documents_loaded} web pages",
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            sources=sources,
        )
        
    except Exception as e:
        logger.error(f"Web crawl error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load/github", response_model=LoadResponse)
async def load_github_repo(request: GitHubRepoRequest):
    """
    Clone and index a GitHub repository.
    
    - Clones the repository (shallow clone for speed)
    - Indexes code files based on patterns
    - Supports private repos with GitHub token
    """
    try:
        store = get_vector_store()
        settings = get_settings()
        
        loader = GitHubRepoLoader(
            repo_url=request.repo_url,
            branch=request.branch,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
            github_token=settings.github_token if hasattr(settings, 'github_token') else None,
        )
        
        documents_loaded = 0
        chunks_created = 0
        sources = []
        
        for doc in loader.load():
            count = store.index_document(
                content=doc.content,
                source=doc.source,
                source_type=doc.source_type,
                metadata=doc.metadata,
            )
            documents_loaded += 1
            chunks_created += count
            sources.append(doc.source)
        
        return LoadResponse(
            success=True,
            message=f"Successfully loaded {documents_loaded} files from GitHub repo",
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            sources=sources[:20],  # Limit sources in response
        )
        
    except Exception as e:
        logger.error(f"GitHub load error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load/pdf", response_model=LoadResponse)
async def load_pdfs(request: PDFLoadRequest):
    """
    Load and index PDF files.
    
    - Supports both local files and remote URLs
    - Extracts text and tables from PDFs
    - Preserves document structure
    """
    try:
        store = get_vector_store()
        
        documents_loaded = 0
        chunks_created = 0
        sources = []
        
        # Load local PDFs
        if request.file_paths:
            loader = PDFLoader(file_paths=request.file_paths)
            for doc in loader.load():
                count = store.index_document(
                    content=doc.content,
                    source=doc.source,
                    source_type=doc.source_type,
                    metadata=doc.metadata,
                )
                documents_loaded += 1
                chunks_created += count
                sources.append(doc.source)
        
        # Load remote PDFs
        for url in request.urls:
            loader = URLLoader(url=url)
            for doc in loader.load():
                count = store.index_document(
                    content=doc.content,
                    source=doc.source,
                    source_type=doc.source_type,
                    metadata=doc.metadata,
                )
                documents_loaded += 1
                chunks_created += count
                sources.append(doc.source)
        
        return LoadResponse(
            success=True,
            message=f"Successfully loaded {documents_loaded} PDF files",
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            sources=sources,
        )
        
    except Exception as e:
        logger.error(f"PDF load error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load/url", response_model=LoadResponse)
async def load_from_url(request: URLLoadRequest):
    """
    Load from any URL with automatic type detection.
    
    - Detects if URL is a GitHub repo, PDF, or web page
    - Automatically uses appropriate loader
    - Supports Playwright for JavaScript-rendered pages
    """
    try:
        store = get_vector_store()
        settings = get_settings()
        
        loader = URLLoader(
            url=request.url,
            github_token=settings.github_token if hasattr(settings, 'github_token') else None,
            use_playwright=request.use_playwright,
        )
        
        documents_loaded = 0
        chunks_created = 0
        sources = []
        
        for doc in loader.load():
            count = store.index_document(
                content=doc.content,
                source=doc.source,
                source_type=doc.source_type,
                metadata=doc.metadata,
            )
            documents_loaded += 1
            chunks_created += count
            sources.append(doc.source)
        
        return LoadResponse(
            success=True,
            message=f"Successfully loaded {documents_loaded} documents from URL",
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            sources=sources[:20],
        )
        
    except Exception as e:
        logger.error(f"URL load error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
