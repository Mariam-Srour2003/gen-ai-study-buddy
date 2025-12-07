"""Utilities for health checks and connection validation"""

import httpx
import logging

logger = logging.getLogger(__name__)


async def check_ollama_connection(base_url: str, timeout: float = 5.0) -> bool:
    """
    Check if Ollama server is reachable and responding.
    
    Args:
        base_url: Base URL of Ollama server (e.g., http://localhost:11434)
        timeout: Timeout in seconds
        
    Returns:
        True if Ollama is reachable, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{base_url}/api/tags")
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Failed to connect to Ollama at {base_url}: {e}")
        return False
