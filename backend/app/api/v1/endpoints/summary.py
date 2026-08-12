from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.schemas.summary import SummarySchema
from app.services.summary_engine import generate_summary

router = APIRouter()


class SummaryGenerationRequest(BaseModel):
    evidence: List[Any] = Field(..., description="List of evidence objects.")
    timeline: List[Any] = Field(..., description="List of timeline events.")
    theories: List[Any] = Field(..., description="List of theory objects.")


@router.post("/summary/generate", response_model=SummarySchema)
async def generate_summary_endpoint(
    req: SummaryGenerationRequest,
    user: Any = Depends(get_current_user),
):
    """Generate an investigation summary from evidence, timeline, and theories.

    Requires Supabase-authenticated user.
    """
    result = await generate_summary(req.evidence, req.timeline, req.theories)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Summary generation failed or produced invalid output.",
        )
    return result
