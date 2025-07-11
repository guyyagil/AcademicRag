# 🧠 Academic RAG AI Agent - Development Checklist

## ✅ Phase 1: Project Setup

**Goal:** Establish foundational environment and architecture.

- [x] **Repository Initialization**
  - [x] Set up Git repo with README and `.gitignore`
  - [x] Define project goals and structure in the `README.md`

- [x] **Create Dockerized Environment**
  - [x] Write `docker-compose.yml` with services:
    - [x] `flask_app`
    - [x] `ollama`
    - [x] `chromadb`
    - [x] `mongodb`
    - [x] `mongo-express`
  - [x] Create `Dockerfile` for Flask app
  - [x] Add `.env` file for managing credentials and configs

- [x] **Define Python Project Structure**
  - [x] Create folders: `app/`, `modelfile/`, `utils/`, `database/`, `rag/`, `api/`
  - [x] Add placeholder `__init__.py` files

---

## ✅ Phase 2: Core Infrastructure

**Goal:** Build PDF processing and vector storage.

- [x] **PDF Upload and Processing**
  - [x] `pdf_processor.py`: Extract and chunk text from PDFs
  - [x] `embeddings.py`: Generate embeddings and store in ChromaDB with metadata

- [x] **Database Setup**
  - [x] `chroma_client.py`: Handle ChromaDB interactions
  - [x] `mongo_client.py`: Log queries in MongoDB

- [x] **Test Vector Flow**
  - [x] Test PDF → embeddings → ChromaDB
  - [x] Validate document ID and metadata storage

---

## ✅ Phase 3: API Development

**Goal:** Build endpoints and ensure request/response validation.

- [x] **Define API Endpoints**
  - [x] `POST /papers`: Upload PDFs
  - [x] `POST /query`: Ask natural language questions

- [x] **Pydantic Models**
  - [x] Input models: PDF upload, query input
  - [x] Output models: Answer text, citations

- [x] **Swagger UI**
  - [x] `swagger.py`: Define and serve API docs
  - [x] Confirm Swagger interface displays all endpoints

---

## ✅ Phase 4: RAG System

**Goal:** Implement context-aware Retrieval-Augmented Generation.

- [ ] **Prompt Engineering**
  - [ ] `prompt_templates.py`: Define system prompt for academic tone

- [ ] **RAG Chain Logic**
  - [ ] `chain.py`: Retrieve relevant chunks
  - [ ] Format and send to LLM with system prompt

- [ ] **Output Parsing**
  - [ ] `output_parser.py`: Extract clean answers
  - [ ] Attach citations and optional confidence

---

## ✅ Phase 5: Logging & Monitoring

**Goal:** Track system behavior and user queries.

- [x] **MongoDB Logging**
  - [x] `logging.py`: Log timestamp, query, answer, and metadata

- [x] **Mongo Express**
  - [x] Connect Mongo Express to view logs in browser

---

## ✅ Phase 6: Testing & Validation

**Goal:** Ensure robustness and quality.

- [ ] **Unit Tests**
  - [ ] `pdf_processor`, `embeddings`, `RAG`, and `output_parser`

- [ ] **Integration Tests**
  - [ ] End-to-end test: upload → embed → query → answer

- [ ] **Load Testing**
  - [ ] Test large PDFs and concurrent users

---

## ✅ Phase 7: Final Touches

**Goal:** Polish and document.

- [ ] **Security & Input Handling**
  - [ ] Sanitize PDF input
  - [ ] Add rate limiting if needed

- [ ] **Deployment Prep**
  - [ ] Build and tag Docker images
  - [ ] Add deployment commands/docs to README

- [ ] **Documentation**
  - [ ] Finalize `README.md` with:
    - [ ] Project goals and tech stack
    - [ ] Setup instructions
    - [ ] API usage examples
    - [ ] Swagger/OpenAPI link

---
