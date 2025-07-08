import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def chunk_text_with_metadata(text, filename, chunk_size=1000, overlap=200):
    """
    Split text into overlapping chunks and attach metadata (filename, chunk index).
    Returns a list of dicts: {"text": ..., "metadata": {...}}
    """
    chunks = []
    start = 0
    chunk_id = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "document_name": filename,
                    "chunk_id": chunk_id
                }
            })
        start += chunk_size - overlap
        chunk_id += 1
    return chunks
