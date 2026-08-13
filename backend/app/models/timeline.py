from pydantic import BaseModel, Field
from typing import List

class TimelineEvent(BaseModel):
    """Domain model for a single timeline event."""
    time: str = Field(..., description="Timestamp or temporal marker of the event.")
    event: str = Field(..., description="Description of the event.")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1 inclusive.")
    supporting_evidence: List[str] = Field(..., description="List of evidence claim strings or IDs supporting this event.")

class Timeline(BaseModel):
    """Model for a full timeline composed of events."""
    events: List[TimelineEvent]
