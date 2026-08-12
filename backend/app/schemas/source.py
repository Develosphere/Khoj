from pydantic import BaseModel
from typing import Optional

class SourceSchema(BaseModel):
    title: str
    url: str
    source_name: str
    published_at: Optional[str]  # ISO format or None
    content: str

class SourceListResponse(BaseModel):
    sources: list[SourceSchema]
