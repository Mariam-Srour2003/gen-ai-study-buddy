"""
Q&A module for RAG system.
Generates answers from retrieved document chunks.
"""

from typing import List, Dict, Any
import re

class SimpleQAGenerator:
    """Simple Q&A generator for testing."""
    
    def __init__(self):
        self.prompts = {
            "explain": "Based on the following context:\n{context}\n\nAnswer: {question}",
            "summarize": "Summarize: {context}",
            "list": "List key points: {context}"
        }
    
    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer from context."""
        if not context_chunks:
            return {
                "answer": "No information found.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Simple extraction
        context = "\n".join([chunk['text'][:200] for chunk in context_chunks[:3]])
        
        # Simple answer generation
        if "?" in question:
            answer = f"I found this information: {context[:300]}..."
        else:
            answer = f"Based on the material: {context[:250]}"
        
        # Sources
        sources = []
        for chunk in context_chunks[:2]:
            metadata = chunk.get('metadata', {})
            sources.append({
                'filename': metadata.get('filename', 'Unknown'),
                'preview': chunk.get('text', '')[:50] + '...'
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": min(0.8, len(context_chunks) * 0.3),
            "chunks_used": len(context_chunks)
        }

