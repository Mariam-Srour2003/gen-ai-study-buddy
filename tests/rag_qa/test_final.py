import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker

# Create a proper test file
test_content = """Artificial Intelligence (AI) is intelligence demonstrated by machines.

Machine Learning (ML) is a subset of AI. ML provides systems the ability to learn from data.

There are three main types of machine learning:
1. Supervised Learning
2. Unsupervised Learning  
3. Reinforcement Learning

Neural Networks are computing systems inspired by biological brains.
They consist of layers: input, hidden, and output layers.
Activation functions like ReLU and Sigmoid are used.
"""

Path("test_final.txt").write_text(test_content)

# Test chunking
chunker = TextChunker(chunk_size=150, chunk_overlap=30)
chunks_data = chunker.chunk_document(Path("test_final.txt"))

print("FINAL CHUNKING TEST")
print("=" * 50)
print(f"Created {len(chunks_data)} chunks")
print("\nChunks:")

for i, chunk_data in enumerate(chunks_data):
    print(f"\n--- Chunk {i} ---")
    text = chunk_data['text']
    print(f"Text: {text[:80]}..." if len(text) > 80 else f"Text: {text}")
    print(f"Length: {len(text)} chars")
    print(f"Metadata: {chunk_data['metadata']}")

# Cleanup
Path("test_final.txt").unlink()

