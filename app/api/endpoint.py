from flask import Blueprint, request, jsonify
from utils.pdf_processor import extract_text_from_pdf, chunk_text_with_metadata
from utils.embedding import get_embeddings, get_embedding
from database.chroma_client import get_chroma_client, add_embedding,get_relevant_chunks_and_metadata
from api.schemas import QueryInput, QueryResponse, UploadResponse
from rag.output_parser import parse_llm_output
from rag.chain import run_rag_chain
import os
import tempfile
from pydantic import BaseModel, ValidationError, validator

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
        chunked = chunk_text_with_metadata(text, filename)
        embeddings = get_embeddings([c["text"] for c in chunked])

        for i, (embedding, chunk) in enumerate(zip(embeddings, chunked)):
            metadata = chunk["metadata"]
            doc_id = add_embedding(client, collection_name, embedding, metadata, document=chunk["text"])
            doc_ids.append(doc_id)

        os.remove(filepath)

    return jsonify({"status": "success", "document_ids": doc_ids}), 200

def get_uploaded_pdf_filenames():
    temp_dir = tempfile.gettempdir()
    return {f for f in os.listdir(temp_dir) if f.lower().endswith('.pdf')}

class QueryInputWithPDF(QueryInput):
    @validator('question')
    def must_mention_existing_pdf(cls, v):
        from database.chroma_client import get_chroma_client
        client = get_chroma_client()
        # Load all stored filenames from Chroma metadata
        try:
            collection = client.get_collection("papers")
            metadatas = collection.get(include=["metadatas"])["metadatas"]
            filenames = {meta.get("filename") or meta.get("document_name") for meta in metadatas if meta}
        except Exception:
            filenames = set()
        # Check question text against each stored file name or its base
        q_lower = v.lower()
        for full in filenames:
            if not full:
                continue
            name_lower = full.lower()
            base = name_lower[:-4] if name_lower.endswith('.pdf') else name_lower
            # match either full name or base name substring
            if base in q_lower or name_lower in q_lower:
                return v
        raise ValueError(f"No referenced file found in Chroma DB among: {', '.join(filenames)}")

@api.route('/query', methods=['POST'])
def query_papers():
    """
    Query the RAG system with a question.
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
              example: "What are the main findings of the paper?"
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
                type: string
      400:
        description: Bad request
    """
    data = request.get_json()
    try:
        validated = QueryInputWithPDF(**data)
    except ValidationError as e:
        # Serialize error messages only
        messages = [err.get("msg") for err in e.errors()]
        return jsonify({"error": messages}), 400
    question = validated.question
    if not question:
        return jsonify({"error": "No question provided"}), 400
    # Determine target file name for context filtering
    client = get_chroma_client()
    collection_name = "papers"
    try:
        collection = client.get_collection(collection_name)
        metadatas = collection.get(include=["metadatas"])["metadatas"]
        filenames = [meta.get("filename") or meta.get("document_name") for meta in metadatas if meta]
    except Exception:
        filenames = []
    q_lower = question.lower()
    target_file = None
    for full in filenames:
        if not full:
            continue
        name_lower = full.lower()
        base = name_lower[:-4] if name_lower.endswith('.pdf') else name_lower
        if name_lower in q_lower or base in q_lower:
            target_file = full
            break

    rag_result = run_rag_chain(question, target_file)
    answer = rag_result["llm_output"]
    context = rag_result["context"]
    parsed = parse_llm_output(answer)
    response = QueryResponse(
        question=question,
        answer=parsed["answer"],
        context=context,
        citations=parsed["citations"],
        filename=target_file
    )
    
    return jsonify(response.model_dump())