from flask import Blueprint, request, jsonify
from utils.pdf_processor import extract_text_from_pdf, chunk_text
from utils.embedding import get_embeddings, get_embedding
from database.chroma_client import get_chroma_client, add_embedding
from api.schemas import QueryInput, QueryResponse, UploadResponse
import os
import tempfile

api = Blueprint('api', __name__)

@api.route('/papers', methods=['POST'])
def upload_papers():
    """
    Upload one or more PDF files and store their embeddings.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: files
        type: file
        required: true
        description: PDF files to upload
    responses:
      200:
        description: Upload successful
        schema:
          type: object
          properties:
            status:
              type: string
            document_ids:
              type: array
              items:
                type: string
      400:
        description: Bad request
    """

    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    client = get_chroma_client()
    collection_name = "papers"
    doc_ids = []

    temp_dir = tempfile.gettempdir()  

    for file in files:
        filename = file.filename
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)

        text = extract_text_from_pdf(filepath)
        chunks = chunk_text(text)
        embeddings = get_embeddings(chunks)

        for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
            metadata = {"chunk_id": i, "text": chunk[:50], "document_name": filename}
            doc_id = add_embedding(client, collection_name, embedding, metadata)
            doc_ids.append(doc_id)

        os.remove(filepath)

    return jsonify({"status": "success", "document_ids": doc_ids}), 200

@api.route('/query', methods=['POST'])
def query_papers():
    """
    Query uploaded papers with natural language questions.
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
              description: The question to ask about the papers
              example: "What are the main findings?"
          required:
            - question
    responses:
      200:
        description: Query successful
        schema:
          type: object
          properties:
            question:
              type: string
            answer:
              type: string
            context:
              type: string
            citations:
              type: array
              items:
                type: object
      400:
        description: Bad request
    """
    data = request.get_json()
    validated = QueryInput(**data)  # Validate input
    question = validated.question
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # 1. Convert question to embedding
    question_embedding = get_embedding(question)

    # 2. Retrieve relevant chunks from ChromaDB
    client = get_chroma_client()
    collection_name = "papers"
    collection = client.get_or_create_collection(collection_name)
    results = collection.query(query_embeddings=[question_embedding], n_results=5)
    retrieved_chunks = [doc for doc in results["documents"][0]]

    # 3. (Optional) Format context for LLM
    context = "\n\n".join(retrieved_chunks)

    answer = "This is a placeholder. Implement LLM call here."

    response = QueryResponse(
        question=question,
        answer=answer,
        context=context,
        citations=results["metadatas"][0]
    )
    return jsonify(response.model_dump())  # Serialize output