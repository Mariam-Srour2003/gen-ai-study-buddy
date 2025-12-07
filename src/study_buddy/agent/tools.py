"""LangChain tools for the Study Agent"""

import json
import logging
import re
from typing import List, Dict, Any, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from ..models import MCQQuestion, MCQOption, Flashcard
from ..rag_qa.qa import RAGPipeline

logger = logging.getLogger(__name__)


# ============== Tool Input Schemas ==============

class MCQInput(BaseModel):
    """Input schema for MCQ generation tool"""
    topic: str = Field(..., description="Topic or question to generate MCQs about")
    num_questions: int = Field(default=5, description="Number of questions to generate (1-20)")
    doc_id: Optional[str] = Field(default=None, description="Document ID to use for context")
    include_explanations: bool = Field(default=True, description="Include explanations for each option")


class FlashcardInput(BaseModel):
    """Input schema for flashcard generation tool"""
    topic: str = Field(..., description="Topic to generate flashcards about")
    num_cards: int = Field(default=5, description="Number of flashcards to generate (1-20)")
    doc_id: Optional[str] = Field(default=None, description="Document ID to use for context")


class ExplainInput(BaseModel):
    """Input schema for explain tool"""
    concept: str = Field(..., description="Concept or topic to explain")
    doc_id: Optional[str] = Field(default=None, description="Document ID to use for context (optional)")


class SummarizeInput(BaseModel):
    """Input schema for summarize tool"""
    topic: str = Field(default="", description="Specific topic to focus on (optional)")
    doc_id: str = Field(..., description="Document ID to summarize")


# ============== Base Tool Class ==============

