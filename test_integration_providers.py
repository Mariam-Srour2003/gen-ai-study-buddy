"""
Integration test for agent functionality with different providers
Tests that tools work correctly regardless of provider
"""

import asyncio
import logging
import os
from pathlib import Path
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_agent_with_mock_pipeline():
    """Test agent initialization and tool structure with both providers"""
    logger.info("=" * 70)
    logger.info("INTEGRATION TEST: Agent Functionality with Different Providers")
    logger.info("=" * 70)
    
    from src.study_buddy.agent.study_agent import StudyAgent
    from src.study_buddy.rag_qa.qa import RAGPipeline
    
    # Create temporary directories for test
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Test 1: Google Provider
        logger.info("\n" + "=" * 70)
        logger.info("Test 1: Agent with Google Providers")
        logger.info("=" * 70)
        
        try:
            pipeline_google = RAGPipeline(
                embedding_provider="google",
                google_api_key="test-key",
                faiss_index_path=tmpdir / "google_indices",
                metadata_path=tmpdir / "google_metadata",
            )
            
            agent_google = StudyAgent(
                pipeline=pipeline_google,
                llm_provider="google",
                llm_model="gemini-2.0-flash",
                google_api_key="test-key"
            )
            
            logger.info("\n✓ Agent created successfully with Google providers")
            logger.info(f"  LLM Provider: {agent_google.llm_provider}")
            logger.info(f"  LLM Model: {agent_google.llm_model}")
            logger.info(f"  Tools available: {len(agent_google.tools)}")
            
            # Verify tools
            tool_names = {tool.name for tool in agent_google.tools}
            expected_tools = {'mcq_generator', 'flashcard_generator', 'explain_concept', 'summarize_document'}
            assert tool_names == expected_tools, f"Unexpected tools: {tool_names}"
            logger.info(f"  ✓ Tools verified: {tool_names}")
            
            # Verify ReAct agent
            assert hasattr(agent_google, 'agent_executor'), "Missing ReAct agent executor"
            logger.info("  ✓ ReAct agent executor created")
            
            # Verify session manager
            assert hasattr(agent_google, 'session_manager'), "Missing session manager"
            logger.info("  ✓ Session manager created")
            
        except Exception as e:
            logger.error(f"✗ Google provider test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 2: Ollama Provider
        logger.info("\n" + "=" * 70)
        logger.info("Test 2: Agent with Ollama Providers")
        logger.info("=" * 70)
        
        try:
            pipeline_ollama = RAGPipeline(
                embedding_provider="ollama",
                ollama_embedding_model="nomic-embed-text:latest",
                faiss_index_path=tmpdir / "ollama_indices",
                metadata_path=tmpdir / "ollama_metadata",
            )
            
            agent_ollama = StudyAgent(
                pipeline=pipeline_ollama,
                llm_provider="ollama",
                llm_model="gemma3:4b"
            )
            
            logger.info("\n✓ Agent created successfully with Ollama providers")
            logger.info(f"  LLM Provider: {agent_ollama.llm_provider}")
            logger.info(f"  LLM Model: {agent_ollama.llm_model}")
            logger.info(f"  Tools available: {len(agent_ollama.tools)}")
            
            # Verify tools
            tool_names = {tool.name for tool in agent_ollama.tools}
            expected_tools = {'mcq_generator', 'flashcard_generator', 'explain_concept', 'summarize_document'}
            assert tool_names == expected_tools, f"Unexpected tools: {tool_names}"
            logger.info(f"  ✓ Tools verified: {tool_names}")
            
            # Verify ReAct agent
            assert hasattr(agent_ollama, 'agent_executor'), "Missing ReAct agent executor"
            logger.info("  ✓ ReAct agent executor created")
            
            # Verify session manager
            assert hasattr(agent_ollama, 'session_manager'), "Missing session manager"
            logger.info("  ✓ Session manager created")
            
        except Exception as e:
            logger.error(f"✗ Ollama provider test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Mixed Providers
        logger.info("\n" + "=" * 70)
        logger.info("Test 3: Agent with Mixed Providers (Google LLM + Ollama Embeddings)")
        logger.info("=" * 70)
        
        try:
            pipeline_mixed = RAGPipeline(
                embedding_provider="ollama",
                ollama_embedding_model="nomic-embed-text:latest",
                faiss_index_path=tmpdir / "mixed_indices",
                metadata_path=tmpdir / "mixed_metadata",
            )
            
            agent_mixed = StudyAgent(
                pipeline=pipeline_mixed,
                llm_provider="google",
                llm_model="gemini-2.0-flash",
                google_api_key="test-key"
            )
            
            logger.info("\n✓ Agent created successfully with mixed providers")
            logger.info(f"  LLM Provider: {agent_mixed.llm_provider} (Google)")
            logger.info(f"  LLM Model: {agent_mixed.llm_model}")
            logger.info(f"  Embedding Provider: {agent_mixed.pipeline.embedding_provider} (Ollama)")
            logger.info(f"  Tools available: {len(agent_mixed.tools)}")
            
            # Verify tools
            tool_names = {tool.name for tool in agent_mixed.tools}
            expected_tools = {'mcq_generator', 'flashcard_generator', 'explain_concept', 'summarize_document'}
            assert tool_names == expected_tools, f"Unexpected tools: {tool_names}"
            logger.info(f"  ✓ Tools verified: {tool_names}")
            
        except Exception as e:
            logger.error(f"✗ Mixed provider test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 4: Tool Compatibility
        logger.info("\n" + "=" * 70)
        logger.info("Test 4: Tool Compatibility Across Providers")
        logger.info("=" * 70)
        
        try:
            # Get tools from both agents
            google_tools = {tool.name: tool for tool in agent_google.tools}
            ollama_tools = {tool.name: tool for tool in agent_ollama.tools}
            
            # Verify same tools exist in both
            for tool_name in expected_tools:
                assert tool_name in google_tools, f"Missing tool {tool_name} in Google agent"
                assert tool_name in ollama_tools, f"Missing tool {tool_name} in Ollama agent"
                
                google_tool = google_tools[tool_name]
                ollama_tool = ollama_tools[tool_name]
                
                # Verify same interface
                assert google_tool.name == ollama_tool.name
                assert google_tool.description == ollama_tool.description
                logger.info(f"  ✓ Tool '{tool_name}' compatible across providers")
            
        except Exception as e:
            logger.error(f"✗ Tool compatibility test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 5: Session Management
        logger.info("\n" + "=" * 70)
        logger.info("Test 5: Session Management with Different Providers")
        logger.info("=" * 70)
        
        try:
            # Test session creation
            session_google = agent_google.session_manager.create_session()
            session_ollama = agent_ollama.session_manager.create_session()
            
            # Verify sessions
            assert session_google.session_id is not None
            assert session_ollama.session_id is not None
            logger.info(f"  ✓ Google session created: {session_google.session_id}")
            logger.info(f"  ✓ Ollama session created: {session_ollama.session_id}")
            
            # Add messages
            session_google.add_human_message("What is machine learning?")
            session_ollama.add_human_message("What is machine learning?")
            
            assert len(session_google.messages) == 1
            assert len(session_ollama.messages) == 1
            logger.info("  ✓ Messages added to sessions successfully")
            
            # Retrieve sessions by ID
            retrieved_google = agent_google.session_manager.get_session(session_google.session_id)
            retrieved_ollama = agent_ollama.session_manager.get_session(session_ollama.session_id)
            
            assert retrieved_google is not None
            assert retrieved_ollama is not None
            assert len(retrieved_google.messages) == 1
            assert len(retrieved_ollama.messages) == 1
            logger.info("  ✓ Sessions retrieved with message history intact")
            
        except Exception as e:
            logger.error(f"✗ Session management test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ ALL INTEGRATION TESTS PASSED")
    logger.info("=" * 70)
    return True


if __name__ == "__main__":
    os.environ["GOOGLE_API_KEY"] = "test-key"
    success = asyncio.run(test_agent_with_mock_pipeline())
    exit(0 if success else 1)
