from pydantic import BaseModel, Field
from typing import List

class TheorySchema(BaseModel):
    theory: str = Field(...)
    confidence: float = Field(..., ge=0, le=1)
    supporting_evidence: List[str] = Field(default_factory=list)
    timeline_events: List[str] = Field(default_factory=list)
    summary: str = Field(...)

class TheoryListResponse(BaseModel):
    theories: List[TheorySchema]
