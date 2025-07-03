# Academic RAG AI Agent

A Python-based RAG (Retrieval-Augmented Generation) system for academic document processing and question answering.

## Features

- PDF text extraction and chunking
- Document embedding generation using Ollama
- Vector storage with ChromaDB
- Query logging with MongoDB
- RESTful API with Flask

## Setup Instructions

### 1. Prerequisites
- Docker and Docker Compose
- Git

### 2. Clone and Setup
```bash
git clone <your-repo-url>
cd slava-project
```

### 3. Start Services
```bash
docker compose up --build
```

### 4. Pull the Base Model and Create Custom Model
```bash
# Pull the base Llama2 model
docker compose exec ollama ollama pull llama2

# Create your custom academic RAG model
docker compose exec ollama ollama create academic-rag -f /modelfile/Modelfile
```

### 5. Pull the Embedding Model
```bash
docker compose exec ollama ollama pull nomic-embed-text
```

### 6. Test the Vector Flow
```bash
# Place a PDF file named 'testing.pdf' in the app/ directory
docker compose exec flask_app python test_vector_flow.py
```

## API Endpoints

- **Flask App**: http://localhost:5000
- **Mongo Express**: http://localhost:8081
- **ChromaDB**: http://localhost:8000

## Project Structure

```
slava-project/
├── app/
│   ├── utils/
│   │   ├── pdf_processor.py
│   │   └── embedding.py
│   ├── database/
│   │   ├── chroma_client.py
│   │   └── mongo_client.py
│   ├── main.py
│   └── test_vector_flow.py
├── modelfile/
│   └── Modelfile
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Testing

The project includes a test script that validates the complete pipeline:
PDF → Text Extraction → Chunking → Embeddings → Vector Storage → Retrieval

Run the test with:
```bash
docker compose exec flask_app python test_vector_flow.py
```