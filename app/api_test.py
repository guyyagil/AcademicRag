import io
import pytest
from app.api.endpoint import api
from flask import Flask
from app.utils.pdf_processor import extract_text_from_pdf, chunk_text
from app.utils.embedding import get_embeddings, get_embedding
from app.database.chroma_client import get_chroma_client, add_embedding

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix='/api')
    app.config['TESTING'] = True
    return app.test_client()

def test_upload_papers_no_files(client):
    response = client.post('/api/papers', data={})
    assert response.status_code == 400
    assert b"No files part in the request" in response.data

def test_upload_papers_success(client, mocker):
    # Mock dependencies
    mocker.patch('app.api.endpoint.get_chroma_client')
    mocker.patch('app.api.endpoint.extract_text_from_pdf', return_value="some text")
    mocker.patch('app.api.endpoint.chunk_text', return_value=["chunk1"])
    mocker.patch('app.api.endpoint.get_embeddings', return_value=[[0.1, 0.2]])
    mocker.patch('app.api.endpoint.add_embedding', return_value="doc_id_1")

    data = {
        'files': (io.BytesIO(b"PDF content"), 'test.pdf')
    }
    response = client.post('/api/papers', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"success" in response.data