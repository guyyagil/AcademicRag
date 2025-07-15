# AcademicRag

## Overview
AcademicRag is a Dockerized Retrieval-Augmented Generation (RAG) system.  
It combines:
- A custom LLM served by Ollama (built from a Modelfile)  
- Chroma for document embeddings  
- MongoDB for logging queries  
- A Flask REST API for interaction  

## Features
- Query the LLM with context from your documents  
- Automatic citation extraction (`[Document: ..., Section: ...]`)  
- Persistent query logs with timestamp filters  
- Fully containerized with Docker Compose  

## Directory Structure
```
slava project/
├─ app/                  # Flask application
│  ├─ api/               # REST endpoints (e.g. /logs)
│  └─ rag/               # LLM output parser
├─ modelfile/
│  └─ Modelfile          # Ollama model definition
├─ docker-compose.yml    # Multi-container setup
├─ Dockerfile            # Flask service build
├─ requirements.txt      # Python deps
└─ .gitignore            # Ignored files/folders
```

## Prerequisites
- Docker & Docker Compose  
- Docker Hub account (optional, for pushing images)  

## Getting Started

1. Clone the repo  
   ```sh
   git clone https://github.com/<your-username>/AcademicRag.git
   cd "slava project"
   ```

2. Configure environment  
   Copy `.env.example` to `.env` and set:
   ```
   MONGO_DB_NAME=academic_rag
   LOGS_COLLECTION=query_logs
   ```

3. Build & run containers  
   ```sh
   docker-compose up --build -d
   ```

4. Access services  
   - Flask API:  http://localhost:5000  
   - Mongo-Express: http://localhost:8081  
   - Ollama LLM: use `ollama` CLI on host or container port `11434`  
   - Chroma HTTP API: http://localhost:8000  

## API Usage

- POST `/ask`  
  ```json
  { "query": "Your question here" }
  ```
  Response:
  ```json
  {
    "answer": "Generated answer…",
    "citations": ["[Document: file.pdf, Section: …]"]
  }
  ```

- GET `/logs?start_time=2025-07-01T00:00:00&end_time=2025-07-15T23:59:59`  
  Returns filtered query logs.

## Managing Data

- To clear MongoDB data, stop services and delete the volume folder:
  ```powershell
  docker-compose down
  Remove-Item -Recurse -Force mongo_data
  docker-compose up -d
  ```
- Similarly remove `chroma_data/` or `ollama_data/` to reset embeddings or models.

## Customizing the Model

Edit `modelfile/Modelfile`:
```plain
FROM llama2
PARAMETER temperature 0.25
```
Rebuild Ollama image:
```sh
docker exec -it ollama ollama create my-model -f /modelfile/Modelfile
```

## Pushing Images to Docker Hub

1. Build & tag:
   ```sh
   docker-compose build
   docker tag flask_app:latest guyyagil/flask_app:latest
   docker commit ollama guyyagil/ollama-custom:latest
   ```
2. Push:
   ```sh
   docker login
   docker push guyyagil/flask_app:latest
   docker push guyyagil/ollama-custom:latest
   ```

## Contributing
1. Fork the repo  
2. Create a feature branch  
3. Submit a pull request  

## License
This project is licensed under the MIT