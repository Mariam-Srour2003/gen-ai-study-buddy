"""Study Buddy FastAPI Application"""

from contextlib import asynccontextmanager
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routers import rag_router, health_router
from .api.agent_router import agent_router
from .config.settings import get_settings
from .rag_qa.qa import RAGPipeline
from .agent.study_agent import StudyAgent
from .utils.health_check import check_ollama_connection


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
    
    Creates the RAG pipeline and Study Agent ONCE at startup - no race conditions
    possible since this runs before any requests are accepted.
    """
    logger.info("Starting Study Buddy API...")
    
    # Create pipeline at startup (single-threaded, no race condition)
    settings = get_settings()
    
    logger.info(f"LLM Provider: {settings.llm_provider}, Model: {settings.llm_model}")
    logger.info(f"Embedding Provider: {settings.embedding_provider}, Model: {settings.embedding_model_name}")
    
    # Validate Ollama connectivity if using Ollama provider
    if settings.embedding_provider == "ollama" or settings.llm_provider == "ollama":
        logger.info(f"Checking Ollama connection at {settings.ollama_base_url}...")
        ollama_available = await check_ollama_connection(settings.ollama_base_url)
        if not ollama_available:
            error_msg = f"Cannot connect to Ollama at {settings.ollama_base_url}. Ensure Ollama is running and accessible."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.info("✓ Ollama connection verified")
    
    app.state.pipeline = RAGPipeline(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        embedding_provider=settings.embedding_provider,
        google_api_key=settings.google_api_key,
        google_embedding_model=settings.google_embedding_model,
        ollama_base_url=settings.ollama_base_url,
        ollama_embedding_model=settings.ollama_embedding_model,
        faiss_index_path=settings.faiss_index_path,
        metadata_path=settings.metadata_path,
        top_k_results=settings.top_k_results
    )
    
    logger.info("RAG Pipeline initialized successfully")
    
    # Create Study Agent
    app.state.study_agent = StudyAgent(
        pipeline=app.state.pipeline,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_temperature=settings.llm_temperature,
        google_api_key=settings.google_api_key,
        ollama_base_url=settings.ollama_base_url,
        max_sessions=settings.agent_max_sessions,
    )
    
    logger.info("Study Agent initialized successfully")
    
    yield  # App runs and handles requests here
    
    # Cleanup on shutdown
    logger.info("Shutting down Study Buddy API...")
    app.state.study_agent = None
    app.state.pipeline = None


app = FastAPI(
    title="Study Buddy API",
    description="AI-powered study assistant with RAG capabilities",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
# Configure CORS_ORIGINS in .env as comma-separated list, or use "*" for all origins
_settings = get_settings()
_cors_origins = (
    _settings.cors_origins.split(",") 
    if _settings.cors_origins and _settings.cors_origins != "*" 
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(rag_router)
app.include_router(agent_router)


@app.get("/")
async def root():
    """Root endpoint with API info"""
    settings = get_settings()
    return {
        "name": "Study Buddy API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "agent": "/agent",
        "providers": {
            "llm": settings.llm_provider,
            "llm_model": settings.llm_model,
            "embedding": settings.embedding_provider,
            "embedding_model": settings.embedding_model_name,
        },
    }


@app.get("/providers")
async def get_providers():
    """Get current provider configuration"""
    settings = get_settings()
    return settings.get_provider_info()
