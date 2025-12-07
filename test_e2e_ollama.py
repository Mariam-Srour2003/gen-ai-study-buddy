"""
End-to-end tests for Ollama provider integration
Tests mixed provider scenarios and ensures backward compatibility with Google
"""

import os
import asyncio
import logging
import json
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
logger = logging.getLogger(__name__)


async def test_providers_configuration():
    """Test that provider configuration works correctly"""
    logger.info("=" * 60)
    logger.info("TEST: Providers Configuration")
    logger.info("=" * 60)
    
    from src.study_buddy.config.settings import Settings
    
    # Test Google provider
    logger.info("\n1. Testing Google provider configuration...")
    os.environ["LLM_PROVIDER"] = "google"
    os.environ["EMBEDDING_PROVIDER"] = "google"
    os.environ["GOOGLE_API_KEY"] = "test-key"
    
    try:
        settings = Settings()
        logger.info(f"✓ Google LLM Provider: {settings.llm_provider} - Model: {settings.llm_model}")
        logger.info(f"✓ Google Embedding Provider: {settings.embedding_provider} - Model: {settings.embedding_model_name}")
        logger.info(f"✓ Dimension: {settings.embedding_dimension}")
    except Exception as e:
        logger.error(f"✗ Google provider configuration failed: {e}")
        return False
    
    # Test Ollama provider
    logger.info("\n2. Testing Ollama provider configuration...")
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["EMBEDDING_PROVIDER"] = "ollama"
    os.environ.pop("GOOGLE_API_KEY", None)
    
    try:
        settings = Settings()
        logger.info(f"✓ Ollama LLM Provider: {settings.llm_provider} - Model: {settings.ollama_llm_model}")
        logger.info(f"✓ Ollama Embedding Provider: {settings.embedding_provider} - Model: {settings.ollama_embedding_model}")
        logger.info(f"✓ Ollama Base URL: {settings.ollama_base_url}")
        logger.info(f"✓ Provider info: {settings.get_provider_info()}")
    except Exception as e:
        logger.error(f"✗ Ollama provider configuration failed: {e}")
        return False
    
    # Test mixed providers
    logger.info("\n3. Testing mixed provider configuration (Google LLM + Ollama Embeddings)...")
    os.environ["LLM_PROVIDER"] = "google"
    os.environ["EMBEDDING_PROVIDER"] = "ollama"
    os.environ["GOOGLE_API_KEY"] = "test-key"
    
    try:
        settings = Settings()
        logger.info(f"✓ LLM Provider: {settings.llm_provider}")
        logger.info(f"✓ Embedding Provider: {settings.embedding_provider}")
        logger.info(f"✓ Full config: {settings.get_provider_info()}")
    except Exception as e:
        logger.error(f"✗ Mixed provider configuration failed: {e}")
        return False
    
    logger.info("\n✓ All provider configurations passed!")
    return True


async def test_embeddings_factory():
    """Test that embeddings factory creates correct instances"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Embeddings Factory")
    logger.info("=" * 60)
    
    from src.study_buddy.rag_qa.vectorstore import create_embeddings
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_ollama import OllamaEmbeddings
    
    # Test Google embeddings
    logger.info("\n1. Testing Google embeddings factory...")
    try:
        embeddings = create_embeddings(
            provider="google",
            google_api_key="test-key",
            google_model="gemini-embedding-001"
        )
        assert isinstance(embeddings, GoogleGenerativeAIEmbeddings)
        logger.info(f"✓ Created Google embeddings: {type(embeddings).__name__}")
    except Exception as e:
        logger.error(f"✗ Google embeddings factory failed: {e}")
        return False
    
    # Test Ollama embeddings
    logger.info("\n2. Testing Ollama embeddings factory...")
    try:
        embeddings = create_embeddings(
            provider="ollama",
            ollama_model="nomic-embed-text:latest"
        )
        assert isinstance(embeddings, OllamaEmbeddings)
        logger.info(f"✓ Created Ollama embeddings: {type(embeddings).__name__}")
    except Exception as e:
        logger.error(f"✗ Ollama embeddings factory failed: {e}")
        return False
    
    logger.info("\n✓ Embeddings factory tests passed!")
    return True


async def test_llm_factory():
    """Test that LLM factory creates correct instances"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: LLM Factory")
    logger.info("=" * 60)
    
    from src.study_buddy.agent.study_agent import create_llm
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama
    
    # Test Google LLM
    logger.info("\n1. Testing Google LLM factory...")
    try:
        llm = create_llm(
            provider="google",
            model="gemini-2.0-flash",
            google_api_key="test-key"
        )
        assert isinstance(llm, ChatGoogleGenerativeAI)
        logger.info(f"✓ Created Google LLM: {type(llm).__name__}")
    except Exception as e:
        logger.error(f"✗ Google LLM factory failed: {e}")
        return False
    
    # Test Ollama LLM
    logger.info("\n2. Testing Ollama LLM factory...")
    try:
        llm = create_llm(
            provider="ollama",
            model="gemma3:4b"
        )
        assert isinstance(llm, ChatOllama)
        logger.info(f"✓ Created Ollama LLM: {type(llm).__name__}")
    except Exception as e:
        logger.error(f"✗ Ollama LLM factory failed: {e}")
        return False
    
    logger.info("\n✓ LLM factory tests passed!")
    return True


