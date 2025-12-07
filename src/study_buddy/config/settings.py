from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Embedding Model Configuration
    embedding_model_name: str = "gemini-embedding-001"
    embedding_dimension: int = 768  # Dimension for gemini-embedding-001
    google_api_key: Optional[str] = None  # Will be loaded from GOOGLE_API_KEY env var
    
    # Chunking Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Storage Paths
    base_storage_path: Path = Path("./storage_data")
    faiss_index_path: Path = base_storage_path / "faiss_indices"
    metadata_path: Path = base_storage_path / "metadata"
    uploaded_files_path: Path = base_storage_path / "uploaded_files"
    
    # LLM Configuration (for QA)
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7
    
    # RAG Configuration
    top_k_results: int = 3
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"
    
    @field_validator("google_api_key", mode="before")
    @classmethod
    def validate_google_api_key(cls, v):
        """Ensure Google API key is provided"""
        # Also check environment variable directly
        api_key = v or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required. Set it as an environment variable "
                "or in your .env file."
            )
        return api_key
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create storage directories on initialization
        self.faiss_index_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        self.uploaded_files_path.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Factory function to get settings - allows for dependency injection in tests"""
    return Settings()


# Global settings instance (for backward compatibility)
settings = Settings()
