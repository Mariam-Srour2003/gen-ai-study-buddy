"""Study Agent - LangChain-based agent for study assistance"""

import logging
from typing import Dict, Any, List, Optional, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from .session_manager import SessionManager, Session
from .tools import create_study_tools
from ..models import (
    AgentMode,
    AgentRequest,
    AgentResponse,
    MCQResponse,
    MCQQuestion,
    MCQOption,
    Flashcard,
)
from ..rag_qa.qa import RAGPipeline

logger = logging.getLogger(__name__)


def create_llm(
    provider: Literal["google", "ollama"],
    model: str,
    temperature: float = 0.7,
    google_api_key: str = None,
    ollama_base_url: str = "http://localhost:11434"
) -> BaseChatModel:
    """
    Factory function to create LLM based on provider.
    
    Args:
        provider: Either "google" or "ollama"
        model: Model name for the provider
        temperature: LLM temperature
        google_api_key: Google API key (required for Google provider)
        ollama_base_url: Ollama server URL
    
    Returns:
        LangChain chat model instance
    """
    if provider == "ollama":
        logger.info(f"Using Ollama LLM: {model} at {ollama_base_url}")
        return ChatOllama(
            model=model,
            base_url=ollama_base_url,
            temperature=temperature,
        )
    else:
        logger.info(f"Using Google Gemini LLM: {model}")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=google_api_key,
            temperature=temperature,
        )