async def test_rag_pipeline_initialization():
    """Test RAGPipeline initialization with different providers"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: RAG Pipeline Initialization")
    logger.info("=" * 60)
    
    from src.study_buddy.rag_qa.qa import RAGPipeline
    from pathlib import Path
    import tempfile
    
    # Test with Google embeddings
    logger.info("\n1. Testing RAG Pipeline with Google embeddings...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RAGPipeline(
                embedding_provider="google",
                google_api_key="test-key",
                faiss_index_path=Path(tmpdir) / "indices",
                metadata_path=Path(tmpdir) / "metadata",
            )
            logger.info("✓ RAG Pipeline created with Google embeddings")
            logger.info(f"  - Provider: {pipeline.embedding_provider}")
    except Exception as e:
        logger.error(f"✗ RAG Pipeline with Google failed: {e}")
        return False
    
    # Test with Ollama embeddings
    logger.info("\n2. Testing RAG Pipeline with Ollama embeddings...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RAGPipeline(
                embedding_provider="ollama",
                ollama_embedding_model="nomic-embed-text:latest",
                faiss_index_path=Path(tmpdir) / "indices",
                metadata_path=Path(tmpdir) / "metadata",
            )
            logger.info("✓ RAG Pipeline created with Ollama embeddings")
            logger.info(f"  - Provider: {pipeline.embedding_provider}")
    except Exception as e:
        logger.error(f"✗ RAG Pipeline with Ollama failed: {e}")
        return False
    
    logger.info("\n✓ RAG Pipeline initialization tests passed!")
    return True


async def test_study_agent_initialization():
    """Test StudyAgent initialization with different providers"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Study Agent Initialization")
    logger.info("=" * 60)
    
    from src.study_buddy.agent.study_agent import StudyAgent
    from src.study_buddy.rag_qa.qa import RAGPipeline
    from pathlib import Path
    import tempfile
    
    # Create a test pipeline
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = RAGPipeline(
            embedding_provider="ollama",
            faiss_index_path=Path(tmpdir) / "indices",
            metadata_path=Path(tmpdir) / "metadata",
        )
        
        # Test with Google LLM
        logger.info("\n1. Testing StudyAgent with Google LLM...")
        try:
            agent = StudyAgent(
                pipeline=pipeline,
                llm_provider="google",
                llm_model="gemini-2.0-flash",
                google_api_key="test-key"
            )
            logger.info("✓ StudyAgent created with Google LLM")
            logger.info(f"  - Provider: {agent.llm_provider}")
            logger.info(f"  - Model: {agent.llm_model}")
            logger.info(f"  - Tools: {[tool.name for tool in agent.tools]}")
        except Exception as e:
            logger.error(f"✗ StudyAgent with Google LLM failed: {e}")
            return False
        
        # Test with Ollama LLM
        logger.info("\n2. Testing StudyAgent with Ollama LLM...")
        try:
            agent = StudyAgent(
                pipeline=pipeline,
                llm_provider="ollama",
                llm_model="gemma3:4b"
            )
            logger.info("✓ StudyAgent created with Ollama LLM")
            logger.info(f"  - Provider: {agent.llm_provider}")
            logger.info(f"  - Model: {agent.llm_model}")
            logger.info(f"  - Tools: {[tool.name for tool in agent.tools]}")
        except Exception as e:
            logger.error(f"✗ StudyAgent with Ollama LLM failed: {e}")
            return False
    
    logger.info("\n✓ Study Agent initialization tests passed!")
    return True


async def test_api_endpoints():
    """Test that API endpoints are correctly set up"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: API Endpoints")
    logger.info("=" * 60)
    
    try:
        from src.study_buddy.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        logger.info("\n1. Testing root endpoint (/)...")
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"✓ Root endpoint returns: {data}")
        assert "name" in data
        assert "providers" in data
        logger.info(f"  - Providers: {data['providers']}")
        
        # Test providers endpoint
        logger.info("\n2. Testing providers endpoint (/providers)...")
        response = client.get("/providers")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"✓ Providers endpoint returns: {json.dumps(data, indent=2)}")
        assert "llm_provider" in data
        assert "embedding_provider" in data
        
        # Test health endpoint
        logger.info("\n3. Testing health endpoint (/health)...")
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"✓ Health endpoint returns: {data}")
        
    except Exception as e:
        logger.error(f"✗ API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n✓ API endpoints tests passed!")
    return True


async def run_all_tests():
    """Run all end-to-end tests"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  END-TO-END TESTS: OLLAMA PROVIDER INTEGRATION".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    results = {}
    
    tests = [
        ("Provider Configuration", test_providers_configuration),
        ("Embeddings Factory", test_embeddings_factory),
        ("LLM Factory", test_llm_factory),
        ("RAG Pipeline Initialization", test_rag_pipeline_initialization),
        ("Study Agent Initialization", test_study_agent_initialization),
        ("API Endpoints", test_api_endpoints),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = "✓ PASSED" if result else "✗ FAILED"
        except Exception as e:
            logger.error(f"✗ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = "✗ CRASHED"
    
    # Print summary
    logger.info("\n")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if "PASSED" in v)
    total = len(results)
    
    for test_name, result in results.items():
        status_symbol = "[PASS]" if "PASSED" in result else "[FAIL]"
        logger.info(f"{status_symbol:12} | {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
