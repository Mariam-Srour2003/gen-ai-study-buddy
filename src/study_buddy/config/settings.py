from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import model_validator, Field
from typing import Optional, Literal
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Provider Selection
    llm_provider: Literal["google", "ollama"] = "google"  # Choose between Google Gemini or Ollama
    embedding_provider: Literal["google", "ollama"] = "google"  # Embedding provider
    
    # Google Configuration
    google_api_key: Optional[str] = None  # Required when using Google provider
    google_llm_model: str = "gemini-2.0-flash"  # Google Gemini LLM model
    google_embedding_model: str = "gemini-embedding-001"  # Google embedding model
    google_embedding_dimension: int = 768  # Dimension for gemini-embedding-001
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"  # Ollama server URL
    ollama_llm_model: str = "gemma3:4b"  # Ollama LLM model
    ollama_embedding_model: str = "nomic-embed-text:latest"  # Ollama embedding model
    ollama_embedding_dimension: int = 768  # Dimension for nomic-embed-text
    
    # Legacy aliases for backward compatibility
    @property
    def llm_model(self) -> str:
        """Get the LLM model based on provider"""
        if self.llm_provider == "ollama":
            return self.ollama_llm_model
        return self.google_llm_model
    
    @property
    def embedding_model_name(self) -> str:
        """Get the embedding model based on provider"""
        if self.embedding_provider == "ollama":
            return self.ollama_embedding_model
        return self.google_embedding_model
    
    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension based on provider"""
        if self.embedding_provider == "ollama":
            return self.ollama_embedding_dimension
        return self.google_embedding_dimension
    
    # Common LLM Configuration
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature (0.0-2.0)")
    
    # Chunking Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Storage Paths
    base_storage_path: Path = Path("./storage_data")
    faiss_index_path: Path = base_storage_path / "faiss_indices"
    metadata_path: Path = base_storage_path / "metadata"
    uploaded_files_path: Path = base_storage_path / "uploaded_files"
    
    # Agent Configuration
    agent_max_sessions: int = 100  # Maximum concurrent sessions
    agent_max_iterations: int = 5  # Max ReAct iterations for auto-study
    agent_max_messages_per_session: int = 10  # Max messages per session
    agent_verbose: bool = False  # Verbose logging for agent
    
    # RAG Configuration
    top_k_results: int = 3
    
    # CORS Configuration
    cors_origins: str = "*"  # Comma-separated list of allowed origins, or "*" for all
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"
    
    @model_validator(mode="after")
    def validate_provider_requirements(self):
        """Validate that required credentials are available for the selected providers"""
        # Check Google API key if using Google provider
        if self.llm_provider == "google" or self.embedding_provider == "google":
            api_key = self.google_api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is required when using Google provider. "
                    "Set it as an environment variable, in your .env file, "
                    "or switch to Ollama provider (LLM_PROVIDER=ollama, EMBEDDING_PROVIDER=ollama)."
                )
            # Update the value if it came from env
            object.__setattr__(self, 'google_api_key', api_key)
        return self
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create storage directories on initialization
        self.faiss_index_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        self.uploaded_files_path.mkdir(parents=True, exist_ok=True)
    
    def get_provider_info(self) -> dict:
        """Get information about current provider configuration"""
        return {
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model_name,
            "embedding_dimension": self.embedding_dimension,
            "ollama_base_url": self.ollama_base_url if self.llm_provider == "ollama" else None,
        }


@lru_cache()
def get_settings() -> Settings:
    """Factory function to get settings - cached for performance"""
    return Settings()