# ReAct prompt template for auto-study mode
REACT_PROMPT = """You are a helpful study assistant that helps users learn and understand content.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be valid JSON)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT RULES:
1. Action Input must be valid JSON with the correct parameters for the tool
2. Use the document ID provided when available
3. Be helpful and educational in your final answer
4. For MCQs, use mcq_generator. For flashcards, use flashcard_generator.
5. For explanations, use explain_concept. For summaries, use summarize_document.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


class StudyAgent:
    """
    LangChain-based study agent with multiple tools and conversation memory.
    
    Supports modes:
    - flashcards: Generate study flashcards
    - mcq: Generate multiple choice questions
    - explain: Explain concepts in a simplified way
    - summarize: Summarize document content
    - auto-study: ReAct agent that chains tools as needed
    """
    
    def __init__(
        self,
        pipeline: RAGPipeline,
        llm_provider: Literal["google", "ollama"] = "google",
        llm_model: str = "gemini-2.0-flash",
        llm_temperature: float = 0.7,
        google_api_key: str = None,
        ollama_base_url: str = "http://localhost:11434",
        max_sessions: int = 100,
    ):
        """
        Initialize the Study Agent.
        
        Args:
            pipeline: RAG pipeline for document retrieval
            llm_provider: Either "google" or "ollama"
            llm_model: Model name for the selected provider
            llm_temperature: Temperature for LLM generation
            google_api_key: Google API key (required for Google provider)
            ollama_base_url: Ollama server URL
            max_sessions: Maximum number of concurrent sessions
        """
        logger.info(f"Initializing StudyAgent with provider: {llm_provider}, model: {llm_model}")
        
        self.pipeline = pipeline
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        
        # Initialize LLM using factory function
        self.llm = create_llm(
            provider=llm_provider,
            model=llm_model,
            temperature=llm_temperature,
            google_api_key=google_api_key,
            ollama_base_url=ollama_base_url,
        )
        
        # Initialize session manager
        self.session_manager = SessionManager(max_sessions=max_sessions)
        
        # Create tools
        self.tools = create_study_tools(pipeline, self.llm)
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        
        # Create ReAct agent for auto-study mode
        self._create_react_agent()
        
        logger.info("StudyAgent initialized successfully")
    
    def _create_react_agent(self) -> None:
        """Create the ReAct agent for auto-study mode"""
        prompt = PromptTemplate.from_template(REACT_PROMPT)
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,  # Disable verbose by default (can be enabled via settings)
            handle_parsing_errors=True,
            max_iterations=5,
        )
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process an agent request based on mode.
        
        Args:
            request: The agent request with mode and input
            
        Returns:
            AgentResponse with results
        """
        # Get or create session
        session = self.session_manager.get_or_create_session(request.session_id)
        
        # Track document if provided
        if request.doc_id:
            session.add_doc_id(request.doc_id)
        
        # Add user message to history
        session.add_human_message(request.input)
        
        # Route to appropriate handler
        try:
            if request.mode == AgentMode.MCQ:
                response = await self._handle_mcq(request, session)
            elif request.mode == AgentMode.FLASHCARDS:
                response = await self._handle_flashcards(request, session)
            elif request.mode == AgentMode.EXPLAIN:
                response = await self._handle_explain(request, session)
            elif request.mode == AgentMode.SUMMARIZE:
                response = await self._handle_summarize(request, session)
            elif request.mode == AgentMode.AUTO_STUDY:
                response = await self._handle_auto_study(request, session)
            else:
                response = AgentResponse(
                    mode=request.mode,
                    session_id=session.session_id,
                    message=f"Unknown mode: {request.mode}",
                    warning="Mode not supported"
                )
            
            # Add AI response to history
            if response.message:
                session.add_ai_message(response.message)
            elif response.mcq:
                session.add_ai_message(f"Generated {response.mcq.total_questions} MCQ questions")
            elif response.flashcards:
                session.add_ai_message(f"Generated {len(response.flashcards)} flashcards")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=f"An error occurred: {str(e)}",
                warning="Processing failed"
            )
    
    async def _handle_mcq(self, request: AgentRequest, session: Session) -> AgentResponse:
        """Handle MCQ generation request"""
        if not request.doc_id:
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message="Document ID is required for MCQ generation. Please upload a document first.",
                warning="Missing document ID"
            )
        
        tool = self.tools_by_name["mcq_generator"]
        result = tool._run(
            topic=request.input,
            num_questions=request.num_questions,
            doc_id=request.doc_id,
            include_explanations=request.include_explanations
        )
        
        if result.get("error"):
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=result.get("error"),
                warning=result.get("warning")
            )
        
        # Build MCQ response
        questions = []
        for q in result.get("questions", []):
            options = [
                MCQOption(**opt) for opt in q.get("options", [])
            ]
            questions.append(MCQQuestion(
                question=q.get("question", ""),
                options=options,
                difficulty=q.get("difficulty", "medium"),
                topic=q.get("topic", "")
            ))
        
        mcq_response = MCQResponse(
            questions=questions,
            total_questions=result.get("total_questions", 0),
            requested_questions=result.get("requested_questions", request.num_questions),
            warning=result.get("warning"),
            doc_id=request.doc_id
        )
        
        return AgentResponse(
            mode=request.mode,
            session_id=session.session_id,
            mcq=mcq_response,
            sources=result.get("sources", []),
            doc_ids_used=[request.doc_id],
            tools_used=["mcq_generator"],
            warning=result.get("warning")
        )
    
    async def _handle_flashcards(self, request: AgentRequest, session: Session) -> AgentResponse:
        """Handle flashcard generation request"""
        tool = self.tools_by_name["flashcard_generator"]
        result = tool._run(
            topic=request.input,
            num_cards=request.num_questions,
            doc_id=request.doc_id
        )
        
        if result.get("error"):
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=result.get("error"),
                warning=result.get("warning")
            )
        
        flashcards = [
            Flashcard(**fc) for fc in result.get("flashcards", [])
        ]
        
        doc_ids = [request.doc_id] if request.doc_id else []
        
        return AgentResponse(
            mode=request.mode,
            session_id=session.session_id,
            flashcards=flashcards,
            sources=result.get("sources", []),
            doc_ids_used=doc_ids,
            tools_used=["flashcard_generator"]
        )
    
    async def _handle_explain(self, request: AgentRequest, session: Session) -> AgentResponse:
        """Handle explain request"""
        tool = self.tools_by_name["explain_concept"]
        result = tool._run(
            concept=request.input,
            doc_id=request.doc_id
        )
        
        if result.get("error"):
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=result.get("error"),
                warning=result.get("warning")
            )
        
        doc_ids = [request.doc_id] if request.doc_id and result.get("used_document") else []
        
        return AgentResponse(
            mode=request.mode,
            session_id=session.session_id,
            message=result.get("explanation", ""),
            sources=result.get("sources", []),
            doc_ids_used=doc_ids,
            tools_used=["explain_concept"]
        )
    
    async def _handle_summarize(self, request: AgentRequest, session: Session) -> AgentResponse:
        """Handle summarize request"""
        if not request.doc_id:
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message="Document ID is required for summarization. Please upload a document first.",
                warning="Missing document ID"
            )
        
        tool = self.tools_by_name["summarize_document"]
        result = tool._run(
            doc_id=request.doc_id,
            topic=request.input if request.input else ""
        )
        
        if result.get("error"):
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=result.get("error"),
                warning=result.get("warning")
            )
        
        return AgentResponse(
            mode=request.mode,
            session_id=session.session_id,
            message=result.get("summary", ""),
            sources=result.get("sources", []),
            doc_ids_used=[request.doc_id],
            tools_used=["summarize_document"]
        )
    
    async def _handle_auto_study(self, request: AgentRequest, session: Session) -> AgentResponse:
        """Handle auto-study mode using ReAct agent"""
        # Build input with context
        input_text = request.input
        if request.doc_id:
            input_text = f"{request.input}\n\nUse document ID: {request.doc_id}"
        
        # Add conversation context
        if session.get_message_count() > 2:
            history = session.get_messages()[-6:-1]  # Last 3 exchanges (excluding current)
            context_parts = []
            for msg in history:
                if isinstance(msg, HumanMessage):
                    context_parts.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    context_parts.append(f"Assistant: {msg.content}")
            
            if context_parts:
                context = "\n".join(context_parts)
                input_text = f"Previous conversation:\n{context}\n\nCurrent request: {input_text}"
        
        try:
            # Run the ReAct agent
            result = await self.agent_executor.ainvoke({"input": input_text})
            output = result.get("output", "I couldn't complete the request.")
            
            # Extract tools used from intermediate steps
            tools_used = []
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if hasattr(step[0], "tool"):
                        tools_used.append(step[0].tool)
            
            doc_ids = [request.doc_id] if request.doc_id else list(session.doc_ids)
            
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=output,
                doc_ids_used=doc_ids,
                tools_used=tools_used or ["react_agent"]
            )
            
        except Exception as e:
            logger.error(f"Auto-study agent error: {e}")
            return AgentResponse(
                mode=request.mode,
                session_id=session.session_id,
                message=f"I encountered an issue processing your request. Error: {str(e)}",
                warning="Agent execution failed"
            )
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        session = self.session_manager.get_session(session_id)
        if session:
            return session.to_dict()
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return self.session_manager.list_sessions()
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session's conversation history"""
        session = self.session_manager.get_session(session_id)
        if session:
            session.clear_messages()
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        return self.session_manager.delete_session(session_id)
