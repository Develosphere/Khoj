from pydantic import BaseModel
from typing import Optional

class Source(BaseModel):
    title: str
    url: str
    source_name: str
    published_at: Optional[str]  # ISO format or None
    content: str
