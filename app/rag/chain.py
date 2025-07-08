from rag.prompt_templates import build_prompt
from database.chroma_client import get_chroma_client, get_relevant_chunks_and_metadata
from utils.embedding import get_embedding
import requests
from flask import current_app

def run_rag_chain(question: str) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant context chunks from ChromaDB.
    2. Build the prompt for the LLM.
    3. Query the LLM (Ollama) for an answer.
    4. Return the raw LLM response and context.
    """
    # 1. Get ChromaDB client and collection name
    client = get_chroma_client()
    collection_name = "papers"  # or use your config if dynamic

    # 2. Get embedding for the question
    query_embedding = get_embedding(question)

    # 3. Retrieve relevant chunks
    top_k = current_app.config.get("DEFAULT_TOP_K", 5)
    documents, metadatas = get_relevant_chunks_and_metadata(client, collection_name, query_embedding, top_k=top_k)
    # Build context entries with metadata labels for accurate citations
    context_entries = []
    for doc, meta in zip(documents, metadatas):
        if isinstance(doc, str) and doc.strip():
            label = f"[Document: {meta.get('document_name')}, Chunk: {meta.get('chunk_id')}]"
            context_entries.append(f"{label}\n{doc}")
    context = "\n\n".join(context_entries)

    # 4. Build prompt
    prompt = build_prompt(context=context, question=question)

    # 5. Query Ollama LLM
    ollama_url = current_app.config["OLLAMA_BASE_URL"] + "/api/generate"
    ollama_model = current_app.config["OLLAMA_MODEL"]
    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(ollama_url, json=payload)
    response.raise_for_status()
    llm_output = response.json().get("response", "")

    # 6. Return for further parsing
    return {
        "llm_output": llm_output,
        "context": context
    }