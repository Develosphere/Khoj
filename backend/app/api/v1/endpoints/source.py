from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.services.source_collector import SourceCollector
from app.schemas.source import SourceListResponse

router = APIRouter()


@router.get("/sources", response_model=SourceListResponse)
async def get_sources(
    case_name: str = Query(..., description="Name of the case to search sources for"),
    user=Depends(get_current_user),
):
    collector = SourceCollector()
    sources = await collector.collect_sources(case_name)
    return SourceListResponse(sources=sources)
