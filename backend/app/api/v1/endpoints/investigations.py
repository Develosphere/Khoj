from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.services.investigation_orchestrator import InvestigationOrchestrator

router = APIRouter()


class InvestigationRunRequest(BaseModel):
    case_name: str = Field(..., description="Name of the case to investigate.")


class InvestigationResult(BaseModel):
    case_name: str
    sources: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    theories: List[Dict[str, Any]]
    summary: Dict[str, Any]


def _get_user_id(user: Any) -> str | None:
    if isinstance(user, dict):
        return user.get("id")
    return getattr(user, "id", None)


@router.post("/run", response_model=InvestigationResult)
async def run_investigation_endpoint(
    payload: InvestigationRunRequest,
    user: Any = Depends(get_current_user),
):
    """Run the full investigation pipeline for a case name.

    Requires Supabase-authenticated user.
    """
    orchestrator = InvestigationOrchestrator()
    user_id = _get_user_id(user)
    result = await orchestrator.run_investigation(payload.case_name, user_id=user_id)
    return InvestigationResult(**result)
