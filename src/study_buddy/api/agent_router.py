"""Agent API router for the Study Buddy application"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List

from ..models import AgentRequest, AgentResponse, AgentMode
from ..agent.study_agent import StudyAgent

# Create router
agent_router = APIRouter(prefix="/agent", tags=["Study Agent"])


def get_agent(request: Request) -> StudyAgent:
    """
    Get Study Agent from app state.
    
    The agent is created once at app startup via the lifespan manager.
    """
    if not hasattr(request.app.state, "study_agent") or request.app.state.study_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Study Agent not initialized. Please try again later."
        )
    return request.app.state.study_agent


@agent_router.post("", response_model=AgentResponse)
async def process_agent_request(
    request: AgentRequest,
    agent: StudyAgent = Depends(get_agent)
) -> AgentResponse:
    """
    Process a study agent request.
    
    Modes:
    - **flashcards**: Generate study flashcards from content
    - **mcq**: Generate multiple choice questions (requires doc_id)
    - **explain**: Explain a concept (uses RAG if doc_id provided)
    - **summarize**: Summarize document content (requires doc_id)
    - **auto-study**: ReAct agent that chains multiple tools as needed
    
    Request body:
    - **mode**: One of 'flashcards', 'mcq', 'explain', 'summarize', 'auto-study'
    - **input**: User's question or topic
    - **session_id**: Optional session ID for conversation continuity
    - **doc_id**: Document ID (required for mcq/summarize, optional for others)
    - **num_questions**: Number of questions/flashcards to generate (default: 5)
    """
    # Validate input is not empty for modes that require it
    if not request.input.strip() and request.mode not in [AgentMode.SUMMARIZE]:
        raise HTTPException(
            status_code=400,
            detail="Input cannot be empty. Please provide a topic or question."
        )
    
    try:
        response = await agent.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@agent_router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_sessions(
    agent: StudyAgent = Depends(get_agent)
) -> List[Dict[str, Any]]:
    """List all active study sessions"""
    return agent.list_sessions()


@agent_router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    agent: StudyAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """Get information about a specific session"""
    info = agent.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return info


@agent_router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    agent: StudyAgent = Depends(get_agent)
) -> Dict[str, str]:
    """Delete a study session"""
    if agent.delete_session(session_id):
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")


@agent_router.post("/sessions/{session_id}/clear")
async def clear_session_history(
    session_id: str,
    agent: StudyAgent = Depends(get_agent)
) -> Dict[str, str]:
    """Clear conversation history for a session (keeps session alive)"""
    if agent.clear_session(session_id):
        return {"status": "cleared", "session_id": session_id}
    raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")


@agent_router.get("/modes")
async def list_available_modes() -> Dict[str, Any]:
    """List available agent modes and their descriptions"""
    return {
        "modes": {
            "flashcards": {
                "description": "Generate study flashcards from content",
                "requires_doc_id": False,
                "parameters": ["num_questions"]
            },
            "mcq": {
                "description": "Generate multiple choice questions with explanations",
                "requires_doc_id": True,
                "parameters": ["num_questions", "include_explanations"]
            },
            "explain": {
                "description": "Explain a concept in a clear, simplified way",
                "requires_doc_id": False,
                "parameters": []
            },
            "summarize": {
                "description": "Summarize document content",
                "requires_doc_id": True,
                "parameters": []
            },
            "auto-study": {
                "description": "AI agent that chains tools to help you study",
                "requires_doc_id": False,
                "parameters": []
            }
        }
    }
