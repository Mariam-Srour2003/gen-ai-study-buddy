from pydantic import BaseModel
from typing import List, Optional

class Flashcard(BaseModel):
    question: str
    answer: str
    mnemonic: str

class FlashcardsRequest(BaseModel):
    text: str

class FlashcardsResponse(BaseModel):
    flashcards: List[Flashcard]

class QuizQuestion(BaseModel):
    question: str
    correct_answer: str
    options: Optional[List[str]] = None

class QuizRequest(BaseModel):
    text: str

class QuizResponse(BaseModel):
    quiz_questions: List[QuizQuestion]

class IngestTextRequest(BaseModel):
    doc_id: str
    text: str

class IngestResponse(BaseModel):
    status: str
    doc_id: str

class QueryRequest(BaseModel):
    doc_id: str
    question: str
    mode: Optional[str] = "normal"  # or "eli5"

class QueryResponse(BaseModel):
    answer: str
    citations: List[str]
