import uuid
import chromadb
from chromadb import HttpClient

def get_chroma_client(host="chromadb", port=8000):
    """Initialize and return a ChromaDB client."""
    client = HttpClient(host=host, port=port)
    return client

def add_embedding(client, collection_name, embedding, metadata, document=None, doc_id=None):
    """Add an embedding with metadata and document text to a collection."""
    collection = client.get_or_create_collection(collection_name)
    
    # Generate a unique ID if not provided
    if doc_id is None:
        doc_id = str(uuid.uuid4())
    
    collection.add(
        embeddings=[embedding], 
        metadatas=[metadata], 
        documents=[document],  # include document text for retrieval
        ids=[doc_id]
    )
    return doc_id

def query_embeddings(client, collection_name, query_embedding, top_k=5):
    """Query for similar embeddings in a collection."""
    collection = client.get_or_create_collection(collection_name)
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=top_k
    )
    return results

def get_relevant_chunks(client, collection_name, query_embedding, top_k=5):
    """Retrieve relevant context chunks (text) based on a query embedding."""
    results = query_embeddings(client, collection_name, query_embedding, top_k)
    return results['documents'][0] if results.get('documents') else []

def get_relevant_chunks_and_metadata(client, collection_name, query_embedding, top_k=5):
    """Retrieve relevant context chunks and their metadata."""
    results = query_embeddings(client, collection_name, query_embedding, top_k)
    documents = results['documents'][0] if results.get('documents') else []
    metadatas = results['metadatas'][0] if results.get('metadatas') else []
    return documents, metadatas



