from pydantic import BaseModel, Field
from typing import List

class TimelineEventSchema(BaseModel):
    id: str | None = None
    time: str = Field(..., description="Timestamp or temporal marker of the event.")
    event: str = Field(..., description="Description of the event.")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1 inclusive.")
    supporting_evidence: List[str] = Field(..., description="List of evidence claim strings or IDs supporting this event.")

class TimelineListResponse(BaseModel):
    timeline: List[TimelineEventSchema]
