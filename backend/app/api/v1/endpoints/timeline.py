from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.evidence import EvidenceSchema
from app.schemas.timeline import TimelineListResponse
from app.services.timeline_engine import TimelineEngine

router = APIRouter()


@router.post("/timeline/generate", response_model=TimelineListResponse)
async def generate_timeline(
    evidence: List[EvidenceSchema],
    user: Any = Depends(get_current_user),
):
    """Generate a timeline from a list of evidence objects.

    Requires Supabase-authenticated user.
    """
    try:
        engine = TimelineEngine()
        timeline = await engine.extract_timeline_async(evidence)
        return {"timeline": timeline}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
