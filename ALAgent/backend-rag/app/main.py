"""
Main FastAPI application for the RAG service.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import tempfile
import os
from pathlib import Path

from app.config import get_settings
from app.models import (
    QueryRequest, QueryResponse,
    IndexRequest, IndexResponse,
    HealthResponse,
    WebCrawlRequest, GitHubRepoRequest, PDFLoadRequest, URLLoadRequest, LoadResponse,
    MultimodalWebCrawlRequest, MultimodalLoadResponse, MediaItem,
    LightRAGInsertRequest, LightRAGInsertResponse,
    LightRAGQueryRequest, LightRAGQueryResponse,
    LightRAGStatsResponse,
    IndexedSourcesResponse,
)
from app.vector_store import get_vector_store
from app.loaders import WebPageLoader, GitHubRepoLoader, PDFLoader, URLLoader, MultimodalWebPageLoader
from app.lightrag_service import get_lightrag_service

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
    lightrag = get_lightrag_service()
    return HealthResponse(
        status="healthy",
        chroma_connected=store.is_healthy(),
        lightrag_healthy=lightrag.is_healthy(),
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
            "load_web_multimodal": "POST /api/load/web/multimodal",
            "load_github": "POST /api/load/github",
            "load_pdf": "POST /api/load/pdf",
            "load_url": "POST /api/load/url",
            "get_indexed_sources": "GET /api/indexed/sources",
            "lightrag_insert": "POST /api/lightrag/insert",
            "lightrag_query": "POST /api/lightrag/query",
            "lightrag_context": "POST /api/lightrag/context",
            "lightrag_stats": "GET /api/lightrag/stats",
        }
    }


# ==================== Loader Endpoints ====================

@app.post("/api/load/web", response_model=LoadResponse)
async def load_web_pages(request: WebCrawlRequest):
    """
    Crawl and index web pages (text only).
    
    - Supports static HTML and JavaScript-rendered pages (via Playwright)
    - Can follow links up to specified depth
    - Supports sitemap.xml for discovering all pages
    - Converts HTML to clean markdown for indexing
    - For multimodal (images/videos), use POST /api/load/web/multimodal
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


@app.post("/api/load/web/multimodal", response_model=MultimodalLoadResponse)
async def load_web_pages_multimodal(request: MultimodalWebCrawlRequest):
    """
    Crawl and index web pages with multimodal content (images and videos).
    
    使用多模态向量化模型（如 qwen2.5-vl-embedding）对网页中的图片和视频进行向量化。
    
    **Sitemap 使用示例：**
    ```json
    {
      "urls": ["https://example.com"],
      "use_sitemap": true,
      "extract_images": true,
      "extract_videos": true
    }
    ```
    这将自动发现并索引 https://example.com/sitemap.xml 中的所有页面及其图片/视频。
    """
    try:
        store = get_vector_store()
        settings = get_settings()
        
        loader = MultimodalWebPageLoader(
            urls=request.urls,
            use_playwright=request.use_playwright,
            max_depth=request.max_depth,
            same_domain_only=request.same_domain_only,
            extract_images=request.extract_images,
            extract_videos=request.extract_videos,
            min_image_size=request.min_image_size,
            max_images_per_page=request.max_images_per_page,
            download_media=request.download_media,
            use_sitemap=request.use_sitemap,
            sitemap_url=request.sitemap_url,
        )
        
        documents_loaded = 0
        chunks_created = 0
        images_extracted = 0
        videos_extracted = 0
        images_embedded = 0
        videos_embedded = 0
        sources = []
        all_media_items: list[MediaItem] = []
        
        for doc, media_items in loader.load():
            # Index text content
            count = store.index_document(
                content=doc.content,
                source=doc.source,
                source_type=doc.source_type,
                metadata=doc.metadata,
            )
            documents_loaded += 1
            chunks_created += count
            sources.append(doc.source)
            
            # Process media items
            for media in media_items:
                if media.media_type == "image":
                    images_extracted += 1
                else:
                    videos_extracted += 1
                
                # Index media with multimodal embedding
                embedded = False
                if media.base64_data:
                    try:
                        # Store media embedding using multimodal model
                        media_count = store.index_multimodal(
                            content=media.alt_text or f"{media.media_type} from {media.source_page}",
                            media_data=media.base64_data,
                            media_type=media.media_type,
                            source=media.url,
                            source_page=media.source_page,
                            metadata={
                                "alt_text": media.alt_text,
                                "width": media.width,
                                "height": media.height,
                                **media.metadata,
                            }
                        )
                        embedded = media_count > 0
                        if embedded:
                            if media.media_type == "image":
                                images_embedded += 1
                            else:
                                videos_embedded += 1
                    except Exception as e:
                        logger.warning(f"Failed to embed media {media.url}: {e}")
                
                all_media_items.append(MediaItem(
                    url=media.url,
                    media_type=media.media_type,
                    alt_text=media.alt_text,
                    width=media.width,
                    height=media.height,
                    embedded=embedded,
                ))
        
        return MultimodalLoadResponse(
            success=True,
            message=f"Successfully loaded {documents_loaded} pages with {images_extracted} images and {videos_extracted} videos",
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            images_extracted=images_extracted,
            videos_extracted=videos_extracted,
            images_embedded=images_embedded,
            videos_embedded=videos_embedded,
            sources=sources[:20],
            media_items=all_media_items[:50],  # Limit response size
        )
        
    except Exception as e:
        logger.error(f"Multimodal web crawl error: {e}")
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
async def load_pdfs(
    files: list[UploadFile] = File(default=[], description="本地 PDF 文件（可多选）"),
    urls: str = Form(default="", description="远程 PDF URL（多个用逗号分隔）"),
):
    """
    Load and index PDF files.
    
    - 支持直接上传 PDF 文件（可多选）
    - 支持远程 PDF URL（多个用逗号分隔）
    - 提取文本和表格
    - 保留文档结构
    
    使用方式：
    1. 点击 "files" 字段选择本地 PDF 文件（可多选）
    2. 或在 "urls" 字段输入远程 PDF 链接（多个用逗号分隔）
    3. 两者可以同时使用
    """
    try:
        store = get_vector_store()
        
        documents_loaded = 0
        chunks_created = 0
        sources = []
        temp_files = []  # Track temporary files for cleanup
        
        # Process uploaded PDF files
        if files:
            file_paths = []
            for upload_file in files:
                if not upload_file.filename:
                    continue
                    
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, f"upload_{upload_file.filename}")
                
                # Save uploaded file
                with open(temp_path, "wb") as f:
                    content = await upload_file.read()
                    f.write(content)
                
                file_paths.append(temp_path)
                temp_files.append(temp_path)
            
            # Load uploaded PDFs
            if file_paths:
                loader = PDFLoader(file_paths=file_paths)
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
        
        # Process remote PDF URLs
        if urls and urls.strip():
            url_list = [url.strip() for url in urls.split(",") if url.strip()]
            for url in url_list:
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
        
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {cleanup_error}")
        
        if documents_loaded == 0:
            return LoadResponse(
                success=False,
                message="No PDF files provided. Please upload files or provide URLs.",
                documents_loaded=0,
                chunks_created=0,
                sources=[],
            )
        
        return LoadResponse(
            success=True,
            message=f"Successfully loaded {documents_loaded} PDF files",
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            sources=sources,
        )
        
    except Exception as e:
        logger.error(f"PDF load error: {e}")
        # Cleanup on error
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
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


