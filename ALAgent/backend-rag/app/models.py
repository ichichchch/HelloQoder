from pydantic import BaseModel, Field
from typing import Optional


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


# ==================== Loader Models ====================

class WebCrawlRequest(BaseModel):
    """Request for crawling web pages."""
    urls: list[str] = Field(default=[], description="List of URLs to crawl")
    max_depth: int = Field(default=0, ge=0, le=3, description="Crawl depth (0 = single page)")
    use_playwright: bool = Field(default=False, description="Use Playwright for JS-rendered pages")
    same_domain_only: bool = Field(default=True, description="Only crawl same domain links")
    use_sitemap: bool = Field(default=False, description="Discover pages from sitemap.xml")
    sitemap_url: str | None = Field(default=None, description="Custom sitemap URL (auto-detected if not provided)")


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
