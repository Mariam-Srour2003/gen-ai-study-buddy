"""
Text chunking module for RAG system.
Word-based chunking to avoid cutting words.
"""

from pathlib import Path
from typing import List, Dict, Any
import re

class TextChunker:
    """Handles splitting documents into chunks without cutting words."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size  # Approximate character count
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks without cutting words."""
        if not text or not text.strip():
            return []
        
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If text is short, return as single chunk
        if len(text) <= self.chunk_size:
            return [text]
        
        # Split into sentences (simplified)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed chunk size
            if current_length + len(sentence) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_sentences = []
                overlap_length = 0
                
                # Add sentences from end for overlap
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s) + 1  # +1 for space
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_length += len(sentence) + 1  # +1 for space
        
        # Add the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks
    
    def chunk_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a document file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except:
            raise ValueError(f"Could not read file: {file_path}")
        
        # Chunk the text
        text_chunks = self.chunk_text(text)
        
        # Add metadata
        result = []
        for i, chunk in enumerate(text_chunks):
            result.append({
                'text': chunk,
                'metadata': {
                    'chunk_id': i,
                    'filename': file_path.name,
                    'total_chunks': len(text_chunks)
                }
            })
        
        return result

