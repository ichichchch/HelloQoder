"""Tests for the code chunker."""

import pytest
from app.chunker import TreeSitterChunker, get_chunker, LANGUAGE_MAP


class TestTreeSitterChunker:
    """Test cases for TreeSitterChunker."""

    def test_get_language(self):
        """Test language detection from file extensions."""
        chunker = get_chunker()
        
        assert chunker.get_language("test.py") == "python"
        assert chunker.get_language("test.ts") == "typescript"
        assert chunker.get_language("test.js") == "javascript"
        assert chunker.get_language("test.cs") == "c_sharp"
        assert chunker.get_language("test.unknown") is None

    def test_chunk_python_file(self):
        """Test chunking a Python file."""
        chunker = get_chunker(max_chunk_size=500)
        
        python_code = '''
def hello():
    """Say hello."""
    print("Hello, World!")

class Greeter:
    """A greeter class."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Greet the user."""
        return f"Hello, {self.name}!"
'''
        
        chunks = list(chunker.chunk_file("test.py", python_code))
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.file_path == "test.py"
            assert chunk.language == "python"
            assert chunk.start_line > 0
            assert chunk.end_line >= chunk.start_line

    def test_chunk_by_text_fallback(self):
        """Test text-based chunking for unsupported languages."""
        chunker = get_chunker(max_chunk_size=100)
        
        content = "Line 1\n" * 50
        
        chunks = list(chunker.chunk_file("test.unknown", content))
        
        assert len(chunks) > 1  # Should split into multiple chunks
        for chunk in chunks:
            assert chunk.node_type == "text_chunk"

    def test_large_chunk_splitting(self):
        """Test that large chunks are split appropriately."""
        chunker = get_chunker(max_chunk_size=200, overlap=50)
        
        # Create a file with one large function
        large_function = "def large_func():\n" + "    x = 1\n" * 100
        
        chunks = list(chunker.chunk_file("test.py", large_function))
        
        # Should be split into multiple chunks
        for chunk in chunks:
            assert len(chunk.content) <= 200 + 100  # Allow some buffer


class TestLanguageMap:
    """Test the language mapping."""

    def test_common_extensions(self):
        """Test that common extensions are mapped."""
        common_extensions = [".py", ".js", ".ts", ".cs", ".java", ".go"]
        
        for ext in common_extensions:
            assert ext in LANGUAGE_MAP, f"Extension {ext} should be in LANGUAGE_MAP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
