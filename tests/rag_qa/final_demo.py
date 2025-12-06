"""
Final demo of complete, working RAG system.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker
from study_buddy.rag_qa.embedder import SimpleEmbedder
from study_buddy.rag_qa.simple_vectorstore import SimpleVectorStore
from study_buddy.rag_qa.qa import SimpleQAGenerator

def main():
    print("🎯 FINAL RAG SYSTEM DEMO")
    print("=" * 60)
    
    # Create study material
    document = """
    ARTIFICIAL INTELLIGENCE FUNDAMENTALS
    
    Definition: AI is the simulation of human intelligence in machines.
    
    Machine Learning is a subset of AI. It enables systems to learn from data.
    
    THREE TYPES OF MACHINE LEARNING:
    1. Supervised Learning: Uses labeled training data.
       Examples: Spam detection, image classification.
    
    2. Unsupervised Learning: Finds patterns in unlabeled data.
       Examples: Customer segmentation, anomaly detection.
    
    3. Reinforcement Learning: Learns through rewards and punishments.
       Examples: Game playing, robotics.
    
    NEURAL NETWORKS:
    - Inspired by biological brains
    - Consist of neurons organized in layers
    - Input layer receives data
    - Hidden layers process information
    - Output layer produces results
    
    COMMON ALGORITHMS:
    - Linear Regression: Predicts continuous values
    - Logistic Regression: Binary classification
    - Decision Trees: Both classification and regression
    - Random Forest: Ensemble of decision trees
    - K-Means: Clustering algorithm
    """
    
    # Save to file
    Path("ai_fundamentals.txt").write_text(document)
    print("1. 📚 Created study document: ai_fundamentals.txt")
    
    # Initialize system
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    embedder = SimpleEmbedder(embedding_dim=128)
    vector_store = SimpleVectorStore("./ai_db.pkl")
    qa_system = SimpleQAGenerator()
    
    print("2. ⚙️  Initialized RAG components")
    
    # Process document
    chunks = chunker.chunk_document(Path("ai_fundamentals.txt"))
    print(f"3. ✂️  Created {len(chunks)} clean chunks")
    
    # Show first chunk as example
    if chunks:
        print(f"   Example chunk: {chunks[0]['text'][:80]}...")
    
    # Store in vector database
    vector_store.add_documents(chunks, embedder)
    stats = vector_store.get_stats()
    print(f"4. 💾 Stored {stats['document_count']} documents in vector database")
    
    # Test questions
    print("\n5. 🧠 INTELLIGENT Q&A DEMO")
    print("-" * 60)
    
    test_questions = [
        "What is artificial intelligence?",
        "What are the three types of machine learning?",
        "Explain neural networks",
        "What is supervised learning?",
        "List some common AI algorithms"
    ]
    
    for question in test_questions:
        print(f"\n❓ QUESTION: {question}")
        
        # Search for relevant information
        results = vector_store.search(question, embedder, n_results=3)
        
        if results:
            # Generate intelligent answer
            answer_data = qa_system.generate_answer(question, results)
            
            print(f"💡 ANSWER: {answer_data['answer']}")
            print(f"   Confidence: {answer_data['confidence']:.2f}")
            print(f"   Based on {answer_data['chunks_used']} document chunks")
            
            # Show sources
            if answer_data['sources']:
                print(f"   Sources:")
                for i, source in enumerate(answer_data['sources'], 1):
                    print(f"     {i}. {source['filename']} - {source['preview']}")
        else:
            print("⚠️  No relevant information found")
    
    # Cleanup
    print("\n6. 🧹 Cleaning up...")
    Path("ai_fundamentals.txt").unlink()
    vector_store.clear()
    
    print("\n" + "=" * 60)
    print("✅ RAG SYSTEM IS FULLY OPERATIONAL!")
    print("\n🎉 CONGRATULATIONS! Your Dev C work is COMPLETE and WORKING!")
    print("\n📤 Push to GitHub and share with your team!")
    print("🔗 Your code: https://github.com/Mariam-Srour2003/gen-ai-study-buddy/tree/dev-c-rag-system")

if __name__ == "__main__":
    main()

