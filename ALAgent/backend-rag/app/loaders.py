"""
Data loaders for various sources: Web pages, GitHub repos, and PDF files.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse, urljoin
import logging
import tempfile
import shutil
import xml.etree.ElementTree as ET

import httpx
from bs4 import BeautifulSoup
import html2text

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a loaded document with content and metadata."""
    content: str
    source: str
    source_type: str  # "web", "github", "pdf", "file"
    title: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class MediaDocument:
    """Represents a media item (image/video) with its data."""
    url: str
    media_type: str  # "image" or "video"
    data: bytes | None = None  # Raw binary data
    base64_data: str | None = None  # Base64 encoded data
    alt_text: str = ""
    width: int | None = None
    height: int | None = None
    source_page: str = ""
    metadata: dict = field(default_factory=dict)


class BaseLoader(ABC):
    """Base class for all document loaders."""
    
    @abstractmethod
    def load(self) -> Generator[Document, None, None]:
        """Load documents from the source."""
        pass


class WebPageLoader(BaseLoader):
    """
    Load content from web pages.
    Supports both static HTML and JavaScript-rendered pages (via Playwright).
    Also supports sitemap.xml for discovering all pages on a site.
    """

    def __init__(
        self,
        urls: list[str],
        use_playwright: bool = False,
        max_depth: int = 0,
        same_domain_only: bool = True,
        use_sitemap: bool = False,
        sitemap_url: str | None = None,
    ):
        self.urls = urls
        self.use_playwright = use_playwright
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.use_sitemap = use_sitemap
        self.sitemap_url = sitemap_url
        self._visited: set[str] = set()
        self._html_converter = html2text.HTML2Text()
        self._html_converter.ignore_links = False
        self._html_converter.ignore_images = True
        self._html_converter.body_width = 0

    def load(self) -> Generator[Document, None, None]:
        """Load web pages and convert to markdown."""
        # If using sitemap, discover URLs first
        if self.use_sitemap:
            sitemap_urls = self._load_from_sitemap()
            for url in sitemap_urls:
                yield from self._load_url(url, depth=0)
        
        # Then load explicitly provided URLs
        for url in self.urls:
            yield from self._load_url(url, depth=0)

    def _load_from_sitemap(self) -> list[str]:
        """
        Load URLs from sitemap.xml.
        Supports standard sitemap and sitemap index files.
        """
        urls = []
        
        # Determine sitemap URL
        if self.sitemap_url:
            sitemap_urls_to_check = [self.sitemap_url]
        elif self.urls:
            # Try common sitemap locations
            parsed = urlparse(self.urls[0])
            base = f"{parsed.scheme}://{parsed.netloc}"
            sitemap_urls_to_check = [
                f"{base}/sitemap.xml",
                f"{base}/sitemap_index.xml",
                f"{base}/sitemap/sitemap.xml",
            ]
        else:
            return urls
        
        for sitemap_url in sitemap_urls_to_check:
            try:
                fetched_urls = self._parse_sitemap(sitemap_url)
                if fetched_urls:
                    urls.extend(fetched_urls)
                    logger.info(f"Loaded {len(fetched_urls)} URLs from sitemap: {sitemap_url}")
                    break
            except Exception as e:
                logger.debug(f"Failed to load sitemap {sitemap_url}: {e}")
                continue
        
        return urls

    def _parse_sitemap(self, sitemap_url: str) -> list[str]:
        """
        Parse a sitemap XML file.
        Handles both regular sitemaps and sitemap index files.
        """
        urls = []
        
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(sitemap_url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ALAgent/1.0)"
            })
            response.raise_for_status()
            content = response.text
        
        # Parse XML
        root = ET.fromstring(content)
        
        # Handle namespace (sitemaps use xmlns)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        
        # Check if this is a sitemap index
        sitemap_tags = root.findall(".//sm:sitemap/sm:loc", ns)
        if sitemap_tags:
            # This is a sitemap index, recursively load each sitemap
            for loc in sitemap_tags:
                if loc.text:
                    try:
                        child_urls = self._parse_sitemap(loc.text)
                        urls.extend(child_urls)
                    except Exception as e:
                        logger.warning(f"Failed to load child sitemap {loc.text}: {e}")
            return urls
        
        # Regular sitemap - extract URLs
        url_tags = root.findall(".//sm:url/sm:loc", ns)
        for loc in url_tags:
            if loc.text:
                url = loc.text.strip()
                # Apply domain filter if needed
                if self.same_domain_only and self.urls:
                    base_domain = urlparse(self.urls[0]).netloc
                    if urlparse(url).netloc != base_domain:
                        continue
                urls.append(url)
        
        # Also try without namespace (some sitemaps don't use it)
        if not urls:
            for loc in root.iter():
                if loc.tag.endswith("loc") and loc.text:
                    urls.append(loc.text.strip())
        
        return urls

    def _load_url(self, url: str, depth: int) -> Generator[Document, None, None]:
        """Load a single URL and optionally crawl links."""
        if url in self._visited:
            return
        self._visited.add(url)

        try:
            if self.use_playwright:
                html, title = self._fetch_with_playwright(url)
            else:
                html, title = self._fetch_with_httpx(url)

            # Convert HTML to markdown
            content = self._html_converter.handle(html)
            content = self._clean_content(content)

            if content.strip():
                yield Document(
                    content=content,
                    source=url,
                    source_type="web",
                    title=title,
                    metadata={
                        "url": url,
                        "domain": urlparse(url).netloc,
                        "depth": depth,
                    }
                )

            # Crawl links if depth allows
            if depth < self.max_depth:
                links = self._extract_links(html, url)
                for link in links:
                    yield from self._load_url(link, depth + 1)

        except Exception as e:
            logger.warning(f"Failed to load {url}: {e}")

    def _fetch_with_httpx(self, url: str) -> tuple[str, str]:
        """Fetch page using httpx (static pages)."""
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ALAgent/1.0)"
            })
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else ""
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Get main content
        main = soup.find("main") or soup.find("article") or soup.find("body")
        return str(main) if main else html, title

    def _fetch_with_playwright(self, url: str) -> tuple[str, str]:
        """Fetch page using Playwright (JS-rendered pages)."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            
            title = page.title()
            html = page.content()
            
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        main = soup.find("main") or soup.find("article") or soup.find("body")
        return str(main) if main else html, title

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        """Extract links from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(base_url).netloc
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Handle relative URLs
            if href.startswith("/"):
                parsed = urlparse(base_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif not href.startswith("http"):
                continue

            # Filter by domain
            if self.same_domain_only and urlparse(href).netloc != base_domain:
                continue

            if href not in self._visited:
                links.append(href)

        return links[:50]  # Limit links per page

    def _clean_content(self, content: str) -> str:
        """Clean up converted markdown content."""
        lines = content.split("\n")
        cleaned = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("![]"):  # Skip image placeholders
                cleaned.append(line)
        return "\n".join(cleaned)


class GitHubRepoLoader(BaseLoader):
    """
    Load content from GitHub repositories.
    Supports loading files, READMEs, and code.
    """

    # File extensions to index
    CODE_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".cs", ".java", ".go", ".rs",
        ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".swift", ".kt", ".scala",
        ".md", ".rst", ".txt", ".json", ".yaml", ".yml", ".toml",
    }

    def __init__(
        self,
        repo_url: str,
        branch: str = "main",
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        github_token: str | None = None,
    ):
        self.repo_url = repo_url
        self.branch = branch
        self.include_patterns = include_patterns or ["*"]
        self.exclude_patterns = exclude_patterns or [
            "node_modules/*", ".git/*", "__pycache__/*", "*.min.js", "*.min.css",
            "dist/*", "build/*", ".venv/*", "venv/*"
        ]
        self.github_token = github_token

    def load(self) -> Generator[Document, None, None]:
        """Load repository contents."""
        import git
        from fnmatch import fnmatch

        # Parse repo info
        parsed = self._parse_repo_url(self.repo_url)
        if not parsed:
            logger.error(f"Invalid GitHub URL: {self.repo_url}")
            return

        owner, repo_name = parsed

        # Clone to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                clone_url = self.repo_url
                if self.github_token:
                    # Use token for private repos
                    clone_url = self.repo_url.replace(
                        "https://", f"https://{self.github_token}@"
                    )

                logger.info(f"Cloning {owner}/{repo_name}...")
                repo = git.Repo.clone_from(
                    clone_url,
                    temp_dir,
                    branch=self.branch,
                    depth=1,  # Shallow clone
                )

                repo_path = Path(temp_dir)

                # Iterate through files
                for file_path in repo_path.rglob("*"):
                    if not file_path.is_file():
                        continue

                    relative_path = str(file_path.relative_to(repo_path))

                    # Check exclusions
                    if any(fnmatch(relative_path, pat) for pat in self.exclude_patterns):
                        continue

                    # Check inclusions
                    if not any(fnmatch(relative_path, pat) for pat in self.include_patterns):
                        continue

                    # Check extension
                    if file_path.suffix.lower() not in self.CODE_EXTENSIONS:
                        continue

                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if len(content.strip()) < 10:
                            continue

                        yield Document(
                            content=content,
                            source=f"github://{owner}/{repo_name}/{relative_path}",
                            source_type="github",
                            title=relative_path,
                            metadata={
                                "owner": owner,
                                "repo": repo_name,
                                "branch": self.branch,
                                "file_path": relative_path,
                                "extension": file_path.suffix,
                            }
                        )

                    except Exception as e:
                        logger.warning(f"Failed to read {relative_path}: {e}")

            except Exception as e:
                logger.error(f"Failed to clone repository: {e}")

    def _parse_repo_url(self, url: str) -> tuple[str, str] | None:
        """Parse GitHub URL to extract owner and repo name."""
        # Handle various formats:
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        
        if "github.com" not in url:
            return None

        if url.startswith("git@"):
            # git@github.com:owner/repo.git
            parts = url.split(":")[-1].replace(".git", "").split("/")
        else:
            # https://github.com/owner/repo
            parsed = urlparse(url)
            parts = parsed.path.strip("/").replace(".git", "").split("/")

        if len(parts) >= 2:
            return parts[0], parts[1]
        return None


