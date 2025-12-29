"""
Tree-sitter based code chunker for semantic code splitting.
Uses AST-based chunking to preserve logical code boundaries.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Generator
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeChunkData:
    """Represents a chunk of code with its metadata."""
    content: str
    file_path: str
    start_line: int
    end_line: int
    node_type: str
    language: str


# Supported file extensions and their languages
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".cs": "c_sharp",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
}

# Node types that represent logical code units for each language
CHUNK_NODE_TYPES = {
    "python": ["function_definition", "class_definition", "decorated_definition"],
    "javascript": ["function_declaration", "class_declaration", "arrow_function", "method_definition"],
    "typescript": ["function_declaration", "class_declaration", "arrow_function", "method_definition", "interface_declaration", "type_alias_declaration"],
    "c_sharp": ["class_declaration", "method_declaration", "interface_declaration", "record_declaration"],
    "java": ["class_declaration", "method_declaration", "interface_declaration"],
    "go": ["function_declaration", "method_declaration", "type_declaration"],
    "rust": ["function_item", "impl_item", "struct_item", "enum_item"],
    "ruby": ["method", "class", "module"],
    "php": ["function_definition", "class_declaration", "method_declaration"],
    "c": ["function_definition", "struct_specifier"],
    "cpp": ["function_definition", "class_specifier", "struct_specifier"],
}


class TreeSitterChunker:
    """
    Code chunker using Tree-sitter for AST-based splitting.
    Prioritizes logical boundaries (classes, functions) over fixed character counts.
    """

    def __init__(self, max_chunk_size: int = 1500, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self._parsers: dict = {}
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """Lazy initialization of tree-sitter parsers."""
        if self._initialized:
            return True
        
        try:
            # Import tree-sitter libraries
            import tree_sitter_python
            import tree_sitter_javascript
            import tree_sitter_typescript
            from tree_sitter import Language, Parser
            
            # Initialize parsers for each language
            self._parsers["python"] = Parser(Language(tree_sitter_python.language()))
            self._parsers["javascript"] = Parser(Language(tree_sitter_javascript.language()))
            self._parsers["typescript"] = Parser(Language(tree_sitter_typescript.language_typescript()))
            
            self._initialized = True
            logger.info("Tree-sitter parsers initialized successfully")
            return True
        except ImportError as e:
            logger.warning(f"Tree-sitter not available, falling back to text chunking: {e}")
            return False
        except Exception as e:
            logger.error(f"Error initializing tree-sitter: {e}")
            return False

    def get_language(self, file_path: str) -> str | None:
        """Determine the language based on file extension."""
        ext = Path(file_path).suffix.lower()
        return LANGUAGE_MAP.get(ext)

    def chunk_file(self, file_path: str, content: str) -> Generator[CodeChunkData, None, None]:
        """
        Chunk a file using AST-based splitting when possible,
        falling back to text-based chunking otherwise.
        """
        language = self.get_language(file_path)
        
        if language and self._ensure_initialized() and language in self._parsers:
            yield from self._chunk_with_ast(file_path, content, language)
        else:
            yield from self._chunk_by_text(file_path, content, language or "unknown")

    def _chunk_with_ast(
        self, file_path: str, content: str, language: str
    ) -> Generator[CodeChunkData, None, None]:
        """Chunk code using AST analysis."""
        parser = self._parsers.get(language)
        if not parser:
            yield from self._chunk_by_text(file_path, content, language)
            return

        try:
            tree = parser.parse(bytes(content, "utf-8"))
            root_node = tree.root_node
            
            chunk_types = set(CHUNK_NODE_TYPES.get(language, []))
            lines = content.split("\n")
            
            # Find all top-level nodes that represent logical units
            chunks_found = False
            for node in self._traverse_nodes(root_node, chunk_types):
                chunks_found = True
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                
                chunk_content = "\n".join(lines[start_line:end_line + 1])
                
                # If chunk is too large, split it further
                if len(chunk_content) > self.max_chunk_size:
                    yield from self._split_large_chunk(
                        file_path, chunk_content, start_line, language, node.type
                    )
                else:
                    yield CodeChunkData(
                        content=chunk_content,
                        file_path=file_path,
                        start_line=start_line + 1,  # 1-indexed
                        end_line=end_line + 1,
                        node_type=node.type,
                        language=language,
                    )
            
            # If no logical chunks found, fall back to text chunking
            if not chunks_found:
                yield from self._chunk_by_text(file_path, content, language)
                
        except Exception as e:
            logger.warning(f"AST parsing failed for {file_path}: {e}, falling back to text chunking")
            yield from self._chunk_by_text(file_path, content, language)

    def _traverse_nodes(self, node, target_types: set) -> Generator:
        """Traverse AST and yield nodes of target types."""
        if node.type in target_types:
            yield node
        else:
            for child in node.children:
                yield from self._traverse_nodes(child, target_types)

    def _split_large_chunk(
        self, file_path: str, content: str, base_line: int, language: str, node_type: str
    ) -> Generator[CodeChunkData, None, None]:
        """Split a large chunk into smaller pieces with overlap."""
        lines = content.split("\n")
        current_chunk_lines = []
        current_start = 0
        current_size = 0

        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > self.max_chunk_size and current_chunk_lines:
                yield CodeChunkData(
                    content="\n".join(current_chunk_lines),
                    file_path=file_path,
                    start_line=base_line + current_start + 1,
                    end_line=base_line + i,
                    node_type=f"{node_type}_part",
                    language=language,
                )
                
                # Calculate overlap
                overlap_lines = []
                overlap_size = 0
                for j in range(len(current_chunk_lines) - 1, -1, -1):
                    if overlap_size + len(current_chunk_lines[j]) > self.overlap:
                        break
                    overlap_lines.insert(0, current_chunk_lines[j])
                    overlap_size += len(current_chunk_lines[j]) + 1
                
                current_chunk_lines = overlap_lines
                current_start = i - len(overlap_lines)
                current_size = overlap_size

            current_chunk_lines.append(line)
            current_size += line_size

        # Yield remaining content
        if current_chunk_lines:
            yield CodeChunkData(
                content="\n".join(current_chunk_lines),
                file_path=file_path,
                start_line=base_line + current_start + 1,
                end_line=base_line + len(lines),
                node_type=f"{node_type}_part",
                language=language,
            )

    def _chunk_by_text(
        self, file_path: str, content: str, language: str
    ) -> Generator[CodeChunkData, None, None]:
        """Fallback text-based chunking for unsupported languages."""
        lines = content.split("\n")
        current_chunk_lines = []
        current_start = 0
        current_size = 0

        for i, line in enumerate(lines):
            line_size = len(line) + 1

            if current_size + line_size > self.max_chunk_size and current_chunk_lines:
                yield CodeChunkData(
                    content="\n".join(current_chunk_lines),
                    file_path=file_path,
                    start_line=current_start + 1,
                    end_line=i,
                    node_type="text_chunk",
                    language=language,
                )

                # Calculate overlap
                overlap_lines = []
                overlap_size = 0
                for j in range(len(current_chunk_lines) - 1, -1, -1):
                    if overlap_size + len(current_chunk_lines[j]) > self.overlap:
                        break
                    overlap_lines.insert(0, current_chunk_lines[j])
                    overlap_size += len(current_chunk_lines[j]) + 1

                current_chunk_lines = overlap_lines
                current_start = i - len(overlap_lines)
                current_size = overlap_size

            current_chunk_lines.append(line)
            current_size += line_size

        if current_chunk_lines:
            yield CodeChunkData(
                content="\n".join(current_chunk_lines),
                file_path=file_path,
                start_line=current_start + 1,
                end_line=len(lines),
                node_type="text_chunk",
                language=language,
            )


# Singleton instance
_chunker: TreeSitterChunker | None = None


def get_chunker(max_chunk_size: int = 1500, overlap: int = 200) -> TreeSitterChunker:
    """Get or create the chunker singleton."""
    global _chunker
    if _chunker is None:
        _chunker = TreeSitterChunker(max_chunk_size, overlap)
    return _chunker
