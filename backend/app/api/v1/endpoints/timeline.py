from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.evidence import EvidenceSchema
from app.schemas.timeline import TimelineListResponse, TimelineEventSchema
from app.services.timeline_engine import TimelineEngine

router = APIRouter()
engine = TimelineEngine()

@router.post("/timeline/generate", response_model=TimelineListResponse)
def generate_timeline(evidence: List[EvidenceSchema]):
    """
    Generate a timeline from a list of evidence objects.
    """
    try:
        timeline = engine.extract_timeline(evidence)
        return {"timeline": timeline}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