class PDFLoader(BaseLoader):
    """
    Load content from PDF files.
    Uses PyMuPDF (fitz) for fast and memory-efficient PDF parsing.
    """

    def __init__(
        self,
        file_paths: list[str | Path],
        extract_images: bool = False,
        max_pages: int = 10000,  # 最大页数限制
    ):
        self.file_paths = [Path(p) for p in file_paths]
        self.extract_images = extract_images
        self.max_pages = max_pages

    def load(self) -> Generator[Document, None, None]:
        """Load PDF files."""
        for file_path in self.file_paths:
            if not file_path.exists():
                logger.warning(f"PDF file not found: {file_path}")
                continue

            try:
                logger.info(f"[PDF] 开始加载: {file_path.name}")
                yield from self._load_pdf(file_path)
                logger.info(f"[PDF] 加载完成: {file_path.name}")
            except Exception as e:
                logger.error(f"[PDF] 加载失败 {file_path}: {e}")

    def _load_pdf(self, file_path: Path) -> Generator[Document, None, None]:
        """
        Load a single PDF file using PyMuPDF (fitz).
        PyMuPDF is much faster and uses less memory than pdfplumber.
        """
        import fitz  # PyMuPDF
        import gc

        full_text = []
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "pages": 0,
        }

        doc = None
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            metadata["pages"] = total_pages
            logger.info(f"[PDF] {file_path.name}: 共 {total_pages} 页")
            
            # 限制最大页数
            pages_to_process = min(total_pages, self.max_pages)
            if total_pages > self.max_pages:
                logger.warning(f"[PDF] {file_path.name}: 页数过多 ({total_pages})，只处理前 {self.max_pages} 页")
            
            # Extract PDF metadata
            if doc.metadata:
                for key in ["title", "author", "subject", "keywords", "creator"]:
                    if doc.metadata.get(key):
                        metadata[key] = doc.metadata[key]

            for i in range(pages_to_process):
                page_num = i + 1
                try:
                    # 进度日志（每20页或第一页/最后一页）
                    if page_num == 1 or page_num == pages_to_process or page_num % 20 == 0:
                        logger.info(f"[PDF] {file_path.name}: 处理第 {page_num}/{pages_to_process} 页...")
                    
                    page = doc[i]
                    text = page.get_text("text")  # 快速提取文本
                    
                    if text and text.strip():
                        full_text.append(f"--- Page {page_num} ---\n{text.strip()}")
                    
                    # 每处理20页，强制垃圾回收
                    if page_num % 20 == 0:
                        gc.collect()
                            
                except Exception as e:
                    logger.warning(f"[PDF] {file_path.name} 第 {page_num} 页处理失败: {e}")
                    continue
                    
        finally:
            # 确保关闭 PDF 释放资源
            if doc:
                doc.close()
            gc.collect()

        content = "\n\n".join(full_text)
        
        if content.strip():
            logger.info(f"[PDF] {file_path.name}: 提取完成，内容长度 {len(content)} 字符")
            yield Document(
                content=content,
                source=str(file_path),
                source_type="pdf",
                title=file_path.stem,
                metadata=metadata,
            )
        else:
            logger.warning(f"[PDF] {file_path.name}: 未提取到任何文本内容")

    def _format_table(self, table: list[list]) -> str:
        """Format extracted table as markdown."""
        if not table or not table[0]:
            return ""
        
        lines = []
        # Header
        headers = [str(cell or "") for cell in table[0]]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # Rows
        for row in table[1:]:
            cells = [str(cell or "") for cell in row]
            lines.append("| " + " | ".join(cells) + " |")
        
        return "\n".join(lines)


