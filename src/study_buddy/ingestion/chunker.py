from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import hashlib
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a single chunk of text with metadata"""
    
    def __init__(
        self,
        text: str,
        chunk_id: str,
        doc_id: str,
        chunk_index: int,
        metadata: Dict[str, Any] = None
    ):
        self.text = text
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.metadata.update({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "chunk_index": chunk_index,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "text_length": len(text)
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            "text": self.text,
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }


class DocumentChunker:
    """Handles document chunking using LangChain's RecursiveCharacterTextSplitter"""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting (default: standard separators)
        """
        logger.info(f"Initializing DocumentChunker with chunk_size={chunk_size}, overlap={chunk_overlap}")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Use LangChain's RecursiveCharacterTextSplitter
        # It tries to split on multiple separators in order
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=separators or ["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False
        )
        
        logger.info("DocumentChunker initialized successfully")
    
    def chunk_text(
        self,
        text: str,
        doc_id: str,
        additional_metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """
        Chunk text using LangChain's text splitter.
        
        Args:
            text: The text to chunk
            doc_id: Unique identifier for the document
            additional_metadata: Additional metadata to attach to chunks
            
        Returns:
            List of DocumentChunk objects
        """
        if not text or not text.strip():
            logger.warning(f"Empty text provided for doc_id: {doc_id}")
            return []
        
        logger.info(f"Chunking document {doc_id} ({len(text)} characters)")
        
        try:
            # Use LangChain to split text
            text_chunks = self.text_splitter.split_text(text)
            
            document_chunks = []
            
            for idx, chunk_text in enumerate(text_chunks):
                # Generate unique chunk ID
                chunk_id = self._generate_chunk_id(doc_id, idx, chunk_text)
                
                # Create metadata
                chunk_metadata = additional_metadata.copy() if additional_metadata else {}
                chunk_metadata.update({
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "chunk_size": len(chunk_text)
                })
                
                # Create DocumentChunk
                doc_chunk = DocumentChunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    chunk_index=idx,
                    metadata=chunk_metadata
                )
                
                document_chunks.append(doc_chunk)
            
            logger.info(f"Created {len(document_chunks)} chunks for doc_id: {doc_id}")
            
            return document_chunks
        
        except Exception as e:
            logger.error(f"Error chunking document {doc_id}: {e}")
            raise
    
    def _generate_chunk_id(self, doc_id: str, chunk_index: int, text: str) -> str:
        """
        Generate a unique ID for a chunk.
        
        Args:
            doc_id: Document identifier
            chunk_index: Index of the chunk
            text: Chunk text
            
        Returns:
            Unique chunk ID
        """
        # Create a hash based on doc_id, index, and text content
        content = f"{doc_id}_{chunk_index}_{text[:100]}"
        hash_obj = hashlib.sha256(content.encode())
        return f"{doc_id}_chunk_{chunk_index}_{hash_obj.hexdigest()[:8]}"
    
    def chunk_multiple_documents(
        self,
        documents: Dict[str, str],
        metadata_map: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, List[DocumentChunk]]:
        """
        Chunk multiple documents.
        
        Args:
            documents: Dictionary mapping doc_id to text
            metadata_map: Optional dictionary mapping doc_id to metadata
            
        Returns:
            Dictionary mapping doc_id to list of chunks
        """
        metadata_map = metadata_map or {}
        results = {}
        
        for doc_id, text in documents.items():
            metadata = metadata_map.get(doc_id, {})
            results[doc_id] = self.chunk_text(text, doc_id, metadata)
        
        return results
