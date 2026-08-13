from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.schemas.source import SourceSchema
from app.schemas.evidence import EvidenceSchema
from app.schemas.timeline import TimelineEventSchema
from app.schemas.theory import TheorySchema

class CaseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the investigation")
    description: Optional[str] = Field(None, description="Detailed context or notes")

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|archived)$")

class CaseResponse(CaseBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CaseDetailsResponse(CaseResponse):
    sources: List[SourceSchema] = []
    evidence: List[EvidenceSchema] = []
    timeline_events: List[TimelineEventSchema] = []
    theories: List[TheorySchema] = []

class DashboardStats(BaseModel):
    total_cases: int
    active_cases: int
    total_sources: int
    total_evidence: int
    total_theories: int
