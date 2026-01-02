"""
Vector store service using Milvus for code embeddings.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings

from app.config import get_settings
from app.chunker import get_chunker, CodeChunkData
from app.models import CodeChunk

logger = logging.getLogger(__name__)

# File extensions to index
INDEXABLE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".cs", ".java", ".go", ".rs",
    ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".swift", ".kt", ".scala",
    ".vue", ".svelte", ".html", ".css", ".scss", ".json", ".yaml", ".yml",
    ".md", ".txt", ".sql", ".sh", ".bash", ".ps1", ".dockerfile",
}

# Directories to ignore
IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".venv", "env",
    "dist", "build", ".next", ".nuxt", "target", "bin", "obj",
    ".vs", ".idea", ".vscode", "coverage", ".pytest_cache", ".mypy_cache",
}


class VectorStore:
    """Milvus-based vector store for code embeddings."""

    def __init__(self):
        self.settings = get_settings()
        self._connected = False
        self._embeddings: OpenAIEmbeddings | DashScopeEmbeddings | None = None
        self._multimodal_embeddings: Any = None  # For multimodal embedding model
        self._collections: dict[str, Collection] = {}
        self._embedding_dim = self.settings.text_embedding_dim
        self._multimodal_embedding_dim = self.settings.multimodal_embedding_dim

    def _ensure_connection(self) -> None:
        """Lazy initialization of Milvus connection."""
        if not self._connected:
            connections.connect(
                alias="default",
                host=self.settings.milvus_host,
                port=self.settings.milvus_port,
                user=self.settings.milvus_user,
                password=self.settings.milvus_password,
                db_name=self.settings.milvus_db_name,
            )
            self._connected = True
            logger.info(
                f"Milvus connected at {self.settings.milvus_host}:{self.settings.milvus_port}"
            )

    def _ensure_multimodal_embeddings(self) -> Any:
        """Lazy initialization of multimodal embedding model (qwen2.5-vl-embedding)."""
        if self._multimodal_embeddings is None:
            if not self.settings.dashscope_api_key:
                raise ValueError(
                    "DashScope API key required for multimodal embeddings. Set DASHSCOPE_API_KEY in .env"
                )
            
            import dashscope
            dashscope.api_key = self.settings.dashscope_api_key
            self._multimodal_embeddings = dashscope.MultiModalEmbedding
            logger.info(f"Using DashScope multimodal embedding model: {self.settings.multimodal_embedding_model}")
        
        return self._multimodal_embeddings

    def _ensure_embeddings(self) -> OpenAIEmbeddings | DashScopeEmbeddings:
        """Lazy initialization of embedding model."""
        if self._embeddings is None:
            # 优先使用 DashScope
            if self.settings.dashscope_api_key:
                logger.info(f"Using DashScope embedding with key: {self.settings.dashscope_api_key[:8]}...")
                self._embeddings = DashScopeEmbeddings(
                    model=self.settings.text_embedding_model,
                    dashscope_api_key=self.settings.dashscope_api_key,
                )
            # 回退到 OpenAI
            elif self.settings.openai_api_key:
                logger.info(f"Using OpenAI embedding with key: {self.settings.openai_api_key[:8]}...")
                self._embeddings = OpenAIEmbeddings(
                    model=self.settings.text_embedding_model,
                    api_key=self.settings.openai_api_key,
                )
            else:
                raise ValueError(
                    "No embedding API key configured. Set DASHSCOPE_API_KEY or OPENAI_API_KEY in .env"
                )
        return self._embeddings

    def _get_collection_name(self, workspace_path: str) -> str:
        """Generate a unique collection name for a workspace."""
        # Create a hash of the workspace path for a consistent name
        path_hash = hashlib.md5(workspace_path.encode()).hexdigest()[:12]
        return f"workspace_{path_hash}"

    def _get_collection(self, workspace_path: str) -> Collection:
        """Get or create a collection for a workspace."""
        collection_name = self._get_collection_name(workspace_path)
        
        if collection_name not in self._collections:
            self._ensure_connection()
            
            # Check if collection exists
            if utility.has_collection(collection_name):
                self._collections[collection_name] = Collection(collection_name)
            else:
                # Create new collection
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=256),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self._embedding_dim),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="start_line", dtype=DataType.INT64),
                    FieldSchema(name="end_line", dtype=DataType.INT64),
                    FieldSchema(name="node_type", dtype=DataType.VARCHAR, max_length=64),
                    FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=32),
                ]
                
                schema = CollectionSchema(fields, description=f"Code chunks for {workspace_path}")
                collection = Collection(collection_name, schema)
                
                # Create index for vector field
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                collection.create_index(field_name="embedding", index_params=index_params)
                
                self._collections[collection_name] = collection
        
        return self._collections[collection_name]

    def index_workspace(
        self, workspace_path: str, force_reindex: bool = False
    ) -> tuple[int, int]:
        """
        Index all code files in a workspace.
        Returns (files_indexed, chunks_created).
        """
        workspace = Path(workspace_path)
        if not workspace.exists():
            raise ValueError(f"Workspace path does not exist: {workspace_path}")

        collection = self._get_collection(workspace_path)
        embeddings = self._ensure_embeddings()
        chunker = get_chunker(
            self.settings.max_chunk_size,
            self.settings.chunk_overlap
        )

        if force_reindex:
            # Drop existing collection
            self._ensure_connection()
            collection_name = self._get_collection_name(workspace_path)
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                if collection_name in self._collections:
                    del self._collections[collection_name]

        files_indexed = 0
        chunks_created = 0

        for file_path in self._iterate_files(workspace):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                
                # Skip empty or very small files
                if len(content.strip()) < 10:
                    continue

                relative_path = str(file_path.relative_to(workspace))
                
                # Chunk the file
                chunks_data = list(chunker.chunk_file(relative_path, content))
                
                if not chunks_data:
                    continue

                # Generate embeddings
                texts = [chunk.content for chunk in chunks_data]
                chunk_embeddings = embeddings.embed_documents(texts)

                # Prepare data for Milvus
                ids = [
                    f"{relative_path}:{chunk.start_line}-{chunk.end_line}"
                    for chunk in chunks_data
                ]
                
                entities = [
                    ids,
                    chunk_embeddings,
                    texts,
                    [chunk.file_path for chunk in chunks_data],
                    [chunk.start_line for chunk in chunks_data],
                    [chunk.end_line for chunk in chunks_data],
                    [chunk.node_type for chunk in chunks_data],
                    [chunk.language for chunk in chunks_data],
                ]

                # Insert into Milvus
                collection.insert(entities)
                collection.flush()

                files_indexed += 1
                chunks_created += len(chunks_data)
                
                logger.debug(f"Indexed {relative_path}: {len(chunks_data)} chunks")

            except Exception as e:
                logger.warning(f"Error indexing {file_path}: {e}")
                continue

        logger.info(
            f"Indexing complete: {files_indexed} files, {chunks_created} chunks"
        )
        return files_indexed, chunks_created

    def _get_global_collection(self) -> Collection:
        """Get or create the global collection for external documents."""
        collection_name = "global_documents"
        
        if collection_name not in self._collections:
            self._ensure_connection()
            
            if utility.has_collection(collection_name):
                self._collections[collection_name] = Collection(collection_name)
            else:
                # Create collection with extended schema for documents
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=512),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self._embedding_dim),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
                    FieldSchema(name="source_type", dtype=DataType.VARCHAR, max_length=32),
                    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="chunk_index", dtype=DataType.INT64),
                ]
                
                schema = CollectionSchema(fields, description="Global documents from external sources")
                collection = Collection(collection_name, schema)
                
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                collection.create_index(field_name="embedding", index_params=index_params)
                
                self._collections[collection_name] = collection
        
        return self._collections[collection_name]

    def index_document(
        self,
        content: str,
        source: str,
        source_type: str,
        metadata: dict | None = None,
    ) -> int:
        """
        Index a single document (web page, PDF, GitHub file, etc.).
        Returns the number of chunks created.
        """
        if len(content.strip()) < 10:
            return 0

        collection = self._get_global_collection()
        embeddings = self._ensure_embeddings()
        
        # Check if document already exists
        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        if self._document_exists(collection, source_hash, source_type):
            logger.info(f"Document already indexed, skipping: {source}")
            return 0
        
        # Split content into chunks
        chunks = self._split_text(content, self.settings.max_chunk_size, self.settings.chunk_overlap)
        
        if not chunks:
            return 0

        # Generate embeddings
        chunk_embeddings = embeddings.embed_documents(chunks)
        
        # Generate unique IDs
        ids = [f"{source_hash}:{i}" for i in range(len(chunks))]
        
        title = metadata.get("title", "") if metadata else ""
        
        entities = [
            ids,
            chunk_embeddings,
            chunks,
            [source] * len(chunks),
            [source_type] * len(chunks),
            [title[:500]] * len(chunks),  # Truncate title if too long
            list(range(len(chunks))),
        ]
        
        collection.insert(entities)
        collection.flush()
        
        logger.info(f"Indexed document from {source}: {len(chunks)} chunks")
        return len(chunks)

    def _document_exists(self, collection: Collection, source_hash: str, source_type: str) -> bool:
        """
        Check if a document with the given source hash already exists in the collection.
        """
        try:
            collection.load()
            if collection.num_entities == 0:
                return False
            
            # Query by ID prefix (source_hash)
            expr = f'id like "{source_hash}:%"'
            results = collection.query(
                expr=expr,
                output_fields=["id"],
                limit=1,
            )
            
            return len(results) > 0
            
        except Exception as e:
            logger.debug(f"Error checking document existence: {e}")
            return False

    def _get_multimodal_collection(self) -> Collection:
        """Get or create the collection for multimodal documents (images/videos)."""
        collection_name = "multimodal_documents"
        
        if collection_name not in self._collections:
            self._ensure_connection()
            
            if utility.has_collection(collection_name):
                self._collections[collection_name] = Collection(collection_name)
            else:
                # Create collection with schema for multimodal content
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=512),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self._multimodal_embedding_dim),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),  # alt text / description
                    FieldSchema(name="media_url", dtype=DataType.VARCHAR, max_length=2048),
                    FieldSchema(name="media_type", dtype=DataType.VARCHAR, max_length=32),  # "image" or "video"
                    FieldSchema(name="source_page", dtype=DataType.VARCHAR, max_length=2048),
                    FieldSchema(name="alt_text", dtype=DataType.VARCHAR, max_length=1024),
                    FieldSchema(name="width", dtype=DataType.INT64),
                    FieldSchema(name="height", dtype=DataType.INT64),
                ]
                
                schema = CollectionSchema(fields, description="Multimodal documents (images and videos)")
                collection = Collection(collection_name, schema)
                
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                collection.create_index(field_name="embedding", index_params=index_params)
                
                self._collections[collection_name] = collection
        
        return self._collections[collection_name]

    def index_multimodal(
        self,
        content: str,
        media_data: str,  # Base64 encoded image/video data
        media_type: str,  # "image" or "video"
        source: str,
        source_page: str,
        metadata: dict | None = None,
    ) -> int:
        """
        Index a multimodal document (image or video) using multimodal embedding.
        
        Uses qwen2.5-vl-embedding model for generating embeddings from image/video.
        Returns 1 if successful, 0 otherwise.
        """
        try:
            collection = self._get_multimodal_collection()
            
            # Generate unique ID and check if already exists
            source_hash = hashlib.md5(source.encode()).hexdigest()[:16]
            doc_id = f"mm_{source_hash}"
            
            if self._multimodal_exists(collection, doc_id):
                logger.debug(f"Multimodal {media_type} already indexed, skipping: {source}")
                return 0
            
            multimodal_emb = self._ensure_multimodal_embeddings()
            
            # Prepare input for multimodal embedding
            # Format: data:image/jpeg;base64,xxx or video format
            if media_type == "image":
                mime_type = self._detect_image_mime(media_data)
                data_url = f"data:{mime_type};base64,{media_data}"
            else:
                # For videos, we typically embed the thumbnail/poster
                data_url = f"data:image/jpeg;base64,{media_data}"
            
            # Call DashScope multimodal embedding API
            response = multimodal_emb.call(
                model=self.settings.multimodal_embedding_model,
                input=[
                    {"image": data_url},
                ],
                auto_truncation=True,
            )
            
            if response.status_code != 200:
                logger.warning(f"Multimodal embedding failed: {response.message}")
                return 0
            
            # Extract embedding from response
            embedding = response.output["embeddings"][0]["embedding"]
            
            # Prepare metadata
            alt_text = metadata.get("alt_text", "") if metadata else ""
            width = metadata.get("width", 0) if metadata else 0
            height = metadata.get("height", 0) if metadata else 0
            
            entities = [
                [doc_id],
                [embedding],
                [content[:65000]],  # Truncate if too long
                [source[:2000]],
                [media_type],
                [source_page[:2000]],
                [alt_text[:1000]],
                [width or 0],
                [height or 0],
            ]
            
            collection.insert(entities)
            collection.flush()
            
            logger.debug(f"Indexed multimodal {media_type} from {source}")
            return 1
            
        except Exception as e:
            logger.error(f"Multimodal indexing error: {e}")
            return 0

    def _multimodal_exists(self, collection: Collection, doc_id: str) -> bool:
        """
        Check if a multimodal document with the given ID already exists.
        """
        try:
            collection.load()
            if collection.num_entities == 0:
                return False
            
            # Query by exact ID
            expr = f'id == "{doc_id}"'
            results = collection.query(
                expr=expr,
                output_fields=["id"],
                limit=1,
            )
            
            return len(results) > 0
            
        except Exception as e:
            logger.debug(f"Error checking multimodal existence: {e}")
            return False

    def _detect_image_mime(self, base64_data: str) -> str:
        """Detect image MIME type from base64 data header."""
        # Check first few bytes to detect format
        if base64_data.startswith("/9j/"):
            return "image/jpeg"
        elif base64_data.startswith("iVBOR"):
            return "image/png"
        elif base64_data.startswith("R0lGO"):
            return "image/gif"
        elif base64_data.startswith("UklGR"):
            return "image/webp"
        else:
            return "image/jpeg"  # Default to JPEG

    def query_multimodal(
        self,
        query: str | None = None,
        image_data: str | None = None,
        top_k: int = 5,
        media_type: str | None = None,
    ) -> list[dict]:
        """
        Query the multimodal collection.
        
        Can search by text query or by image similarity.
        """
        try:
            collection = self._get_multimodal_collection()
            
            collection.load()
            if collection.num_entities == 0:
                return []
            
            # Generate query embedding
            if image_data:
                # Use multimodal embedding for image query
                multimodal_emb = self._ensure_multimodal_embeddings()
                mime_type = self._detect_image_mime(image_data)
                data_url = f"data:{mime_type};base64,{image_data}"
                
                response = multimodal_emb.call(
                    model=self.settings.multimodal_embedding_model,
                    input=[{"image": data_url}],
                    auto_truncation=True,
                )
                
                if response.status_code != 200:
                    logger.warning(f"Multimodal query embedding failed: {response.message}")
                    return []
                
                query_embedding = response.output["embeddings"][0]["embedding"]
            elif query:
                # Use text embedding for text query
                embeddings = self._ensure_embeddings()
                query_embedding = embeddings.embed_query(query)
            else:
                return []
            
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Build expression filter if media_type specified
            expr = f'media_type == "{media_type}"' if media_type else None
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["content", "media_url", "media_type", "source_page", "alt_text", "width", "height"],
            )
            
            items = []
            if results and len(results) > 0:
                for hit in results[0]:
                    items.append({
                        "media_url": hit.entity.get("media_url"),
                        "media_type": hit.entity.get("media_type"),
                        "source_page": hit.entity.get("source_page"),
                        "alt_text": hit.entity.get("alt_text"),
                        "content": hit.entity.get("content"),
                        "width": hit.entity.get("width"),
                        "height": hit.entity.get("height"),
                        "score": float(hit.distance),
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Multimodal query error: {e}")
            return []

    def _split_text(self, text: str, max_size: int, overlap: int) -> list[str]:
        """Split text into chunks with overlap."""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_size
            
            # Try to break at a paragraph or sentence
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break > start + max_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence break
                    for sep in [". ", "。", "\n", "; ", "! ", "? "]:
                        sent_break = text.rfind(sep, start, end)
                        if sent_break > start + max_size // 2:
                            end = sent_break + len(sep)
                            break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - overlap if end < len(text) else len(text)
        
        return chunks

    def query_global(
        self, query: str, top_k: int = 5, source_type: str | None = None
    ) -> list[CodeChunk]:
        """
        Query the global documents collection.
        """
        try:
            collection = self._get_global_collection()
            embeddings = self._ensure_embeddings()
            
            collection.load()
            if collection.num_entities == 0:
                return []
            
            query_embedding = embeddings.embed_query(query)
            
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Build expression filter if source_type specified
            expr = f'source_type == "{source_type}"' if source_type else None
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["content", "source", "source_type", "title", "chunk_index"],
            )
            
            chunks = []
            if results and len(results) > 0:
                for hit in results[0]:
                    chunks.append(CodeChunk(
                        content=hit.entity.get("content"),
                        file_path=hit.entity.get("source"),
                        start_line=hit.entity.get("chunk_index", 0),
                        end_line=hit.entity.get("chunk_index", 0),
                        score=float(hit.distance),
                        metadata={
                            "source_type": hit.entity.get("source_type"),
                            "title": hit.entity.get("title"),
                        },
                    ))
            
            return chunks
            
        except Exception as e:
            logger.error(f"Global query error: {e}")
            return []

    def query(
        self, query: str, workspace_path: str, top_k: int = 5
    ) -> list[CodeChunk]:
        """
        Query the vector store for relevant code chunks.
        """
        try:
            collection = self._get_collection(workspace_path)
            embeddings = self._ensure_embeddings()

            # Check if collection has any documents
            collection.load()
            if collection.num_entities == 0:
                logger.warning(f"No documents in collection for {workspace_path}")
                return []

            # Generate query embedding
            query_embedding = embeddings.embed_query(query)

            # Search in Milvus
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["content", "file_path", "start_line", "end_line", "node_type", "language"],
            )

            # Convert to CodeChunk objects
            chunks = []
            if results and len(results) > 0:
                for hit in results[0]:
                    # Milvus returns distance, convert to similarity score
                    # For COSINE metric, distance is already similarity (higher is better)
                    score = float(hit.distance)
                    
                    chunks.append(CodeChunk(
                        content=hit.entity.get("content"),
                        file_path=hit.entity.get("file_path"),
                        start_line=hit.entity.get("start_line"),
                        end_line=hit.entity.get("end_line"),
                        score=score,
                        metadata={
                            "node_type": hit.entity.get("node_type"),
                            "language": hit.entity.get("language"),
                        },
                    ))

            return chunks

        except Exception as e:
            logger.error(f"Query error: {e}")
            return []

    def _iterate_files(self, workspace: Path):
        """Iterate over indexable files in a workspace."""
        for path in workspace.rglob("*"):
            if path.is_file():
                # Check if in ignored directory
                if any(ignored in path.parts for ignored in IGNORED_DIRS):
                    continue
                
                # Check extension
                if path.suffix.lower() in INDEXABLE_EXTENSIONS:
                    yield path

    def is_healthy(self) -> bool:
        """Check if the vector store is operational."""
        try:
            self._ensure_connection()
            # Try to list collections as a health check
            utility.list_collections()
            return True
        except Exception:
            return False

    def get_indexed_sources(self, source_type: str | None = None) -> list[str]:
        """
        Get list of already indexed document sources.
        Useful for resuming interrupted indexing jobs.
        
        Args:
            source_type: Filter by source type (e.g., "web_multimodal", "web", "pdf")
        
        Returns:
            List of source URLs/paths that have been indexed
        """
        try:
            collection = self._get_global_collection()
            collection.load()
            
            if collection.num_entities == 0:
                return []
            
            # Build expression filter if source_type specified
            expr = f'source_type == "{source_type}"' if source_type else None
            
            # Query all unique sources
            results = collection.query(
                expr=expr,
                output_fields=["source"],
                limit=10000,  # Large limit to get all sources
            )
            
            # Extract unique sources
            sources = list(set(r["source"] for r in results))
            return sorted(sources)
            
        except Exception as e:
            logger.error(f"Error getting indexed sources: {e}")
            return []


# Singleton instance
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
