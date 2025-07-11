from rag.prompt_templates import build_prompt
from database.chroma_client import get_chroma_client, get_relevant_chunks_and_metadata
from utils.embedding import get_embedding
import requests
from flask import current_app
from typing import Optional

def run_rag_chain(question: str, target_files: Optional[list] = None) -> dict:
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
    # Keep originals for fallback
    orig_docs, orig_meta = documents, metadatas
    # If target_files are specified, filter accordingly
    if target_files:
        filtered = []
        # single-file filter or union for multiple
        for doc, meta in zip(orig_docs, orig_meta):
            name = meta.get('document_name') or meta.get('filename')
            if name in target_files:
                filtered.append((doc, meta))
        if filtered:
            documents, metadatas = zip(*filtered)
        else:
            documents, metadatas = [], []
        # fallback: if too few filtered chunks, revert to no filter
        min_chunks = current_app.config.get('MIN_FILE_CHUNKS', 1)
        if len(documents) < min_chunks:
            documents, metadatas = orig_docs, orig_meta
    
    # For multi-file queries, prepend hint to question
    if target_files and len(target_files) > 1:
        hint = f"Compare content from {', '.join(target_files)}. Use only these documents.\n"
        question = hint + question

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