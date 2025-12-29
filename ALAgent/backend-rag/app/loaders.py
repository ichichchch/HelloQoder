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
    Supports both text-based and scanned PDFs (with OCR).
    """

    def __init__(
        self,
        file_paths: list[str | Path],
        extract_images: bool = False,
        use_ocr: bool = False,
    ):
        self.file_paths = [Path(p) for p in file_paths]
        self.extract_images = extract_images
        self.use_ocr = use_ocr

    def load(self) -> Generator[Document, None, None]:
        """Load PDF files."""
        for file_path in self.file_paths:
            if not file_path.exists():
                logger.warning(f"PDF file not found: {file_path}")
                continue

            try:
                yield from self._load_pdf(file_path)
            except Exception as e:
                logger.error(f"Failed to load PDF {file_path}: {e}")

    def _load_pdf(self, file_path: Path) -> Generator[Document, None, None]:
        """Load a single PDF file."""
        import pdfplumber

        full_text = []
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "pages": 0,
        }

        with pdfplumber.open(file_path) as pdf:
            metadata["pages"] = len(pdf.pages)
            
            # Extract PDF metadata
            if pdf.metadata:
                metadata.update({
                    k: v for k, v in pdf.metadata.items()
                    if isinstance(v, (str, int, float))
                })

            for i, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text()
                if text:
                    full_text.append(f"--- Page {i + 1} ---\n{text}")

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        table_text = self._format_table(table)
                        full_text.append(table_text)

        content = "\n\n".join(full_text)
        
        if content.strip():
            yield Document(
                content=content,
                source=str(file_path),
                source_type="pdf",
                title=file_path.stem,
                metadata=metadata,
            )

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
