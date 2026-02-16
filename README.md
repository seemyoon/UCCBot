# Ukrainian Criminal Code AI Assistant 🇺🇦

An intelligent legal assistant powered by RAG (Retrieval-Augmented Generation) technology for the Criminal Code of Ukraine. This application helps users quickly find and understand relevant legal articles through natural language queries.

![Demo](https://drive.google.com/file/d/1mqSSM6ROe2o57IbLpKAtE-HaBnuz4QOY/view?usp=sharing)

## Features

- **Natural Language Queries**: Ask questions in Ukrainian about the Criminal Code
- **Real-time Streaming**: AI responses stream in real-time for better UX
- **Context-Aware**: Maintains conversation history for follow-up questions
- **Vector Search**: Semantic search through legal documents using embeddings
- **Professional UI**: Clean, Ukrainian-themed interface with blue and yellow accents

## Project Structure
```
UCCBot/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── rag/
│       ├── rag_pipeline.py     # RAG implementation
│       └── context_builder.py  # Context assembly logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── App.css            # Ukrainian-themed styles
│   │   └── index.js           # React entry point
│   └── public/
│       └── index.html
├── ml/
│   ├── ingestion_pipeline.py  # Document processing pipeline
│   ├── preprocessing/
│   │   ├── text_normalizer.py
│   │   ├── text_processor.py
│   │   └── legal_text_patterns.py
│   └── data/
│       └── criminal_code_of_ukraine.pdf
├── schemas/
│   ├── query_request.py
│   ├── query_response.py
│   └── session_response.py
├── chroma_db/                  # Vector database storage
├── config.py                   # Configuration
├── vector_db.py                # Vector DB wrapper
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing LLM applications
- **OpenAI GPT-5-mini**: Language model for generating responses
- **ChromaDB**: Vector database for semantic search
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI library
- **Axios**: HTTP client
- **Lucide React**: Icon library
- **CSS3**: Custom Ukrainian-themed styling

### Machine Learning
- **OpenAI Embeddings** (text-embedding-3-small): Text vectorization
- **PyPDF**: PDF text extraction
- **LangChain Text Splitters**: Document chunking

### Database
- **ChromaDB**: Open-source vector database
  - Storage: SQLite + HNSW index
  - Embeddings
  - Persistence: Local file system

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API Key

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/seemyoon/UCCBot.git
cd UCCBot
```

2. **Set up environment variables**
```bash
# Create .env file in root directory
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

3. **Run with Docker Compose**
```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

4. **Run the backend**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm start
```

The frontend will open at http://localhost:3000

## Data Ingestion Pipeline

The ingestion pipeline processes the Criminal Code of Ukraine PDF and stores it in the vector database.

### Process Overview

1. **PDF Extraction**: Extract raw text from PDF using PyPDF
2. **Text Normalization**: Clean and normalize Ukrainian text
3. **Structure Detection**: Identify articles, sections, and parts using regex patterns
4. **Text Chunking**: Split long articles into manageable chunks (max 1000 tokens)
5. **Embedding Generation**: Create vector embeddings using OpenAI
6. **Database Storage**: Store chunks with metadata in ChromaDB

### Running Ingestion
```bash
cd ml
python ingestion_pipeline.py
```

### Ingestion Features

- **Hierarchical Structure**: Preserves legal document hierarchy (Parts → Sections → Articles)
- **Metadata Enrichment**: Each chunk includes:
  - `part`: Major division (e.g., "ЗАГАЛЬНА ЧАСТИНА")
  - `section`: Section number (e.g., "Розділ VI")
  - `article_num`: Article number (e.g., "185")
  - `chunk_index`: Position in multi-chunk articles
  - `total_chunks`: Total chunks for the article
  - `law_name`: "Кримінальний кодекс України"
  - `source_file`: Original PDF filename

- **Smart Chunking**: 
  - Articles split at natural boundaries
  - Maintains context across chunks

- **Pattern Recognition**:
  - Handles article variations: "Стаття 96-3", "Стаття 150 - 1"
  - Preserves notes and amendments
  - Captures revision information

### Database Schema
```python
{
    "id": "uuid",
    "vector": [1536-dimensional embedding],
    "metadata": {
        "part": "ОСОБЛИВА ЧАСТИНА",
        "section": "Розділ VI",
        "article_num": "185",
        "chunk_index": 0,
        "total_chunks": 3,
        "law_name": "Кримінальний кодекс України",
        "source_file": "criminal_code_of_ukraine.pdf"
    },
    "page_content": "Стаття 185. Крадіжка..."
}
```

## How It Works

### RAG Pipeline

1. **User Query**: User asks a question in Ukrainian
2. **Vector Search**: Query is embedded and similar chunks are retrieved from ChromaDB
3. **Context Building**: Retrieved chunks are assembled with complete article context
4. **LLM Generation**: GPT-4o-mini generates a response using the context
5. **Streaming Response**: Answer streams back to the user in real-time

### Context Assembly

The system intelligently assembles context:
- For multi-chunk articles: retrieves all chunks and combines them
- For sections: includes neighboring chunks for better context
- Maintains proper order using `chunk_index`

## Configuration

Edit `config.py` to customize:
```python
# OpenAI Configuration
import os

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MODEL = "text-embedding-3-small"

# Vector DB
PERSIST_DIR = './chroma_db'
COLLECTION_NAME = 'ucc_collection'

# RAG Parameters
NUMBER_OF_RESULTS_TO_RETURN = 5
MAX_CHUNKS_TOKENS = 1000
CHUNK_OVERLAP = 50

# Document
LAW_NAME = "Кримінальний кодекс України"
```

## API Endpoints

### POST `/query`
Query the assistant (non-streaming)

**Request:**
```json
{
  "query": "Що таке крадіжка?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Крадіжка - це таємне викрадення чужого майна...",
  "session_id": "uuid"
}
```

### POST `/query/stream`
Query with streaming response

### POST `/session/new`
Create a new conversation session

### POST `/session/{session_id}/clear`
Clear conversation history

### GET `/health`
Health check endpoint

## UI Features

- **Ukrainian Color Theme**: Blue (#005BBB) and Yellow (#FFD700)
- **Responsive Design**: Works on desktop and mobile
- **Real-time Streaming**: See AI responses as they're generated
- **Conversation History**: Maintains context across questions
- **Thinking Indicator**: Shows "..." while processing
- **Error Handling**: Graceful error messages

## Example Queries
```
"Що таке крадіжка?"
"Яке покарання за шахрайство?"
"Розкажи про статтю 185"
"Чим відрізняється крадіжка від грабежу?"
"Які є обставини що пом'якшують покарання?"
```

## Docker Commands
```bash
# Start services
docker compose up

# Build and start
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f
docker compose logs backend
docker compose logs frontend

# Stop services
docker compose down

# Rebuild specific service
docker compose build backend
docker compose restart backend
```

## 🛠️ Development

### Backend Development
```bash
# With auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

```

### Frontend Development
```bash
cd frontend
npm start
```

### Development with Docker
```bash
# Use development compose file with hot reload
docker compose -f docker-compose.dev.yml up
```

## Performance

- **Response Time**: ~2-5 seconds for typical queries
- **Streaming Latency**: First token in ~500ms
- **Vector Search**: <100ms for similarity search
- **Database Size**: ~50MB for complete Criminal Code
- **Memory Usage**: ~500MB (backend) + ~100MB (frontend)

## Security Notes

- API keys stored in `.env` file (never commit to git)
- CORS configured for localhost only
- No authentication (add for production)
- Rate limiting recommended for production
