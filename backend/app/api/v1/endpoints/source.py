from fastapi import APIRouter, Query
from app.services.source_collector import SourceCollector
from app.schemas.source import SourceListResponse

router = APIRouter()

@router.get("/sources", response_model=SourceListResponse)
async def get_sources(case_name: str = Query(..., description="Name of the case to search sources for")):
    collector = SourceCollector()
    sources = await collector.collect_sources(case_name)
    return SourceListResponse(sources=sources)
