from pydantic import BaseModel, Field
from typing import List, Optional

class Theory(BaseModel):
    theory: str = Field(..., description="Hypothesis explaining the evidence/timeline")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    supporting_evidence: List[str] = Field(default_factory=list, description="IDs of supporting evidence claims")
    timeline_events: List[str] = Field(default_factory=list, description="IDs of supporting timeline events")
    summary: str = Field(..., description="Short summary/justification for the theory")
