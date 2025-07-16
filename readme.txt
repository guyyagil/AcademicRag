FINAL project RAG System

AcademicRag is a Retrieval-Augmented Generation (RAG) system for academic papers. 
Upload PDFs, get intelligent AI responses based on document content using embeddings and vector search.

Built with Flask, MongoDB, ChromaDB, and Ollama for local LLM inference.
Containerized with Docker for easy deployment and cross-platform compatibility.

Key features:
- PDF upload and text extraction
- Document chunking and embedding generation  
- Vector similarity search with ChromaDB
- Local AI chat using Ollama models
- RESTful API with Swagger documentation
- Query logging and analytics

Run with: docker-compose up --build
Access API: http://localhost:5000/swagger 