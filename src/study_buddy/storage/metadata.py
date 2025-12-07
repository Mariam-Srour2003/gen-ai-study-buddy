import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class MetadataStore:
    """Handles storage and retrieval of chunk metadata"""
    
    def __init__(self, storage_path: str | Path):
        """
        Initialize metadata store.
        
        Args:
            storage_path: Directory path for storing metadata
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Metadata store initialized at: {self.storage_path}")
    
    def save_metadata(
        self,
        doc_id: str,
        chunks_metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Save metadata for all chunks of a document.
        
        Args:
            doc_id: Document identifier
            chunks_metadata: List of metadata dictionaries for each chunk
        """
        metadata_file = self.storage_path / f"{doc_id}_metadata.json"
        
        metadata_package = {
            "doc_id": doc_id,
            "num_chunks": len(chunks_metadata),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunks": chunks_metadata
        }
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_package, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved metadata for {len(chunks_metadata)} chunks of doc_id: {doc_id}")
        
        except Exception as e:
            logger.error(f"Error saving metadata for {doc_id}: {e}")
            raise
    
    def load_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata for a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_file = self.storage_path / f"{doc_id}_metadata.json"
        
        if not metadata_file.exists():
            logger.warning(f"Metadata file not found for doc_id: {doc_id}")
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"Loaded metadata for doc_id: {doc_id}")
            return metadata
        
        except Exception as e:
            logger.error(f"Error loading metadata for {doc_id}: {e}")
            return None
    
    def get_chunk_metadata(self, doc_id: str, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific chunk.
        
        Args:
            doc_id: Document identifier
            chunk_id: Chunk identifier
            
        Returns:
            Chunk metadata or None if not found
        """
        doc_metadata = self.load_metadata(doc_id)
        
        if not doc_metadata:
            return None
        
        for chunk in doc_metadata.get("chunks", []):
            if chunk.get("chunk_id") == chunk_id:
                return chunk
        
        logger.warning(f"Chunk {chunk_id} not found in doc_id: {doc_id}")
        return None
    
    def get_all_chunks_metadata(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get metadata for all chunks of a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            List of chunk metadata dictionaries
        """
        doc_metadata = self.load_metadata(doc_id)
        
        if not doc_metadata:
            return []
        
        return doc_metadata.get("chunks", [])
    
    def delete_metadata(self, doc_id: str) -> bool:
        """
        Delete metadata for a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        metadata_file = self.storage_path / f"{doc_id}_metadata.json"
        
        if not metadata_file.exists():
            logger.warning(f"Metadata file not found for deletion: {doc_id}")
            return False
        
        try:
            metadata_file.unlink()
            logger.info(f"Deleted metadata for doc_id: {doc_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting metadata for {doc_id}: {e}")
            return False
    
    def list_documents(self) -> List[str]:
        """
        List all document IDs with stored metadata.
        
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for metadata_file in self.storage_path.glob("*_metadata.json"):
            doc_id = metadata_file.stem.replace("_metadata", "")
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def get_chunk_by_index(self, doc_id: str, chunk_index: int) -> Optional[Dict[str, Any]]:
        """
        Get chunk metadata by its index.
        
        Args:
            doc_id: Document identifier
            chunk_index: Index of the chunk
            
        Returns:
            Chunk metadata or None if not found
        """
        chunks = self.get_all_chunks_metadata(doc_id)
        
        for chunk in chunks:
            if chunk.get("chunk_index") == chunk_index:
                return chunk
        
        return None
