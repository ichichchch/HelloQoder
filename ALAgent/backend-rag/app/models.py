from pydantic import BaseModel, Field
from typing import Literal, Optional


class QueryRequest(BaseModel):
    """Request model for code context query."""
    query: str = Field(..., description="The search query")
    workspace_path: str = Field(..., description="Path to the workspace to search")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class CodeChunk(BaseModel):
    """A chunk of code with metadata."""
    content: str = Field(..., description="The code content")
    file_path: str = Field(..., description="Path to the source file")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    score: float = Field(..., description="Relevance score")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class QueryResponse(BaseModel):
    """Response model for code context query."""
    chunks: list[CodeChunk] = Field(default_factory=list, description="Retrieved code chunks")


class IndexRequest(BaseModel):
    """Request model for indexing a workspace."""
    workspace_path: str = Field(..., description="Path to the workspace to index")
    force_reindex: bool = Field(default=False, description="Force re-indexing even if already indexed")


class IndexResponse(BaseModel):
    """Response model for indexing operation."""
    success: bool
    message: str
    files_indexed: int = 0
    chunks_created: int = 0


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "0.1.0"
    chroma_connected: bool = False
    lightrag_healthy: bool = False


# ==================== Loader Models ====================

class WebCrawlRequest(BaseModel):
    """Request for crawling web pages (text only)."""
    urls: list[str] = Field(default=[], description="List of URLs to crawl")
    max_depth: int = Field(default=0, ge=0, le=3, description="Crawl depth (0 = single page)")
    use_playwright: bool = Field(default=False, description="Use Playwright for JS-rendered pages")
    same_domain_only: bool = Field(default=True, description="Only crawl same domain links")
    use_sitemap: bool = Field(default=False, description="Discover pages from sitemap.xml")
    sitemap_url: str | None = Field(default=None, description="Custom sitemap URL (auto-detected if not provided)")


class MultimodalWebCrawlRequest(BaseModel):
    """Request for crawling web pages with multimodal content (images and videos).
    
    使用多模态向量化模型（如 qwen2.5-vl-embedding）对网页中的图片和视频进行向量化。
    支持通过 sitemap.xml 批量发现和索引网站所有页面。
    """
    urls: list[str] = Field(default=[], description="List of URLs to crawl")
    max_depth: int = Field(default=0, ge=0, le=3, description="Crawl depth (0 = single page)")
    use_playwright: bool = Field(default=True, description="Use Playwright for JS-rendered pages (recommended for media)")
    same_domain_only: bool = Field(default=True, description="Only crawl same domain links")
    extract_images: bool = Field(default=True, description="Extract and embed images")
    extract_videos: bool = Field(default=True, description="Extract and embed video thumbnails/frames")
    min_image_size: int = Field(default=100, ge=0, description="Minimum image dimension (width or height) in pixels")
    max_images_per_page: int = Field(default=20, ge=1, le=100, description="Maximum images to extract per page")
    download_media: bool = Field(default=True, description="Download media files for embedding")
    use_sitemap: bool = Field(default=False, description="Discover pages from sitemap.xml")
    sitemap_url: str | None = Field(default=None, description="Custom sitemap URL (auto-detected if not provided)")


class MediaItem(BaseModel):
    """Represents an extracted media item."""
    url: str = Field(..., description="URL of the media")
    media_type: Literal["image", "video"] = Field(..., description="Type of media")
    alt_text: str = Field(default="", description="Alt text or description")
    width: int | None = Field(default=None, description="Width in pixels")
    height: int | None = Field(default=None, description="Height in pixels")
    embedded: bool = Field(default=False, description="Whether embedding was successful")


class MultimodalLoadResponse(BaseModel):
    """Response for multimodal loading operations."""
    success: bool
    message: str
    documents_loaded: int = 0
    chunks_created: int = 0
    images_extracted: int = 0
    videos_extracted: int = 0
    images_embedded: int = 0
    videos_embedded: int = 0
    sources: list[str] = Field(default_factory=list)
    media_items: list[MediaItem] = Field(default_factory=list)


class GitHubRepoRequest(BaseModel):
    """Request for loading GitHub repository."""
    repo_url: str = Field(..., description="GitHub repository URL")
    branch: str = Field(default="main", description="Branch to clone")
    include_patterns: list[str] = Field(default=["*"], description="File patterns to include")
    exclude_patterns: list[str] = Field(
        default=["node_modules/*", ".git/*", "__pycache__/*"],
        description="File patterns to exclude"
    )


class PDFLoadRequest(BaseModel):
    """Request for loading PDF files."""
    file_paths: list[str] = Field(default=[], description="Local PDF file paths")
    urls: list[str] = Field(default=[], description="Remote PDF URLs")


class URLLoadRequest(BaseModel):
    """Request for loading from any URL (auto-detect type)."""
    url: str = Field(..., description="URL to load (web page, GitHub repo, or PDF)")
    use_playwright: bool = Field(default=False, description="Use Playwright for JS-rendered pages")


class LoadResponse(BaseModel):
    """Response for loading operations."""
    success: bool
    message: str
    documents_loaded: int = 0
    chunks_created: int = 0
    sources: list[str] = Field(default_factory=list)


# ==================== LightRAG Models ====================

class LightRAGInsertRequest(BaseModel):
    """请求向 LightRAG 插入文档。
    
    文档会被处理以提取实体、关系，并构建知识图谱。
    """
    documents: list[str] = Field(..., description="要插入的文档列表")
    workspace_path: str | None = Field(default=None, description="工作空间路径（用于命名空间隔离）")


class LightRAGQueryRequest(BaseModel):
    """请求查询 LightRAG。
    
    支持多种查询模式：
    - naive: 标准向量检索（类似传统 RAG）
    - local: 使用局部知识图谱上下文（实体 + 邻居）
    - global: 使用全局图谱模式和社区
    - hybrid: 结合 local 和 global 方法
    - mix: 结合所有模式 + 重排序（启用 reranker 时推荐）
    """
    query: str = Field(..., description="查询字符串")
    workspace_path: str | None = Field(default=None, description="工作空间路径")
    mode: Literal["naive", "local", "global", "hybrid", "mix"] | None = Field(
        default=None, description="查询模式（默认使用配置值）"
    )
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    only_need_context: bool = Field(default=False, description="仅返回上下文，不进行 LLM 生成")


class LightRAGInsertResponse(BaseModel):
    """LightRAG 插入操作响应。"""
    success: bool
    documents_inserted: int = 0
    message: str = ""


class LightRAGQueryResponse(BaseModel):
    """LightRAG 查询响应。"""
    success: bool
    query: str
    mode: str
    result: str | None = None
    error: str | None = None


class LightRAGStatsResponse(BaseModel):
    """LightRAG 统计信息响应。"""
    working_dir: str | None = None
    status: str
    message: str | None = None


class IndexedSourcesResponse(BaseModel):
    """已索引源的响应。"""
    total_count: int
    source_type: str | None = None
    sources: list[str] = Field(default_factory=list)
