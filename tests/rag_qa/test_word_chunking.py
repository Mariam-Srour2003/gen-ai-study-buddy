import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker

# Test text
test_text = """Artificial Intelligence (AI) is intelligence demonstrated by machines.

Machine Learning (ML) is a subset of AI. ML provides systems the ability to learn from data.

There are three main types of machine learning:
1. Supervised Learning
2. Unsupervised Learning  
3. Reinforcement Learning

Neural Networks are computing systems inspired by biological brains.
They consist of layers: input, hidden, and output layers.
Activation functions like ReLU and Sigmoid are used."""

Path("test_word.txt").write_text(test_text)

# Test
chunker = TextChunker(chunk_size=150, chunk_overlap=50)
chunks_data = chunker.chunk_document(Path("test_word.txt"))

print("WORD-BASED CHUNKING TEST")
print("=" * 50)
print(f"Created {len(chunks_data)} chunks")
print("\nChunks (showing start/end):")

for i, chunk_data in enumerate(chunks_data):
    text = chunk_data['text']
    print(f"\n--- Chunk {i} ---")
    print(f"Start: {text[:50]}...")
    print(f"End: ...{text[-50:]}")
    print(f"Length: {len(text)} chars")
    print(f"Words: {len(text.split())}")

# Cleanup
Path("test_word.txt").unlink()