class URLLoader(BaseLoader):
    """
    Unified loader that automatically detects URL type and uses appropriate loader.
    """

    def __init__(
        self,
        url: str,
        github_token: str | None = None,
        use_playwright: bool = False,
    ):
        self.url = url
        self.github_token = github_token
        self.use_playwright = use_playwright

    def load(self) -> Generator[Document, None, None]:
        """Load from URL, detecting the type automatically."""
        if "github.com" in self.url and self._is_repo_url(self.url):
            loader = GitHubRepoLoader(
                self.url,
                github_token=self.github_token
            )
        elif self.url.lower().endswith(".pdf"):
            # Download PDF first
            yield from self._load_remote_pdf(self.url)
            return
        else:
            loader = WebPageLoader(
                [self.url],
                use_playwright=self.use_playwright
            )
        
        yield from loader.load()

    def _is_repo_url(self, url: str) -> bool:
        """Check if URL is a GitHub repository root (not a file)."""
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        # Repo URL has exactly owner/repo or owner/repo/
        return len(parts) == 2 or (len(parts) == 3 and parts[2] == "")

    def _load_remote_pdf(self, url: str) -> Generator[Document, None, None]:
        """Download and load a remote PDF."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            try:
                with httpx.Client(follow_redirects=True, timeout=60) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    tmp.write(response.content)
                    tmp.flush()

                loader = PDFLoader([tmp.name])
                for doc in loader.load():
                    doc.source = url
                    doc.metadata["original_url"] = url
                    yield doc
            finally:
                Path(tmp.name).unlink(missing_ok=True)


class MultimodalWebPageLoader(BaseLoader):
    """
    Load content from web pages including images and videos.
    Uses multimodal embedding model (e.g., qwen2.5-vl-embedding) for media vectorization.
    
    支持提取网页中的：
    - 图片：<img> 标签、CSS 背景图片
    - 视频：<video> 标签、视频缩略图
    - 支持 sitemap.xml 批量发现页面
    """

    # Supported image formats
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
    # Supported video formats
    VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg", ".mov", ".avi"}

    def __init__(
        self,
        urls: list[str],
        use_playwright: bool = True,
        max_depth: int = 0,
        same_domain_only: bool = True,
        extract_images: bool = True,
        extract_videos: bool = True,
        min_image_size: int = 100,
        max_images_per_page: int = 20,
        download_media: bool = True,
        use_sitemap: bool = False,
        sitemap_url: str | None = None,
    ):
        self.urls = urls
        self.use_playwright = use_playwright
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.extract_images = extract_images
        self.extract_videos = extract_videos
        self.min_image_size = min_image_size
        self.max_images_per_page = max_images_per_page
        self.download_media = download_media
        self.use_sitemap = use_sitemap
        self.sitemap_url = sitemap_url
        self._visited: set[str] = set()
        self._html_converter = html2text.HTML2Text()
        self._html_converter.ignore_links = False
        self._html_converter.ignore_images = False
        self._html_converter.body_width = 0

    def load(self) -> Generator[tuple[Document, list[MediaDocument]], None, None]:
        """
        Load web pages and extract media.
        Yields tuples of (Document, list[MediaDocument]).
        """
        # If using sitemap, discover URLs first
        if self.use_sitemap:
            sitemap_urls = self._load_from_sitemap()
            logger.info(f"Discovered {len(sitemap_urls)} URLs from sitemap for multimodal indexing")
            for url in sitemap_urls:
                yield from self._load_url(url, depth=0)
        
        # Then load explicitly provided URLs
        for url in self.urls:
            yield from self._load_url(url, depth=0)

    def _load_from_sitemap(self) -> list[str]:
        """
        Load URLs from sitemap.xml.
        Reuses the same logic as WebPageLoader.
        """
        urls = []
        
        # Determine sitemap URL
        if self.sitemap_url:
            sitemap_urls_to_check = [self.sitemap_url]
        elif self.urls:
            # Try common sitemap locations
            parsed = urlparse(self.urls[0])
            base = f"{parsed.scheme}://{parsed.netloc}"
            sitemap_urls_to_check = [
                f"{base}/sitemap.xml",
                f"{base}/sitemap_index.xml",
                f"{base}/sitemap/sitemap.xml",
            ]
        else:
            return urls
        
        for sitemap_url in sitemap_urls_to_check:
            try:
                fetched_urls = self._parse_sitemap(sitemap_url)
                if fetched_urls:
                    urls.extend(fetched_urls)
                    logger.info(f"Loaded {len(fetched_urls)} URLs from sitemap: {sitemap_url}")
                    break
            except Exception as e:
                logger.debug(f"Failed to load sitemap {sitemap_url}: {e}")
                continue
        
        return urls

    def _parse_sitemap(self, sitemap_url: str) -> list[str]:
        """
        Parse a sitemap XML file.
        Handles both regular sitemaps and sitemap index files.
        """
        urls = []
        
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(sitemap_url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ALAgent/1.0)"
            })
            response.raise_for_status()
            content = response.text
        
        # Parse XML
        root = ET.fromstring(content)
        
        # Handle namespace (sitemaps use xmlns)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        
        # Check if this is a sitemap index
        sitemap_tags = root.findall(".//sm:sitemap/sm:loc", ns)
        if sitemap_tags:
            # This is a sitemap index, recursively load each sitemap
            for loc in sitemap_tags:
                if loc.text:
                    try:
                        child_urls = self._parse_sitemap(loc.text)
                        urls.extend(child_urls)
                    except Exception as e:
                        logger.warning(f"Failed to load child sitemap {loc.text}: {e}")
            return urls
        
        # Regular sitemap - extract URLs
        url_tags = root.findall(".//sm:url/sm:loc", ns)
        for loc in url_tags:
            if loc.text:
                url = loc.text.strip()
                # Apply domain filter if needed
                if self.same_domain_only and self.urls:
                    base_domain = urlparse(self.urls[0]).netloc
                    if urlparse(url).netloc != base_domain:
                        continue
                urls.append(url)
        
        # Also try without namespace (some sitemaps don't use it)
        if not urls:
            for loc in root.iter():
                if loc.tag.endswith("loc") and loc.text:
                    urls.append(loc.text.strip())
        
        return urls

    def _load_url(self, url: str, depth: int) -> Generator[tuple[Document, list[MediaDocument]], None, None]:
        """Load a single URL and extract media."""
        if url in self._visited:
            return
        self._visited.add(url)

        try:
            if self.use_playwright:
                html, title, media_items = self._fetch_with_playwright_multimodal(url)
            else:
                html, title = self._fetch_with_httpx(url)
                media_items = self._extract_media_from_html(html, url)

            # Convert HTML to markdown (for text content)
            content = self._html_converter.handle(html)
            content = self._clean_content(content)

            # Download media if requested
            if self.download_media:
                media_items = self._download_media_items(media_items)

            doc = Document(
                content=content,
                source=url,
                source_type="web_multimodal",
                title=title,
                metadata={
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "depth": depth,
                    "images_count": len([m for m in media_items if m.media_type == "image"]),
                    "videos_count": len([m for m in media_items if m.media_type == "video"]),
                }
            )

            yield (doc, media_items)

            # Crawl links if depth allows
            if depth < self.max_depth:
                links = self._extract_links(html, url)
                for link in links:
                    yield from self._load_url(link, depth + 1)

        except Exception as e:
            logger.warning(f"Failed to load {url}: {e}")

    def _fetch_with_httpx(self, url: str) -> tuple[str, str]:
        """Fetch page using httpx (static pages)."""
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ALAgent/1.0)"
            })
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else ""
        return html, title

    def _fetch_with_playwright_multimodal(self, url: str) -> tuple[str, str, list[MediaDocument]]:
        """
        Fetch page using Playwright and extract media information.
        Returns (html, title, media_items).
        """
        from playwright.sync_api import sync_playwright
        import base64

        media_items: list[MediaDocument] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            
            title = page.title()
            html = page.content()

            # Extract images using Playwright's evaluate
            if self.extract_images:
                images = page.evaluate("""
                    () => {
                        const imgs = [];
                        document.querySelectorAll('img').forEach((img, idx) => {
                            if (img.src && img.naturalWidth > 0) {
                                imgs.push({
                                    src: img.src,
                                    alt: img.alt || '',
                                    width: img.naturalWidth,
                                    height: img.naturalHeight
                                });
                            }
                        });
                        return imgs;
                    }
                """)

                for img in images[:self.max_images_per_page]:
                    # Filter by size
                    if img.get("width", 0) < self.min_image_size and img.get("height", 0) < self.min_image_size:
                        continue
                    
                    media_items.append(MediaDocument(
                        url=img["src"],
                        media_type="image",
                        alt_text=img.get("alt", ""),
                        width=img.get("width"),
                        height=img.get("height"),
                        source_page=url,
                    ))

            # Extract videos
            if self.extract_videos:
                videos = page.evaluate("""
                    () => {
                        const vids = [];
                        document.querySelectorAll('video').forEach((video) => {
                            const src = video.src || video.querySelector('source')?.src;
                            if (src) {
                                vids.push({
                                    src: src,
                                    poster: video.poster || '',
                                    width: video.videoWidth || video.width,
                                    height: video.videoHeight || video.height
                                });
                            }
                        });
                        return vids;
                    }
                """)

                for video in videos:
                    # Use poster image if available, otherwise use video URL
                    media_url = video.get("poster") or video["src"]
                    media_items.append(MediaDocument(
                        url=media_url,
                        media_type="video",
                        alt_text=f"Video from {url}",
                        width=video.get("width"),
                        height=video.get("height"),
                        source_page=url,
                        metadata={"video_src": video["src"], "poster": video.get("poster", "")}
                    ))

            browser.close()

        return html, title, media_items

    def _extract_media_from_html(self, html: str, base_url: str) -> list[MediaDocument]:
        """Extract media URLs from static HTML."""
        soup = BeautifulSoup(html, "html.parser")
        media_items: list[MediaDocument] = []

        # Extract images
        if self.extract_images:
            for img in soup.find_all("img", src=True)[:self.max_images_per_page]:
                src = img["src"]
                # Handle relative URLs
                if src.startswith("/"):
                    parsed = urlparse(base_url)
                    src = f"{parsed.scheme}://{parsed.netloc}{src}"
                elif not src.startswith("http"):
                    src = urljoin(base_url, src)

                # Skip data URLs and tiny images
                if src.startswith("data:"):
                    continue

                media_items.append(MediaDocument(
                    url=src,
                    media_type="image",
                    alt_text=img.get("alt", ""),
                    width=int(img.get("width")) if img.get("width", "").isdigit() else None,
                    height=int(img.get("height")) if img.get("height", "").isdigit() else None,
                    source_page=base_url,
                ))

        # Extract videos
        if self.extract_videos:
            for video in soup.find_all("video"):
                src = video.get("src")
                if not src:
                    source = video.find("source")
                    if source:
                        src = source.get("src")
                
                if src:
                    # Handle relative URLs
                    if src.startswith("/"):
                        parsed = urlparse(base_url)
                        src = f"{parsed.scheme}://{parsed.netloc}{src}"
                    elif not src.startswith("http"):
                        src = urljoin(base_url, src)

                    poster = video.get("poster", "")
                    media_items.append(MediaDocument(
                        url=poster if poster else src,
                        media_type="video",
                        alt_text=f"Video from {base_url}",
                        source_page=base_url,
                        metadata={"video_src": src, "poster": poster}
                    ))

        return media_items

    def _download_media_items(self, media_items: list[MediaDocument]) -> list[MediaDocument]:
        """Download media items and encode as base64."""
        import base64

        downloaded = []
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            for item in media_items:
                try:
                    # Skip data URLs
                    if item.url.startswith("data:"):
                        downloaded.append(item)
                        continue

                    response = client.get(item.url, headers={
                        "User-Agent": "Mozilla/5.0 (compatible; ALAgent/1.0)"
                    })
                    response.raise_for_status()
                    
                    item.data = response.content
                    item.base64_data = base64.b64encode(response.content).decode("utf-8")
                    downloaded.append(item)
                    
                except Exception as e:
                    logger.warning(f"Failed to download media {item.url}: {e}")
                    # Keep the item without data
                    downloaded.append(item)

        return downloaded

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        """Extract links from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(base_url).netloc
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/"):
                parsed = urlparse(base_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif not href.startswith("http"):
                continue

            if self.same_domain_only and urlparse(href).netloc != base_domain:
                continue

            if href not in self._visited:
                links.append(href)

        return links[:50]

    def _clean_content(self, content: str) -> str:
        """Clean up converted markdown content."""
        lines = content.split("\n")
        cleaned = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned.append(line)
        return "\n".join(cleaned)
