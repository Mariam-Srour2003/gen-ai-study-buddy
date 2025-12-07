from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ============== Enums ==============

class AgentMode(str, Enum):
    """Available agent modes"""
    FLASHCARDS = "flashcards"
    MCQ = "mcq"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    AUTO_STUDY = "auto-study"


# ============== Flashcard Models ==============

class Flashcard(BaseModel):
    """A single flashcard with question, answer, and mnemonic"""
    question: str
    answer: str
    mnemonic: str = ""


class FlashcardsRequest(BaseModel):
    text: str


class FlashcardsResponse(BaseModel):
    flashcards: List[Flashcard]


# ============== MCQ Models ==============

class MCQOption(BaseModel):
    """A single MCQ option"""
    label: str = Field(..., description="Option label (A, B, C, D)")
    text: str = Field(..., description="Option text")
    is_correct: bool = Field(default=False, description="Whether this is the correct answer")
    explanation: str = Field(default="", description="Explanation of why this option is correct/incorrect")


class MCQQuestion(BaseModel):
    """A single MCQ question with options and explanations"""
    question: str = Field(..., description="The question text")
    options: List[MCQOption] = Field(..., description="List of 4 options (A, B, C, D)")
    difficulty: str = Field(default="medium", description="Question difficulty: easy, medium, hard")
    topic: str = Field(default="", description="Topic or concept being tested")


class MCQResponse(BaseModel):
    """Response containing generated MCQ questions"""
    questions: List[MCQQuestion] = Field(default_factory=list)
    total_questions: int = Field(default=0)
    requested_questions: int = Field(default=5)
    warning: Optional[str] = Field(default=None, description="Warning if fewer questions generated")
    doc_id: str = Field(default="")


# ============== RAG Models ==============

class IngestResponse(BaseModel):
    status: str
    doc_id: str
    num_chunks: Optional[int] = None


class QueryRequest(BaseModel):
    doc_id: str
    question: str
    mode: Optional[str] = "normal"  # or "eli5"


class QueryResponse(BaseModel):
    answer: str
    citations: List[str]
    doc_id: str


# ============== Citation Models ==============

class Citation(BaseModel):
    """A citation with chunk metadata and relevance score"""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    score: float = Field(..., description="Relevance score (0-1)")
    text: str = Field(..., description="Preview text from the chunk")

# ============== Agent Models ==============

class AgentRequest(BaseModel):
    """Request to the Study Agent"""
    mode: AgentMode = Field(..., description="Agent mode: flashcards, mcq, explain, summarize, auto-study")
    input: str = Field(..., description="User input/question")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    doc_id: Optional[str] = Field(default=None, description="Document ID to query (required for mcq, optional for others)")
    
    # Mode-specific options
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of MCQ/flashcard questions to generate")
    include_explanations: bool = Field(default=True, description="Include explanations in MCQ responses")


class AgentResponse(BaseModel):
    """Response from the Study Agent"""
    mode: AgentMode = Field(..., description="Mode that was executed")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    
    # Content fields (populated based on mode)
    message: Optional[str] = Field(default=None, description="Text response for explain/summarize/auto-study")
    mcq: Optional[MCQResponse] = Field(default=None, description="MCQ questions for mcq mode")
    flashcards: Optional[List[Flashcard]] = Field(default=None, description="Flashcards for flashcards mode")
    
    # Metadata
    sources: List[Citation] = Field(default_factory=list, description="Source citations from RAG with metadata")
    doc_ids_used: List[str] = Field(default_factory=list, description="Document IDs used in response")
    tools_used: List[str] = Field(default_factory=list, description="Tools invoked (for auto-study mode)")
    warning: Optional[str] = Field(default=None, description="Any warnings")


class SessionInfo(BaseModel):
    """Information about a study session"""
    session_id: str
    doc_ids: List[str] = Field(default_factory=list)
    message_count: int = Field(default=0)
    created_at: str = Field(default="")
