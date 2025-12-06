"""
Q&A module for RAG system.
Generates answers from retrieved document chunks.
"""

from typing import List, Dict, Any
import re

class SimpleQAGenerator:
    """Simple Q&A generator for testing."""
    
    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer from retrieved context chunks.
        
        Args:
            question: User's question
            context_chunks: List of relevant text chunks with metadata
            
        Returns:
            Dictionary with answer and sources
        """
        if not context_chunks:
            return {
                "answer": "I don't have enough information to answer that question.",
                "sources": [],
                "confidence": 0.0,
                "chunks_used": 0
            }
        
        # Extract and clean context text
        context_texts = []
        for chunk in context_chunks[:3]:  # Use top 3 chunks
            text = chunk.get('text', '').strip()
            if text:
                # Clean up the text
                text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
                text = re.sub(r'\n+', ' ', text)  # Remove newlines
                context_texts.append(text)
        
        if not context_texts:
            return {
                "answer": "No readable content found in the documents.",
                "sources": [],
                "confidence": 0.0,
                "chunks_used": 0
            }
        
        # Combine context
        combined_context = " ".join(context_texts)
        
        # Simple keyword matching for answer generation
        question_lower = question.lower()
        
        # Try to find relevant sentences
        sentences = re.split(r'[.!?]+', combined_context)
        relevant_sentences = []
        
        # Extract keywords from question (remove common words)
        question_keywords = set(question_lower.split())
        common_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'explain', 'list', 'some', 'me', 'about'}
        question_keywords = [kw for kw in question_keywords if kw not in common_words and len(kw) > 2]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            sentence_lower = sentence.lower()
            
            # Check if sentence contains question keywords
            if question_keywords:
                keyword_match = any(keyword in sentence_lower for keyword in question_keywords)
            else:
                # If no specific keywords, use first few sentences
                keyword_match = len(relevant_sentences) < 2
            
            if keyword_match:
                relevant_sentences.append(sentence)
                if len(relevant_sentences) >= 2:  # Limit to 2 sentences
                    break
        
        # Generate answer
        if relevant_sentences:
            answer = "Based on the study material: " + ". ".join(relevant_sentences) + "."
        else:
            # Fallback: use most relevant-looking parts
            # Find sentences that look like definitions or lists
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and (':' in sentence or sentence[0].isdigit()):
                    answer = f"I found this information: {sentence}"
                    break
            else:
                # Last resort: first reasonable sentence
                for sentence in sentences:
                    if len(sentence) > 40:
                        answer = f"According to the material: {sentence}"
                        break
                else:
                    answer = f"Relevant information: {combined_context[:200]}..."
        
        # Extract sources
        sources = []
        for chunk in context_chunks[:2]:
            metadata = chunk.get('metadata', {})
            text = chunk.get('text', '')
            text_preview = text[:80].replace('\n', ' ') + '...' if len(text) > 80 else text
            sources.append({
                'filename': metadata.get('filename', 'Unknown document'),
                'chunk_id': metadata.get('chunk_id', 0),
                'preview': text_preview
            })
        
        # Calculate confidence
        confidence = min(0.9, len(context_chunks) * 0.2)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": round(confidence, 2),
            "chunks_used": len(context_chunks)
        }

