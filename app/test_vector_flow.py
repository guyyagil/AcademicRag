from utils.pdf_processor import extract_text_from_pdf, chunk_text
from utils.embedding import get_embeddings
from database.chroma_client import get_chroma_client, add_embedding, query_embeddings

PDF_PATH = "testing.pdf"
COLLECTION_NAME = "test_papers"

# 1. Extract and chunk text
text = extract_text_from_pdf(PDF_PATH)
chunks = chunk_text(text)

# 2. Generate embeddings
embeddings = get_embeddings(chunks)

# 3. Store embeddings in ChromaDB and validate storage
client = get_chroma_client()
doc_ids = []
for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
    metadata = {"chunk_id": i, "text": chunk[:50], "document_name": PDF_PATH}
    doc_id = add_embedding(client, COLLECTION_NAME, embedding, metadata)
    doc_ids.append(doc_id)
    # --- Validation step ---
    collection = client.get_or_create_collection(COLLECTION_NAME)
    result = collection.get(ids=[doc_id])
    stored_metadata = result['metadatas'][0] if result['metadatas'] else None
    assert stored_metadata == metadata, f"Metadata mismatch for ID {doc_id}: {stored_metadata} != {metadata}"
    print(f"✅ ID {doc_id} and metadata validated.")

print(f"Added and validated {len(doc_ids)} embeddings to ChromaDB.")

# 4. Query ChromaDB to validate retrieval
results = query_embeddings(client, COLLECTION_NAME, embeddings[0])
print("Query results:", results)