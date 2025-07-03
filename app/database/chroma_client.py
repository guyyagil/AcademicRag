import chromadb
import uuid

def get_chroma_client(host="chromadb", port=8000):
    """Initialize and return a ChromaDB client."""
    client = chromadb.HttpClient(host=host, port=port)
    return client

def add_embedding(client, collection_name, embedding, metadata, doc_id=None):
    """Add an embedding with metadata to a collection."""
    collection = client.get_or_create_collection(collection_name)
    
    # Generate a unique ID if not provided
    if doc_id is None:
        doc_id = str(uuid.uuid4())
    
    collection.add(
        embeddings=[embedding], 
        metadatas=[metadata], 
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