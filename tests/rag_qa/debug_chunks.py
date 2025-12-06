import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker

# Create test file
test_text = """Machine Learning is a subset of AI.
There are three types: supervised, unsupervised, reinforcement.
Neural networks have layers."""

Path("debug.txt").write_text(test_text)

# Chunk it
chunker = TextChunker(chunk_size=100, chunk_overlap=20)
chunks = chunker.chunk_document(Path("debug.txt"))

print("Chunks created:")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i}:")
    print(f"Text: '{chunk['text'][:50]}...'")
    print(f"Length: {len(chunk['text'])} chars")
    print(f"Metadata: {chunk['metadata']}")

# Cleanup
Path("debug.txt").unlink()

