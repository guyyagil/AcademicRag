import requests

def get_embedding(text, api_url="http://ollama:11434/api/embeddings", model="nomic-embed-text"):
    """
    Get embedding for a single text chunk from Ollama or another embedding service.
    """
    payload = {
        "model": model,
        "prompt": text
    }
    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("embedding")

def get_embeddings(chunks, api_url="http://ollama:11434/api/embeddings", model="nomic-embed-text"):
    """
    Get embeddings for a list of text chunks.
    """
    return [get_embedding(chunk, api_url, model) for chunk in chunks]
