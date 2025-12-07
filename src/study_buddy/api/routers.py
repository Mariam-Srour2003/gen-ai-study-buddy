"""API routers for the Study Buddy application"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from typing import List, Dict, Any
import tempfile
import shutil
import re
from pathlib import Path

from ..models import (
    IngestResponse,
    QueryRequest,
    QueryResponse,
)
from ..rag_qa.qa import RAGPipeline
from ..config.settings import Settings, get_settings

# Constants
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 50 MB

# Create routers
rag_router = APIRouter(prefix="/rag", tags=["RAG"])
health_router = APIRouter(tags=["Health"])


def generate_doc_id_from_filename(filename: str) -> str:
    """
    Generate a safe doc_id from a filename.
    
    Example: "My Document (2).pdf" -> "my_document_2"
    """
    # Remove extension
    name = Path(filename).stem
    
    # Convert to lowercase and replace spaces/special chars with underscores
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    
    # Remove leading/trailing underscores and collapse multiple underscores
    name = re.sub(r'_+', '_', name).strip('_')
    
    # Ensure it's not empty
    if not name:
        import uuid
        name = f"doc_{uuid.uuid4().hex[:8]}"
    
    return name


def get_pipeline(request: Request) -> RAGPipeline:
    """
    Get RAG pipeline from app state.
    
    The pipeline is created once at app startup via the lifespan manager,
    so there's no race condition - we just return the existing instance.
    """
    return request.app.state.pipeline


# Health check endpoints
@health_router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint"""
    return {"status": "healthy"}


@health_router.get("/ready")
async def readiness_check(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Readiness check - verifies all dependencies are available"""
    checks = {
        "api_key_configured": settings.google_api_key is not None,
        "storage_path_exists": settings.base_storage_path.exists(),
    }
    
    all_ready = all(checks.values())
    
    if not all_ready:
        raise HTTPException(status_code=503, detail={"status": "not ready", "checks": checks})
    
    return {"status": "ready", "checks": checks}


# RAG endpoints
@rag_router.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    pipeline: RAGPipeline = Depends(get_pipeline)
) -> IngestResponse:
    """Upload and ingest a PDF file. Document ID is auto-generated from filename."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Check file size by reading content-length header or measuring
    file_size = 0
    if hasattr(file, 'size') and file.size:
        file_size = file.size
    else:
        # Read to measure size (will need to seek back)
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset for later reading
    
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum {MAX_FILE_SIZE_MB} MB allowed."
        )
    
    # Auto-generate doc_id from filename
    doc_id = generate_doc_id_from_filename(file.filename)
    
    # Save uploaded file temporarily
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)
        
        result = pipeline.ingest_pdf(tmp_path, doc_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return IngestResponse(
            status=result["status"], 
            doc_id=result["doc_id"],
            num_chunks=result.get("num_chunks")
        )
    finally:
        # Clean up temp file
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


@rag_router.post("/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_pipeline)
) -> QueryResponse:
    """Query a document using RAG"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not request.doc_id.strip():
        raise HTTPException(status_code=400, detail="doc_id cannot be empty")
    
    result = pipeline.query(request.doc_id, request.question)
    
    # Convert citations to list of strings
    citations = [
        f"[{c.get('chunk_id', 'unknown')}] (score: {c.get('score', 0):.3f}): {c.get('text', '')}"
        for c in result.get("citations", [])
    ]
    
    return QueryResponse(
        answer=result["answer"], 
        citations=citations,
        doc_id=request.doc_id
    )


@rag_router.get("/documents", response_model=List[str])
async def list_documents(
    pipeline: RAGPipeline = Depends(get_pipeline)
) -> List[str]:
    """List all ingested documents"""
    return pipeline.list_documents()


@rag_router.get("/documents/{doc_id}")
async def get_document_info(
    doc_id: str,
    pipeline: RAGPipeline = Depends(get_pipeline)
) -> Dict[str, Any]:
    """Get information about a specific document"""
    info = pipeline.get_document_info(doc_id)
    
    if info is None:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    
    return info


@rag_router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    pipeline: RAGPipeline = Depends(get_pipeline)
) -> Dict[str, str]:
    """Delete a document from the RAG pipeline"""
    result = pipeline.delete_document(doc_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return {"status": "deleted", "doc_id": doc_id}