@app.get("/api/indexed/sources", response_model=IndexedSourcesResponse)
async def get_indexed_sources(source_type: str | None = None):
    """
    获取已索引的文档源列表。
    
    用于断点续传，查看哪些页面已经被向量化。
    
    Parameters:
    - source_type: 过滤源类型，例如 "web_multimodal", "web", "pdf", "github"
    
    Returns:
    - total_count: 已索引文档总数
    - sources: 已索引的 URL/路径列表
    
    示例：
    - GET /api/indexed/sources?source_type=web_multimodal
    - GET /api/indexed/sources  (查看所有类型)
    """
    try:
        store = get_vector_store()
        sources = store.get_indexed_sources(source_type)
        
        return IndexedSourcesResponse(
            total_count=len(sources),
            source_type=source_type,
            sources=sources,
        )
        
    except Exception as e:
        logger.error(f"Get indexed sources error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LightRAG Endpoints ====================

@app.post("/api/lightrag/insert", response_model=LightRAGInsertResponse)
async def lightrag_insert(request: LightRAGInsertRequest):
    """
    向 LightRAG 插入文档。
    
    文档会被处理以：
    - 提取实体（Entity Extraction）
    - 提取关系（Relationship Extraction）
    - 构建知识图谱（Knowledge Graph Construction）
    - 生成向量嵌入（Vector Embedding Generation）
    """
    try:
        service = get_lightrag_service()
        result = await service.insert_documents(
            documents=request.documents,
            workspace_path=request.workspace_path,
        )
        return LightRAGInsertResponse(**result)
        
    except Exception as e:
        logger.error(f"LightRAG insert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lightrag/query", response_model=LightRAGQueryResponse)
async def lightrag_query(request: LightRAGQueryRequest):
    """
    使用 LightRAG 进行查询。
    
    支持多种查询模式：
    - naive: 标准向量检索（类似传统 RAG）
    - local: 使用局部知识图谱上下文（实体 + 邻居关系）
    - global: 使用全局图谱模式和社区结构
    - hybrid: 结合 local 和 global 方法
    - mix: 结合所有模式 + 重排序（启用 reranker 时推荐）
    """
    try:
        service = get_lightrag_service()
        result = await service.query(
            query=request.query,
            workspace_path=request.workspace_path,
            mode=request.mode,
            top_k=request.top_k,
            only_need_context=request.only_need_context,
        )
        return LightRAGQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"LightRAG query error: {e}")
        return LightRAGQueryResponse(
            success=False,
            query=request.query,
            mode=request.mode or "hybrid",
            error=str(e),
        )


@app.post("/api/lightrag/context", response_model=LightRAGQueryResponse)
async def lightrag_get_context(request: LightRAGQueryRequest):
    """
    从 LightRAG 获取上下文（不进行 LLM 生成）。
    
    当你想要使用自己的 LLM 处理检索到的上下文时非常有用。
    """
    try:
        service = get_lightrag_service()
        result = await service.query_with_context(
            query=request.query,
            workspace_path=request.workspace_path,
            mode=request.mode,
            top_k=request.top_k,
        )
        return LightRAGQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"LightRAG context error: {e}")
        return LightRAGQueryResponse(
            success=False,
            query=request.query,
            mode=request.mode or "hybrid",
            error=str(e),
        )


@app.get("/api/lightrag/stats", response_model=LightRAGStatsResponse)
async def lightrag_stats(workspace_path: str | None = None):
    """
    获取 LightRAG 知识图谱统计信息。
    """
    try:
        service = get_lightrag_service()
        stats = await service.get_graph_stats(workspace_path)
        return LightRAGStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"LightRAG stats error: {e}")
        return LightRAGStatsResponse(
            status="error",
            message=str(e),
        )
