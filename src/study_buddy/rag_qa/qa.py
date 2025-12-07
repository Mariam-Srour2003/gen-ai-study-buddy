"""Minimal RAG pipeline leveraging LangChain for all heavy lifting"""

from typing import List, Dict, Any, Optional, Literal
from pathlib import Path
import logging

from ..ingestion.pdf_loader import PDFLoader
from ..ingestion.chunker import DocumentChunker
from ..rag_qa.vectorstore import FAISSVectorStore
from ..storage.metadata import MetadataStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Minimal RAG pipeline using LangChain's built-in capabilities"""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        embedding_provider: Literal["google", "ollama"] = "google",
        google_api_key: str = None,
        google_embedding_model: str = "gemini-embedding-001",
        ollama_base_url: str = "http://localhost:11434",
        ollama_embedding_model: str = "nomic-embed-text:latest",
        faiss_index_path: str | Path = None,
        metadata_path: str | Path = None,
        top_k_results: int = 3
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_provider: Either "google" or "ollama"
            google_api_key: Google API key for embeddings (required for Google provider)
            google_embedding_model: Google embedding model name
            ollama_base_url: Ollama server URL
            ollama_embedding_model: Ollama embedding model name
            faiss_index_path: Path to store FAISS indices
            metadata_path: Path to store metadata
            top_k_results: Number of results to return in queries
        """
        logger.info(f"Initializing RAG Pipeline with {embedding_provider} embeddings")
        
        # Store config
        self.top_k_results = top_k_results
        self.embedding_provider = embedding_provider
        
        # Validate required paths
        if faiss_index_path is None:
            raise ValueError("faiss_index_path is required")
        if metadata_path is None:
            raise ValueError("metadata_path is required")
        
        # Validate Google API key if using Google provider
        if embedding_provider == "google" and not google_api_key:
            raise ValueError("google_api_key is required when using Google embedding provider")
        
        self.pdf_loader = PDFLoader()
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.vectorstore = FAISSVectorStore(
            index_path=faiss_index_path,
            embedding_provider=embedding_provider,
            google_api_key=google_api_key,
            google_embedding_model=google_embedding_model,
            ollama_base_url=ollama_base_url,
            ollama_embedding_model=ollama_embedding_model,
        )
        self.metadata_store = MetadataStore(storage_path=metadata_path)
        
        logger.info(f"RAG Pipeline ready (provider: {embedding_provider})")
    
    def ingest_pdf(self, pdf_path: str | Path, doc_id: str, force_recreate: bool = False) -> Dict[str, Any]:
        """Ingest PDF document"""
        try:
            logger.info(f"Ingesting PDF: {pdf_path}")
            text = self.pdf_loader.load_pdf(pdf_path)
            pdf_meta = self.pdf_loader.get_pdf_metadata(pdf_path)
            
            chunks = self.chunker.chunk_text(text, doc_id, pdf_meta)
            if not chunks:
                raise ValueError("No chunks generated")
            
            self.vectorstore.create_index(doc_id, chunks, force_recreate)
            self.metadata_store.save_metadata(doc_id, [c.to_dict() for c in chunks])
            
            return {"status": "success", "doc_id": doc_id, "num_chunks": len(chunks)}
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            return {"status": "error", "error": str(e)}
    
    def ingest_text(self, text: str, doc_id: str, metadata: Dict = None, force_recreate: bool = False) -> Dict[str, Any]:
        """Ingest raw text"""
        try:
            logger.info(f"Ingesting text: {doc_id}")
            chunks = self.chunker.chunk_text(text, doc_id, metadata)
            if not chunks:
                raise ValueError("No chunks generated")
            
            self.vectorstore.create_index(doc_id, chunks, force_recreate)
            self.metadata_store.save_metadata(doc_id, [c.to_dict() for c in chunks])
            
            return {"status": "success", "doc_id": doc_id, "num_chunks": len(chunks)}
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            return {"status": "error", "error": str(e)}
    
    def query(self, doc_id: str, question: str, k: int = None) -> Dict[str, Any]:
        """Query document - LangChain handles retrieval"""
        k = k or self.top_k_results
        
        try:
            logger.info(f"Querying {doc_id}")
            results = self.vectorstore.search(doc_id, question, k)
            
            if not results:
                return {"answer": "No relevant information found", "citations": [], "doc_id": doc_id}
            
            citations = [
                {
                    "chunk_id": doc.metadata.get("chunk_id", f"chunk_{i}"),
                    "score": float(score),
                    "text": doc.page_content[:200]
                }
                for i, (doc, score) in enumerate(results)
            ]
            
            # Simple answer from context
            context = "\n\n".join([doc.page_content for doc, _ in results])
            answer = f"Based on retrieved context:\n\n{context}"
            
            return {"answer": answer, "citations": citations, "doc_id": doc_id}
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {"answer": f"Error: {str(e)}", "citations": [], "doc_id": doc_id}
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete document"""
        try:
            self.vectorstore.delete_index(doc_id)
            self.metadata_store.delete_metadata(doc_id)
            return {"status": "success", "doc_id": doc_id}
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_documents(self) -> List[str]:
        """List all documents"""
        return self.metadata_store.list_documents()
    
    def get_document_info(self, doc_id: str) -> Optional[Dict]:
        """Get document info"""
        return self.metadata_store.load_metadata(doc_id)
