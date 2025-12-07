"""Study Buddy FastAPI Application"""

from contextlib import asynccontextmanager
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routers import rag_router, health_router
from .config.settings import get_settings
from .rag_qa.qa import RAGPipeline


def setup_logging() -> None:
    """Configure application logging"""
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)


# Setup logging on module import
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Creates the RAG pipeline ONCE at startup - no race conditions possible
    since this runs before any requests are accepted.
    """
    logger.info("Starting Study Buddy API...")
    
    # Create pipeline at startup (single-threaded, no race condition)
    settings = get_settings()
    app.state.pipeline = RAGPipeline(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        google_api_key=settings.google_api_key,
        faiss_index_path=settings.faiss_index_path,
        metadata_path=settings.metadata_path,
        top_k_results=settings.top_k_results
    )
    
    logger.info("RAG Pipeline initialized successfully")
    
    yield  # App runs and handles requests here
    
    # Cleanup on shutdown
    logger.info("Shutting down Study Buddy API...")
    app.state.pipeline = None


app = FastAPI(
    title="Study Buddy API",
    description="AI-powered study assistant with RAG capabilities",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Study Buddy API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
