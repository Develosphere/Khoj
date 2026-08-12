from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.api.v1.endpoints.case import get_user_db_client
from app.schemas.case import DashboardStats

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Client = Depends(get_user_db_client)
):
    """Retrieve overall statistics for the current user's investigations dashboard.

    Calculates exact counts for cases, active cases, sources, evidence,
    and theories, filtered by database Row Level Security.
    """
    try:
        # Fetch counts using exact count queries (which only fetches counts, not full data payloads)
        cases_res = db.table("cases").select("id", count="exact").execute()
        total_cases = cases_res.count if cases_res.count is not None else len(cases_res.data or [])

        active_res = db.table("cases").select("id", count="exact").eq("status", "active").execute()
        active_cases = active_res.count if active_res.count is not None else len(active_res.data or [])

        sources_res = db.table("sources").select("id", count="exact").execute()
        total_sources = sources_res.count if sources_res.count is not None else len(sources_res.data or [])

        evidence_res = db.table("evidence").select("id", count="exact").execute()
        total_evidence = evidence_res.count if evidence_res.count is not None else len(evidence_res.data or [])

        theories_res = db.table("theories").select("id", count="exact").execute()
        total_theories = theories_res.count if theories_res.count is not None else len(theories_res.data or [])

        return DashboardStats(
            total_cases=total_cases,
            active_cases=active_cases,
            total_sources=total_sources,
            total_evidence=total_evidence,
            total_theories=total_theories
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during gathering statistics: {str(e)}"
        )