class BaseStudyTool(BaseTool):
    """Base class for study tools with shared functionality"""
    
    pipeline: RAGPipeline = None
    llm: BaseChatModel = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_rag_context(self, doc_id: str, query: str, k: int = 5) -> tuple[str, List[str]]:
        """Retrieve context from RAG pipeline"""
        if not self.pipeline or not doc_id:
            return "", []
        
        # Validate query is not empty - use fallback if needed
        if not query or not query.strip():
            query = "main concepts key points important information summary"
        
        try:
            result = self.pipeline.query(doc_id, query, k=k)
            context = result.get("answer", "").replace("Based on retrieved context:\n\n", "")
            citations = [c.get("text", "") for c in result.get("citations", [])]
            return context, citations
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return "", []
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from potentially markdown-wrapped LLM response"""
        text = text.strip()
        
        # Try to find JSON in code blocks
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if match:
            return match.group(1).strip()
        
        # Try to find raw JSON object
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group(0)
        
        return text


# ============== MCQ Generator Tool ==============

class MCQGeneratorTool(BaseStudyTool):
    """Tool for generating multiple choice questions from document content"""
    
    name: str = "mcq_generator"
    description: str = """Generate multiple choice questions (MCQ) from document content.
    Use this tool when the user wants to test their knowledge with quiz questions.
    Requires a document ID to retrieve relevant content.
    Returns questions with 4 options each, with explanations for each option."""
    args_schema: Type[BaseModel] = MCQInput
    
    def _run(
        self,
        topic: str,
        num_questions: int = 5,
        doc_id: Optional[str] = None,
        include_explanations: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Generate MCQ questions"""
        logger.info(f"Generating {num_questions} MCQs on topic: {topic} (explanations: {include_explanations})")
        
        # Validate doc_id is provided
        if not doc_id:
            return {
                "error": "Document ID is required for MCQ generation",
                "questions": [],
                "warning": "Please specify a document to generate questions from"
            }
        
        # Get RAG context
        context, sources = self._get_rag_context(doc_id, topic, k=8)
        
        if not context:
            return {
                "error": f"No content found in document '{doc_id}'",
                "questions": [],
                "warning": "Document may be empty or not ingested"
            }
        
        # Build explanation instruction based on flag
        explanation_instruction = ""
        explanation_field = ""
        if include_explanations:
            explanation_instruction = "4. Include a clear explanation for why each option is correct or incorrect"
            explanation_field = ', "explanation": "Why this is wrong/correct"'
        else:
            explanation_instruction = "4. No explanations needed"
            explanation_field = ""
        
        # Generate MCQs using LLM
        prompt = f"""You are an expert educator creating multiple choice questions for adult learners.

Based on the following content, generate exactly {num_questions} multiple choice questions.
Each question should:
1. Test understanding of key concepts
2. Have exactly 4 options (A, B, C, D)
3. Have only ONE correct answer
{explanation_instruction}

CONTENT:
{context}

TOPIC FOCUS: {topic}

Respond in this exact JSON format:
{{
    "questions": [
        {{
            "question": "The question text?",
            "options": [
                {{"label": "A", "text": "Option A text", "is_correct": false{explanation_field}}},
                {{"label": "B", "text": "Option B text", "is_correct": true{explanation_field}}},
                {{"label": "C", "text": "Option C text", "is_correct": false{explanation_field}}},
                {{"label": "D", "text": "Option D text", "is_correct": false{explanation_field}}}
            ],
            "difficulty": "medium",
            "topic": "Specific topic tested"
        }}
    ]
}}

Generate {num_questions} questions. If the content is insufficient, generate as many as possible.
IMPORTANT: Return ONLY valid JSON, no markdown or extra text."""

        try:
            response = self.llm.invoke(prompt)
            content = self._extract_json(response.content)
            
            result = json.loads(content)
            questions = result.get("questions", [])
            
            # Build response
            mcq_questions = []
            for q in questions:
                options = [
                    MCQOption(
                        label=opt.get("label", ""),
                        text=opt.get("text", ""),
                        is_correct=opt.get("is_correct", False),
                        explanation=opt.get("explanation", "")
                    )
                    for opt in q.get("options", [])
                ]
                mcq_questions.append(MCQQuestion(
                    question=q.get("question", ""),
                    options=options,
                    difficulty=q.get("difficulty", "medium"),
                    topic=q.get("topic", topic)
                ))
            
            warning = None
            if len(mcq_questions) < num_questions:
                warning = f"Only {len(mcq_questions)} questions could be generated from available content"
            
            return {
                "questions": [q.model_dump() for q in mcq_questions],
                "total_questions": len(mcq_questions),
                "requested_questions": num_questions,
                "warning": warning,
                "doc_id": doc_id,
                "sources": sources[:3]
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCQ response: {e}")
            return {
                "error": "Failed to generate valid MCQ format",
                "questions": [],
                "warning": "LLM response was not valid JSON"
            }
        except Exception as e:
            logger.error(f"MCQ generation error: {e}")
            return {
                "error": str(e),
                "questions": [],
                "warning": "An error occurred during MCQ generation"
            }


# ============== Flashcard Generator Tool ==============

class FlashcardGeneratorTool(BaseStudyTool):
    """Tool for generating flashcards from document content"""
    
    name: str = "flashcard_generator"
    description: str = """Generate study flashcards from document content.
    Use this tool when the user wants to create flashcards for memorization and review.
    Each flashcard has a question, answer, and optional mnemonic device."""
    args_schema: Type[BaseModel] = FlashcardInput
    
    def _run(
        self,
        topic: str,
        num_cards: int = 5,
        doc_id: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Generate flashcards"""
        logger.info(f"Generating {num_cards} flashcards on topic: {topic}")
        
        # Get RAG context if doc_id provided
        context = ""
        sources = []
        if doc_id:
            context, sources = self._get_rag_context(doc_id, topic, k=6)
        
        context_instruction = f"\n\nBased on this content:\n{context}" if context else ""
        
        prompt = f"""You are an expert educator creating flashcards for adult learners.

Generate exactly {num_cards} flashcards about: {topic}{context_instruction}

Each flashcard should:
1. Have a clear, specific question
2. Have a concise but complete answer
3. Include a helpful mnemonic or memory trick (if applicable)

Respond in this exact JSON format:
{{
    "flashcards": [
        {{
            "question": "What is X?",
            "answer": "X is...",
            "mnemonic": "Remember it as..."
        }}
    ]
}}

Generate {num_cards} flashcards. Be clear and educational.
IMPORTANT: Return ONLY valid JSON, no markdown or extra text."""

        try:
            response = self.llm.invoke(prompt)
            content = self._extract_json(response.content)
            
            result = json.loads(content)
            flashcards = [
                Flashcard(
                    question=fc.get("question", ""),
                    answer=fc.get("answer", ""),
                    mnemonic=fc.get("mnemonic", "")
                )
                for fc in result.get("flashcards", [])
            ]
            
            return {
                "flashcards": [fc.model_dump() for fc in flashcards],
                "count": len(flashcards),
                "doc_id": doc_id,
                "sources": sources[:3] if sources else []
            }
            
        except Exception as e:
            logger.error(f"Flashcard generation error: {e}")
            return {
                "error": str(e),
                "flashcards": [],
                "warning": "Failed to generate flashcards"
            }


# ============== Explain Tool ==============

class ExplainTool(BaseStudyTool):
    """Tool for explaining concepts in a simplified way"""
    
    name: str = "explain_concept"
    description: str = """Explain a concept in a clear, simplified way for non-expert adults.
    Use this tool when the user wants to understand something better.
    Uses document content for context if doc_id is provided, otherwise uses general knowledge."""
    args_schema: Type[BaseModel] = ExplainInput
    
    def _run(
        self,
        concept: str,
        doc_id: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Explain a concept"""
        logger.info(f"Explaining concept: {concept}")
        
        # Get RAG context if doc_id provided
        context = ""
        sources = []
        if doc_id:
            context, sources = self._get_rag_context(doc_id, concept, k=5)
        
        context_instruction = ""
        if context:
            context_instruction = f"""
Use the following content as your primary source:
{context}

Base your explanation on this content, but make it clearer and more accessible."""
        
        prompt = f"""You are a friendly, expert educator explaining concepts to non-expert adults.

Explain this concept: {concept}
{context_instruction}

Your explanation should:
1. Be clear and easy to understand (no jargon, or explain jargon when necessary)
2. Use simple analogies and real-world examples
3. Break down complex ideas into digestible parts
4. Be conversational and engaging
5. Be thorough but not overwhelming

Provide a clear, helpful explanation:"""

        try:
            response = self.llm.invoke(prompt)
            explanation = response.content.strip()
            
            return {
                "explanation": explanation,
                "concept": concept,
                "doc_id": doc_id,
                "sources": sources[:3] if sources else [],
                "used_document": bool(context)
            }
            
        except Exception as e:
            logger.error(f"Explain error: {e}")
            return {
                "error": str(e),
                "explanation": "",
                "warning": "Failed to generate explanation"
            }


# ============== Summarize Tool ==============

class SummarizeTool(BaseStudyTool):
    """Tool for summarizing document content"""
    
    name: str = "summarize_document"
    description: str = """Summarize document content in a clear, concise way.
    Use this tool when the user wants a summary or overview of a document.
    Requires a document ID."""
    args_schema: Type[BaseModel] = SummarizeInput
    
    def _run(
        self,
        doc_id: str,
        topic: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Summarize document content"""
        logger.info(f"Summarizing document: {doc_id}")
        
        if not doc_id:
            return {
                "error": "Document ID is required for summarization",
                "summary": "",
                "warning": "Please specify a document to summarize"
            }
        
        # Get document content - use broader query for summary
        query = topic if topic else "main concepts key points important information"
        context, sources = self._get_rag_context(doc_id, query, k=10)
        
        if not context:
            return {
                "error": f"No content found in document '{doc_id}'",
                "summary": "",
                "warning": "Document may be empty or not ingested"
            }
        
        topic_focus = f"\n\nFocus especially on: {topic}" if topic else ""
        
        prompt = f"""You are an expert at creating clear, useful summaries for adult learners.

Summarize the following content in a clear, organized way:

{context}
{topic_focus}

Your summary should:
1. Capture the main ideas and key points
2. Be well-organized (use bullet points or sections if helpful)
3. Be concise but complete
4. Highlight the most important takeaways
5. Be easy to understand for non-experts

Provide a helpful summary:"""

        try:
            response = self.llm.invoke(prompt)
            summary = response.content.strip()
            
            return {
                "summary": summary,
                "doc_id": doc_id,
                "topic": topic,
                "sources": sources[:5] if sources else []
            }
            
        except Exception as e:
            logger.error(f"Summarize error: {e}")
            return {
                "error": str(e),
                "summary": "",
                "warning": "Failed to generate summary"
            }


# ============== Tool Factory ==============

def create_study_tools(
    pipeline: RAGPipeline,
    llm: BaseChatModel
) -> List[BaseTool]:
    """Create all study tools with shared dependencies"""
    
    tools = [
        MCQGeneratorTool(pipeline=pipeline, llm=llm),
        FlashcardGeneratorTool(pipeline=pipeline, llm=llm),
        ExplainTool(pipeline=pipeline, llm=llm),
        SummarizeTool(pipeline=pipeline, llm=llm),
    ]
    
    return tools
