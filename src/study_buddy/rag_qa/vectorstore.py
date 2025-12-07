"""Vector store wrapper - uses LangChain's FAISS integration with Google embeddings"""

from pathlib import Path
from typing import List, Any, Tuple
from collections import OrderedDict
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

logger = logging.getLogger(__name__)

# Maximum number of FAISS indices to keep in memory
MAX_CACHED_INDICES = 20


class LRUCache:
    """Simple LRU cache for FAISS vectorstores"""
    
    def __init__(self, max_size: int = MAX_CACHED_INDICES):
        self.max_size = max_size
        self._cache: OrderedDict[str, FAISS] = OrderedDict()
    
    def get(self, key: str) -> FAISS | None:
        """Get item and move to end (most recently used)"""
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None
    
    def put(self, key: str, value: FAISS) -> None:
        """Add item, evicting oldest if at capacity"""
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.max_size:
                evicted_key, _ = self._cache.popitem(last=False)
                logger.info(f"Evicted index '{evicted_key}' from cache (LRU)")
            self._cache[key] = value
    
    def delete(self, key: str) -> bool:
        """Remove item from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def __contains__(self, key: str) -> bool:
        return key in self._cache


class FAISSVectorStore:
    """Minimal wrapper around LangChain's FAISS vectorstore with LRU caching"""
    
    def __init__(
        self,
        index_path: str | Path,
        google_api_key: str = None,
        max_cached_indices: int = MAX_CACHED_INDICES
    ):
        """
        Initialize FAISS vectorstore.
        
        Args:
            index_path: Directory to store indices
            google_api_key: Google API key
            max_cached_indices: Maximum number of indices to keep in memory
        """
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # LangChain's Google embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=google_api_key
        )
        
        # LRU cache for vectorstores (prevents unbounded memory growth)
        self.vectorstores = LRUCache(max_size=max_cached_indices)
        
        logger.info(f"FAISS VectorStore initialized at {self.index_path} (max cache: {max_cached_indices})")
    
    def create_index(
        self,
        doc_id: str,
        chunks: List[Any],
        force_recreate: bool = False
    ) -> None:
        """Create FAISS index from chunks"""
        index_file = self.index_path / f"{doc_id}.faiss"
        
        if index_file.exists() and not force_recreate:
            self.load_index(doc_id)
            return
        
        if not chunks:
            logger.warning(f"No chunks for {doc_id}")
            return
        
        logger.info(f"Creating index for {doc_id}")
        
        try:
            documents = [
                Document(page_content=c.text, metadata=c.metadata)
                for c in chunks
            ]
            vectorstore = FAISS.from_documents(documents, self.embeddings)
            self.vectorstores.put(doc_id, vectorstore)
            vectorstore.save_local(str(self.index_path), index_name=doc_id)
            logger.info(f"Index created for {doc_id}")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    def search(self, doc_id: str, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """Search similar documents using LangChain"""
        vs = self.vectorstores.get(doc_id)
        if vs is None:
            self.load_index(doc_id)
            vs = self.vectorstores.get(doc_id)
        
        if vs is None:
            return []
        
        try:
            return vs.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def load_index(self, doc_id: str) -> bool:
        """Load FAISS index from disk"""
        try:
            vs = FAISS.load_local(
                str(self.index_path),
                self.embeddings,
                index_name=doc_id,
                allow_dangerous_deserialization=True
            )
            self.vectorstores.put(doc_id, vs)
            return True
        except Exception as e:
            logger.warning(f"Could not load index for {doc_id}: {e}")
            return False
    
    def delete_index(self, doc_id: str) -> bool:
        """Delete FAISS index"""
        self.vectorstores.delete(doc_id)
        
        for file in [f"{doc_id}.faiss", f"{doc_id}.pkl"]:
            fp = self.index_path / file
            if fp.exists():
                fp.unlink()
        
        return True
    
    def list_indices(self) -> List[str]:
        """List all available indices"""
        return [f.stem for f in self.index_path.glob("*.faiss")]
