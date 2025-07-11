from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from collections import OrderedDict
from utils.pdf_processor import extract_text_from_pdf, chunk_text_with_metadata
from utils.embedding import get_embeddings
from database.chroma_client import get_chroma_client, add_embedding
from api.schemas import QueryInput
from rag.output_parser import parse_llm_output
from rag.chain import run_rag_chain
from pydantic import ValidationError, validator
from database.mongo_client import get_mongo_client, log_query, get_logs
from datetime import datetime
import os
import tempfile

api = Blueprint('api', __name__)

@api.route('/papers', methods=['POST'])
@swag_from({
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'in': 'formData',
            'name': 'files',
            'type': 'file',
            'required': True,
            'description': 'PDF files to upload'
        }
    ],
    'responses': {
        200: {'description': 'Documents uploaded successfully'},
        400: {'description': 'Invalid request'}
    }
})
def upload_papers():
    """Upload one or more PDF files and store their embeddings."""
    if 'files' not in request.files:
        return jsonify({"success": "false", "error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"success": "false", "error": "No files uploaded"}), 400

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

        for embedding, chunk in zip(embeddings, chunked):
            metadata = chunk["metadata"]
            doc_id = add_embedding(client, collection_name, embedding, metadata, document=chunk["text"])
            doc_ids.append(doc_id)

        os.remove(filepath)

    return jsonify({"success": "true", "document_ids": doc_ids}), 200

class QueryInputWithPDF(QueryInput):
    @validator('question')
    def must_mention_existing_pdf(cls, v):
        client = get_chroma_client()
        try:
            collection = client.get_collection("papers")
            metadatas = collection.get(include=["metadatas"])["metadatas"]
            filenames = {meta.get("filename") or meta.get("document_name") for meta in metadatas if meta}
        except Exception:
            filenames = set()

        q_lower = v.lower()
        for full in filenames:
            if not full:
                continue
            name_lower = full.lower()
            base = name_lower[:-4] if name_lower.endswith('.pdf') else name_lower
            if base in q_lower or name_lower in q_lower:
                return v
        raise ValueError(f"No referenced file found in Chroma DB among: {', '.join(filenames)}")

def api_response(success: bool, msg: str, data=None, status_code: int = 200):
    payload = OrderedDict(success=success, msg=msg, data=data)
    return jsonify(payload), status_code

@api.route('/query', methods=['POST'])
@swag_from({
    'consumes': ['application/json'],
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {
                        'type': 'string',
                        'example': 'what are the main findings in the uploaded papers?'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Query completed successfully'},
        400: {'description': 'Validation failed or question not found in uploaded files'}
    }
})
def query_papers():
    start_time = datetime.utcnow()
    data = request.get_json()
    try:
        validated = QueryInputWithPDF(**data)
    except ValidationError as e:
        messages = [err.get("msg") for err in e.errors()]
        return api_response(False, "; ".join(messages), None, 400)

    question = validated.question
    client = get_chroma_client()
    try:
        collection = client.get_collection("papers")
        metadatas = collection.get(include=["metadatas"])["metadatas"]
        stored = [meta.get("filename") or meta.get("document_name") for meta in metadatas if meta]
    except Exception:
        stored = []

    q_lower = question.lower()
    matches = []
    for full in stored:
        if not full:
            continue
        name_lower = full.lower()
        base = name_lower[:-4] if name_lower.endswith('.pdf') else name_lower
        if name_lower in q_lower or base in q_lower:
            matches.append(full)

    target_files = list(dict.fromkeys(matches))
    # Execute RAG chain
    rag_result = run_rag_chain(question, target_files)
    # Extract answer and full context
    parsed = parse_llm_output(rag_result["llm_output"])
    # For logging, capture only chunk labels (e.g. [Document: x, Chunk: y])
    raw_context = rag_result.get("context", "")
    chunk_labels = []
    if raw_context:
        entries = raw_context.split("\n\n")
        for entry in entries:
            label = entry.splitlines()[0] if entry else None
            if label:
                chunk_labels.append(label)
    duration = (datetime.utcnow() - start_time).total_seconds()

    try:
        mongo_client = get_mongo_client()
        db = mongo_client[current_app.config.get('MONGO_DB_NAME', 'academic_rag')]
        log_query(db, current_app.config.get('LOGS_COLLECTION', 'query_logs'), {
            'timestamp': datetime.utcnow(),
            'question': question,
            # only store labels of retrieved chunks
            'retrieved_chunks': chunk_labels,
            'answer': parsed.get('answer'),
            'citations': parsed.get('citations', []),
            'metadata': None,
            'performance': {'duration_seconds': duration}
        })
    except Exception:
        # silence logging errors
        pass

    return api_response(True, "Query successful", {"filename": target_files, "answer": parsed["answer"]}, 200)

@api.route('/logs', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'in': 'query', 'name': 'start_time', 'type': 'string', 'format': 'date-time',
            'required': False, 'description': 'ISO timestamp to filter logs on or after this time'
        },
        {
            'in': 'query', 'name': 'end_time', 'type': 'string', 'format': 'date-time',
            'required': False, 'description': 'ISO timestamp to filter logs on or before this time'
        }
    ],
    'responses': {
        200: {'description': 'Query logs retrieved'},
        400: {'description': 'Invalid date format or bad request'}
    }
})
def get_query_logs():
    start = request.args.get('start_time')
    end = request.args.get('end_time')
    filter_query = {}
    try:
        if start:
            filter_query.setdefault('timestamp', {})['$gte'] = datetime.fromisoformat(start)
        if end:
            filter_query.setdefault('timestamp', {})['$lte'] = datetime.fromisoformat(end)
    except ValueError:
        return api_response(False, 'Invalid date format, use ISO format', None, 400)

    client = get_mongo_client()
    db = client[current_app.config.get('MONGO_DB_NAME', 'academic_rag')]
    logs = get_logs(db, current_app.config.get('LOGS_COLLECTION', 'query_logs'), filter_query)

    safe_logs = []
    for entry in logs:
        if '_id' in entry:
            entry['_id'] = str(entry['_id'])
        if 'timestamp' in entry and isinstance(entry['timestamp'], datetime):
            entry['timestamp'] = entry['timestamp'].isoformat()
        safe_logs.append(entry)

    return api_response(True, 'Logs retrieved', {'logs': safe_logs}, 200)
