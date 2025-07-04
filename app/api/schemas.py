from pydantic import BaseModel
from typing import List, Optional

class QueryInput(BaseModel):
    question: str

class UploadResponse(BaseModel) :
    status: str
    document_ids: List[str]

class QueryResponse(BaseModel):
    question: str
    answer: str
    context: str
    citations: Optional[list]
