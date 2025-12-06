"""
Example of using the complete RAG system.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker
from study_buddy.rag_qa.embedder import SimpleEmbedder
from study_buddy.rag_qa.simple_vectorstore import SimpleVectorStore
from study_buddy.rag_qa.qa import SimpleQAGenerator

def main():
    print("📚 Study Buddy RAG System - Complete Example")
    print("=" * 50)
    
    # 1. Create a study document
    document = """
    Machine Learning Types:
    1. Supervised Learning: Uses labeled data (e.g., classification, regression)
    2. Unsupervised Learning: Finds patterns in unlabeled data (e.g., clustering)
    3. Reinforcement Learning: Learns through rewards/punishments
    
    Neural Networks:
    - Consist of layers (input, hidden, output)
    - Use activation functions like ReLU, Sigmoid
    - Trained with backpropagation
    
    Key Algorithms:
    - Linear Regression: Predicts continuous values
    - Logistic Regression: For classification
    - K-Means: Clustering algorithm
    - Random Forest: Ensemble of decision trees
    """
    
    # Save to file
    Path("ml_notes.txt").write_text(document)
    
    print("1. 📝 Created study document: ml_notes.txt")
    
    # 2. Initialize components
    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    embedder = SimpleEmbedder(embedding_dim=128)
    vector_store = SimpleVectorStore("./ml_store.pkl")
    qa_generator = SimpleQAGenerator()
    
    print("2. 🔧 Initialized all RAG components")
    
    # 3. Process document
    chunks = chunker.chunk_document(Path("ml_notes.txt"))
    print(f"3. ✂️  Split into {len(chunks)} chunks")
    
    # 4. Add to vector store
    vector_store.add_documents(chunks, embedder)
    print("4. 💾 Added to vector store")
    
    # 5. Ask questions
    questions = [
        "What are the types of machine learning?",
        "Explain neural networks",
        "What is supervised learning?",
        "List some key algorithms"
    ]
    
    print("\n5. ❓ Q&A Examples:")
    print("-" * 30)
    
    for question in questions:
        print(f"\nQ: {question}")
        
        # Search for relevant chunks
        results = vector_store.search(question, embedder, n_results=3)
        
        # Generate answer
        answer_data = qa_generator.generate_answer(question, results)
        
        print(f"A: {answer_data['answer'][:100]}...")
        print(f"   Confidence: {answer_data['confidence']:.2f}")
        print(f"   Sources: {len(answer_data['sources'])}")
    
    # 6. Cleanup
    print("\n6. 🧹 Cleaning up...")
    Path("ml_notes.txt").unlink()
    vector_store.clear()
    
    print("\n✅ Example complete!")
    print("\n📁 Your RAG system is ready for integration with:")
    print("   - Dev A: API endpoints for ingestion/Q&A")
    print("   - Dev B: Flashcard generation from documents")
    print("\n🚀 Push to GitHub and share with your team!")

if __name__ == "__main__":
    main()

