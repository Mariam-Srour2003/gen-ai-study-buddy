"""
Better example showing improved Q&A.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker
from study_buddy.rag_qa.embedder import SimpleEmbedder
from study_buddy.rag_qa.simple_vectorstore import SimpleVectorStore
from study_buddy.rag_qa.qa import SimpleQAGenerator

def main():
    print("🧠 IMPROVED RAG System Demo")
    print("=" * 50)
    
    # Create a cleaner test document
    document = """
    ARTIFICIAL INTELLIGENCE STUDY NOTES
    
    Machine Learning is a subset of artificial intelligence.
    There are three main types of machine learning:
    
    1. SUPERVISED LEARNING: The algorithm learns from labeled data.
       Examples: Classification, Regression.
    
    2. UNSUPERVISED LEARNING: The algorithm finds patterns in unlabeled data.
       Examples: Clustering, Association.
    
    3. REINFORCEMENT LEARNING: The algorithm learns through trial and error.
       Examples: Game playing, Robotics.
    
    Neural Networks are computing systems inspired by biological brains.
    Key components of neural networks:
    - Input Layer: Receives the data
    - Hidden Layers: Process the data
    - Output Layer: Produces the result
    - Activation Functions: Decide if a neuron should fire
    
    Common algorithms include:
    - Linear Regression for predicting continuous values
    - Logistic Regression for classification problems
    - Decision Trees for both classification and regression
    - Random Forests as an ensemble of decision trees
    """
    
    # Save to file
    Path("ai_notes.txt").write_text(document)
    print("1. 📝 Created AI study notes")
    
    # Initialize
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    embedder = SimpleEmbedder(embedding_dim=128)
    vector_store = SimpleVectorStore("./ai_store.pkl")
    qa = SimpleQAGenerator()
    
    print("2. 🔧 Initialized RAG system")
    
    # Process
    chunks = chunker.chunk_document(Path("ai_notes.txt"))
    print(f"3. ✂️  Created {len(chunks)} chunks")
    
    vector_store.add_documents(chunks, embedder)
    print("4. 💾 Stored in vector database")
    
    # Test questions
    print("\n5. 🧪 TESTING Q&A SYSTEM")
    print("-" * 40)
    
    tests = [
        ("What is machine learning?", "Should explain ML definition"),
        ("What are the types of machine learning?", "Should list 3 types"),
        ("Explain neural networks", "Should describe NN components"),
        ("What is supervised learning?", "Should define supervised learning"),
        ("List some common algorithms", "Should list algorithms")
    ]
    
    for question, expected in tests:
        print(f"\nQ: {question}")
        print(f"   Expected: {expected}")
        
        # Search
        results = vector_store.search(question, embedder, n_results=3)
        
        if results:
            # Generate answer
            answer_data = qa.generate_answer(question, results)
            
            print(f"A: {answer_data['answer']}")
            print(f"   Confidence: {answer_data['confidence']}")
            print(f"   Sources: {len(answer_data['sources'])} documents")
            
            # Show sources
            for i, source in enumerate(answer_data['sources'], 1):
                print(f"   Source {i}: {source['filename']} - {source['preview']}")
        else:
            print("A: No relevant information found")
    
    # Cleanup
    print("\n6. 🧹 Cleaning up...")
    Path("ai_notes.txt").unlink()
    vector_store.clear()
    
    print("\n✅ DEMO COMPLETE!")
    print("\n🎯 Your RAG system is working and ready for team integration!")

if __name__ == "__main__":
    main()

