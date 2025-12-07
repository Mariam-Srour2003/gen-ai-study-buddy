# Study Buddy 📚

An intelligent AI-powered study companion that transforms your documents into interactive learning experiences. Upload PDFs, ask questions, generate flashcards, and take quizzes—all powered by advanced RAG (Retrieval-Augmented Generation) and LLM technology.

## Features ✨

### Core Capabilities

- **📄 Document Processing**: Upload and ingest PDF documents with automatic text extraction and chunking
- **🤖 AI Chat Interface**: Ask questions about your documents and get accurate, cited answers
- **📚 Flashcard Generation**: Automatically generate custom flashcards from document content
- **🧠 Quiz Generation**: Create multiple-choice quizzes to test your knowledge
- **🔍 RAG Pipeline**: Retrieve relevant content from documents to provide context-aware responses
- **💾 Vector Search**: Fast semantic search using FAISS with persistent indexing

### LLM Provider Support

- **Google Gemini**: Full support for Gemini 2.0 Flash and embedding models
- **Ollama**: Local LLM inference with models like Gemma3, Mistral, and more
- **Easy Switching**: Toggle between providers without restarting

### UI Features

- **🎨 Beautiful Web Interface**: Modern, pastel-themed single-page application
- **💬 Multi-turn Conversations**: Maintain conversation history with multiple chat sessions
- **📌 Citation Tracking**: See which document sections support each answer
- **⚡ Real-time Responses**: Streaming support for better UX
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

## System Architecture

```
┌─────────────────┐
│   Web UI        │  ← Vanilla HTML/CSS/JS (SPA)
└────────┬────────┘
         │
┌────────▼──────────────────────────────┐
│        FastAPI Backend                 │
├────────────────────────────────────────┤
│  • Document Ingestion (/rag/ingest)   │
│  • AI Agent (/agent)                  │
│  • Health Check (/health)             │
└────────────────┬───────────────────────┘
         │       │
    ┌────▼─┐  ┌──▼─────────────┐
    │ RAG  │  │ LLM Provider   │
    │ Core │  │  - Google      │
    └────┬─┘  │  - Ollama      │
         │    └────────────────┘
    ┌────▼──────────────┐
    │ Vector Store      │
    │ (FAISS Indices)   │
    └────────────────────┘
```

## Installation

### Prerequisites

- **Python**: 3.12 or higher
- **Git**: For cloning the repository
- **pip/uv**: Python package manager (uv recommended for speed)

### Step 1: Clone Repository

```bash
git clone https://github.com/Mariam-Srour2003/gen-ai-study-buddy.git
cd gen-ai-study-buddy
```

### Step 2: Set Up Python Environment

Using **uv** (recommended, faster):
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

Using traditional **pip**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

#### For Google Gemini Provider

```bash
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=google
EMBEDDING_PROVIDER=google
```

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

#### For Ollama Provider (Local)

```bash
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

Install Ollama from [ollama.ai](https://ollama.ai) and pull models:
```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
ollama serve  # In another terminal
```

### Step 4: Run the Application

```bash
# With Ollama (ensure ollama serve is running in another terminal)
export LLM_PROVIDER=ollama
export EMBEDDING_PROVIDER=ollama
uvicorn src.study_buddy.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# With Google
export GOOGLE_API_KEY=your_key_here
export LLM_PROVIDER=google
export EMBEDDING_PROVIDER=google
uvicorn src.study_buddy.main:app --reload --host 0.0.0.0 --port 8000
```

Or use uv:
```bash
uv run uvicorn src.study_buddy.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Usage Guide

### 1. Upload a Document

- Click the **Upload** button (📤 icon) in the bottom left
- Select a PDF file from your computer
- Wait for processing to complete

### 2. Chat with Your Document

- Type questions in the chat box
- Questions are answered using context from your uploaded document
- Each answer includes citations showing which parts of the document were used

### 3. Generate Flashcards

- Click the **📚 Flashcards** button in the top right
- Select the number of cards (4, 5, 10, or 15)
- Click **Generate** to create flashcards
- Click cards to flip them and reveal answers

### 4. Create Quizzes

- Click the **🧠 Quiz** button in the top right
- Select the number of questions (3, 5, or 10)
- Click **Generate** to create a quiz
- Answer questions and get immediate feedback

