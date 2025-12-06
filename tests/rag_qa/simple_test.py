import sys
from pathlib import Path

sys.path.insert(0, 'src')

from study_buddy.rag_qa.chunking import TextChunker

# Test with simple text
test_text = "Hello world. This is AI. Machine learning is cool. Neural networks are amazing."

chunker = TextChunker(chunk_size=30, chunk_overlap=10)
chunks = chunker.chunk_text(test_text)

print("Simple chunking test:")
print(f"Original: '{test_text}'")
print(f"\nChunks ({len(chunks)}):")
for i, chunk in enumerate(chunks):
    print(f"{i}: '{chunk}'")

