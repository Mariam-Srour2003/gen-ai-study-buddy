"""
Simple in-memory vector store for testing.
Can be replaced with ChromaDB later.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path
import pickle
import hashlib

class SimpleVectorStore:
    """Simple in-memory vector store."""
    
    def __init__(self, persist_path: str = "./simple_vector_store.pkl"):
        self.persist_path = Path(persist_path)
        self.documents = []  # List of {"text": str, "metadata": dict, "embedding": list}
        self._load()
    
    def add_documents(self, documents: List[Dict[str, Any]], embedder) -> List[str]:
        """Add documents with embeddings."""
        if not documents:
            return []
        
        ids = []
        for doc in documents:
            # Generate ID
            doc_id = hashlib.md5(
                f"{doc['text'][:100]}_{doc['metadata'].get('filename', '')}".encode()
            ).hexdigest()[:16]
            
            # Create embedding
            embedding = embedder.embed_query(doc['text'])
            
            # Store
            self.documents.append({
                'id': doc_id,
                'text': doc['text'],
                'metadata': doc['metadata'],
                'embedding': embedding
            })
            ids.append(doc_id)
        
        self._save()
        print(f"✅ Added {len(ids)} documents to vector store")
        return ids
    
    def search(self, query: str, embedder, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity."""
        if not self.documents:
            return []
        
        # Embed query
        query_embedding = np.array(embedder.embed_query(query))
        
        # Calculate similarities
        similarities = []
        for doc in self.documents:
            doc_embedding = np.array(doc['embedding'])
            
            # Cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((similarity, doc))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return top results
        results = []
        for similarity, doc in similarities[:n_results]:
            results.append({
                'text': doc['text'],
                'metadata': doc['metadata'],
                'distance': 1 - similarity,  # Convert to distance
                'id': doc['id']
            })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'document_count': len(self.documents),
            'persist_path': str(self.persist_path)
        }
    
    def clear(self):
        """Clear all documents."""
        self.documents = []
        self._save()
        print("✅ Cleared vector store")
    
    def _save(self):
        """Save to disk."""
        with open(self.persist_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def _load(self):
        """Load from disk."""
        if self.persist_path.exists():
            try:
                with open(self.persist_path, 'rb') as f:
                    self.documents = pickle.load(f)
                print(f"✅ Loaded {len(self.documents)} documents from disk")
            except:
                self.documents = []
                print("⚠ Could not load, starting fresh")
        else:
            self.documents = []
            print("✅ Starting new vector store")

