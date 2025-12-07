"""Embedding wrapper - thin layer over LangChain's GoogleGenerativeAIEmbeddings"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

logger = logging.getLogger(__name__)


class Embedder:
    """Thin wrapper around LangChain's GoogleGenerativeAIEmbeddings"""
    
    def __init__(
        self,
        model_name: str = "gemini-embedding-001",
        google_api_key: str = None
    ):
        """
        Initialize embedder using LangChain's Google embeddings.
        
        Args:
            model_name: Name of the Google embedding model
            google_api_key: Google API key (uses env var if None)
        """
        logger.info(f"Initializing embeddings with {model_name}")
        self.model = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=google_api_key
        )
        logger.info("Embeddings initialized")

