"""
Embedding module for RAG system.
"""

import numpy as np
from typing import List
import hashlib

class SimpleEmbedder:
    """Simple embedder for testing. Creates deterministic fake embeddings."""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Create fake embeddings for documents."""
        embeddings = []
        for text in texts:
            embedding = self._text_to_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Create fake embedding for query."""
        return self._text_to_embedding(query)
    
    def _text_to_embedding(self, text: str) -> List[float]:
        """Convert text to deterministic fake embedding."""
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        np.random.seed(hash_int % (2**32))
        embedding = np.random.randn(self.embedding_dim).tolist()
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def get_embedding_dim(self) -> int:
        return self.embedding_dim

