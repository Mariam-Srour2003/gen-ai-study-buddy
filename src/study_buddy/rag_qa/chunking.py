"""
Chunking module for RAG system.
Splits documents into manageable chunks for embedding.
"""

from pathlib import Path
from typing import List, Dict, Any
import re

class TextChunker:
    """Handles splitting documents into chunks."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text or not text.strip():
            return []
        
        text = self._clean_text(text)
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence boundary
            if end < text_length:
                for break_char in ['. ', '! ', '? ', '\n\n']:
                    pos = text.rfind(break_char, start, end)
                    if pos != -1:
                        end = pos + len(break_char.rstrip())
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean up text."""
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


    def chunk_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a document file and return with metadata."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file based on extension
        text = self._read_file(file_path)
        
        # Chunk the text
        text_chunks = self.chunk_text(text)
        
        # Add metadata
        chunks_with_metadata = []
        for i, chunk in enumerate(text_chunks):
            chunks_with_metadata.append({
                'text': chunk,
                'metadata': {
                    'chunk_id': i,
                    'filename': file_path.name,
                    'total_chunks': len(text_chunks)
                }
            })
        
        return chunks_with_metadata
    
    def _read_file(self, file_path: Path) -> str:
        """Read text from different file formats."""
        ext = file_path.suffix.lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                raise ImportError("Install PyPDF2: pip install pypdf")
        
        else:
            # Try reading as text anyway
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                raise ValueError(f"Unsupported or corrupt file: {file_path}")

# Simple function for quick use
def chunk_text_simple(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Simple function to chunk text."""
    chunker = TextChunker(chunk_size, chunk_overlap)
    return chunker.chunk_text(text)

