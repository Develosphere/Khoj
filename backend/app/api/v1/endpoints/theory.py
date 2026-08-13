from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.theory import TheoryListResponse
from app.services.theory_engine import generate_theories
from app.core.security import get_current_user
from pydantic import BaseModel, Field
from typing import List, Any

router = APIRouter()

class TheoryGenerationRequest(BaseModel):
    evidence: List[Any] = Field(...)
    timeline: List[Any] = Field(...)

@router.post("/theories/generate", response_model=TheoryListResponse)
async def generate_theories_endpoint(
    req: TheoryGenerationRequest,
    user=Depends(get_current_user),
):
    """
    Generate at least 3 competing investigation theories from evidence + timeline.
    """
    result = await generate_theories(req.evidence, req.timeline)
    if not result.theories:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Theory generation failed or returned fewer than 3 valid theories."
        )
    return result
