# "schemas.py contains the Pydantic models used by the service."

from pydantic import BaseModel
from typing import List, Optional

# Schema for data input (CREATE)
# The RAG File Processing service will send this
class DataIngestionRequest(BaseModel):
    chunk_id: str
    original_chunk: str
    summary_chunk: str
    embedding: List[float]

# Schema for the response when creating (optional, but good practice)
class DataIngestionResponse(BaseModel):
    status: str
    stored_id: str

# Schema for the search request (READ)
# The RAG Retriever service will send this
class QueryRequest(BaseModel):
    query_embedding: List[float]
    k: int = 3  # Number of chunks to retrieve

# Schema for a single retrieved chunk
class RetrievedChunk(BaseModel):
    id: str
    original_chunk: str

# Schema for the search response
class QueryResponse(BaseModel):
    retrieved_chunks: List[RetrievedChunk]