### 5. Switch Providers

- Use the **Provider** dropdown in the header
- Select between **Google** or **Ollama**
- Click **Apply** to switch

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | google | LLM provider: `google` or `ollama` |
| `EMBEDDING_PROVIDER` | google | Embedding provider: `google` or `ollama` |
| `GOOGLE_API_KEY` | - | Required for Google provider |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server URL |
| `OLLAMA_LLM_MODEL` | gemma3:4b | Ollama LLM model |
| `OLLAMA_EMBEDDING_MODEL` | nomic-embed-text:latest | Ollama embedding model |
| `CHUNK_SIZE` | 512 | Document chunk size |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |
| `TOP_K_RESULTS` | 3 | Number of retrieved results for RAG |
| `BASE_STORAGE_PATH` | ./storage_data | Storage location for indices and metadata |

### Storage Structure

```
storage_data/
├── faiss_indices/          # Vector indices (.index and .pkl files)
├── metadata/               # Chunk metadata and embeddings
└── uploaded_files/         # Original PDF files
```

## Project Structure

```
gen-ai-study-buddy/
├── src/study_buddy/
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models (Flashcard, MCQQuestion, etc.)
│   ├── config/
│   │   └── settings.py         # Configuration and environment variables
│   ├── api/
│   │   ├── routers.py          # RAG and health endpoints
│   │   ├── agent_router.py     # Agent endpoints
│   │   └── dependencies.py     # Dependency injection
│   ├── rag_qa/
│   │   ├── qa.py               # RAG pipeline orchestration
│   │   ├── vectorstore.py      # FAISS vector store
│   │   └── embedder.py         # Embedding providers
│   ├── ingestion/
│   │   ├── pdf_loader.py       # PDF text extraction
│   │   └── chunker.py          # Document chunking
│   ├── flashcards/
│   │   ├── generator.py        # Flashcard generation logic
│   │   └── templates.py        # Prompt templates
│   ├── agent/
│   │   ├── study_agent.py      # LangChain agent
│   │   └── tools.py            # Agent tools
│   ├── storage/
│   │   └── metadata.py         # Metadata persistence
│   └── ui/
│       └── app_ui.py           # Web UI
├── tests/
│   └── test_basic.py           # Basic tests
├── pyproject.toml              # Project configuration
└── .env                        # Environment variables
```

## API Endpoints

### Core Endpoints

#### Upload PDF
```
POST /rag/ingest/pdf
Content-Type: multipart/form-data

Body:
  file: <PDF file>

Response:
{
  "doc_id": "unique_document_id",
  "status": "success"
}
```

#### Ask Question / Generate Content
```
POST /agent
Content-Type: application/json

Body:
{
  "mode": "explain|summarize|flashcards|mcq",
  "input": "Your question",
  "doc_id": "document_id",
  "num_questions": 5  # For flashcards/mcq
}

Response:
{
  "message": "...",
  "sources": [...]  # Citations
}
```

#### Health Check
```
GET /health
```

#### Provider Management
```
GET /providers
POST /providers/switch
```

## Troubleshooting

### Issue: "GOOGLE_API_KEY is required"

**Solution**: Set your Google API key in `.env`:
```bash
export GOOGLE_API_KEY=your_key_here
```

### Issue: Ollama connection error

**Solution**: Ensure Ollama is running:
```bash
ollama serve
```

And verify the connection:
```bash
curl http://localhost:11434/api/tags
```


## Performance Tips

- **Chunk Size**: Larger chunks (1024) for long-form content, smaller (256) for precise answers
- **Top K Results**: Increase to 5-10 for broader context, decrease to 2-3 for precision
- **Model Selection**: 
  - **Fast**: Phi 2.7B, Gemma 7B
  - **Balanced**: Mistral 7B, Gemma3 4B
  - **Best Quality**: Mistral 12B, Gemini

## Development

### Running Tests

```bash
python -m pytest tests/
```

## Technologies Used

- **FastAPI**: Modern Python web framework
- **LangChain**: LLM orchestration and RAG
- **FAISS**: Vector similarity search
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **PDFPlumber**: PDF text extraction
- **Google Generative AI**: LLM and embedding APIs
- **Ollama**: Local LLM inference

**Happy Studying! 📚✨**
