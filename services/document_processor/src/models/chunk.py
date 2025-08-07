from pydantic import BaseModel
from typing import Literal, Dict, Any

class DocumentChunkOut(BaseModel):
    content: str
    type: Literal["text", "table", "image"]
    source_page: int
    metadata: Dict[str, Any]