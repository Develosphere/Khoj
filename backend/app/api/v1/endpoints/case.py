from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security, _require_bearer_token, get_current_user
from app.core.config import settings
from supabase import create_client, Client, ClientOptions
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseDetailsResponse

router = APIRouter()

def get_user_db_client(creds: HTTPAuthorizationCredentials = Depends(security)) -> Client:
    """Dependency that returns a user-authenticated Supabase client.

    This client automatically carries the user's JWT, prompting Supabase
    to enforce RLS policies at the database level.
    """
    token = _require_bearer_token(creds)
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        options=ClientOptions(
            headers={"Authorization": f"Bearer {token}"}
        )
    )

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreate,
    current_user: Any = Depends(get_current_user),
    db: Client = Depends(get_user_db_client)
):
    """Create a new case/investigation owned by the current user."""
    # current_user has id field
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identity could not be verified."
        )

    payload = {
        "title": case_in.title,
        "description": case_in.description,
        "user_id": user_id,
        "status": "active"
    }

    try:
        res = db.table("cases").insert(payload).execute()
        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create case record."
            )
        return res.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during case creation: {str(e)}"
        )

@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    db: Client = Depends(get_user_db_client)
):
    """Retrieve all cases owned by the authenticated user."""
    try:
        res = db.table("cases").select("*").execute()
        return res.data or []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during listing: {str(e)}"
        )

@router.get("/{case_id}", response_model=CaseDetailsResponse)
async def get_case_details(
    case_id: str,
    db: Client = Depends(get_user_db_client)
):
    """Retrieve complete details for a specific case, including sources, evidence, timeline, and theories."""
    try:
        # 1. Fetch case metadata (RLS will check if user owns it)
        case_res = db.table("cases").select("*").eq("id", case_id).execute()
        if not case_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or access denied."
            )
        case_data = case_res.data[0]

        # 2. Fetch associated resources
        sources_res = db.table("sources").select("*").eq("case_id", case_id).execute()
        evidence_res = db.table("evidence").select("*").eq("case_id", case_id).execute()
        timeline_res = db.table("timeline_events").select("*").eq("case_id", case_id).execute()
        theories_res = db.table("theories").select("*").eq("case_id", case_id).execute()

        # 3. Assemble and return
        case_data["sources"] = sources_res.data or []
        case_data["evidence"] = evidence_res.data or []
        case_data["timeline_events"] = timeline_res.data or []
        case_data["theories"] = theories_res.data or []

        return case_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during details retrieval: {str(e)}"
        )

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_in: CaseUpdate,
    db: Client = Depends(get_user_db_client)
):
    """Update metadata fields of a specific case."""
    try:
        # Check if case exists and is owned by the user
        check_res = db.table("cases").select("id").eq("id", case_id).execute()
        if not check_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or access denied."
            )

        update_data = {}
        if case_in.title is not None:
            update_data["title"] = case_in.title
        if case_in.description is not None:
            update_data["description"] = case_in.description
        if case_in.status is not None:
            update_data["status"] = case_in.status
        
        # Only update if fields were provided
        if not update_data:
            return check_res.data[0]

        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        res = db.table("cases").update(update_data).eq("id", case_id).execute()
        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update case record."
            )
        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during update: {str(e)}"
        )

@router.delete("/{case_id}", status_code=status.HTTP_200_OK)
async def delete_case(
    case_id: str,
    db: Client = Depends(get_user_db_client)
):
    """Delete a specific case and all cascade-related resources (sources, evidence, timeline, etc.)."""
    try:
        # Check if case exists and is owned by the user
        check_res = db.table("cases").select("id").eq("id", case_id).execute()
        if not check_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or access denied."
            )

        db.table("cases").delete().eq("id", case_id).execute()
        return {"status": "success", "message": "Case and all associated resources deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during deletion: {str(e)}"
        )

@router.post("/{case_id}/analyze", response_model=CaseDetailsResponse)
async def analyze_case(
    case_id: str,
    db: Client = Depends(get_user_db_client)
):
    """Run the complete AI investigation analysis pipeline:

    1. Collect sources using case title.
    2. Store sources in database.
    3. Extract evidence claims using AI (Gemini).
    4. Store evidence in database.
    5. Generate timeline of events.
    6. Store timeline events in database.
    7. Generate competing theories using AI (Gemini).
    8. Store theories in database.
    9. Return full CaseDetailsResponse.
    """
    try:
        # 1. Fetch case details to get the title
        case_res = db.table("cases").select("*").eq("id", case_id).execute()
        if not case_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or access denied."
            )
        case_data = case_res.data[0]
        case_title = case_data["title"]

        # Clean existing analysis if repeating (cascade will handle child tables)
        db.table("sources").delete().eq("case_id", case_id).execute()

        # 2. Collect sources
        from app.services.source_collector import SourceCollector
        collector = SourceCollector()
        sources_schemas = await collector.collect_sources(case_title)
        
        # 3. Store sources
        sources_payload = []
        for src in sources_schemas:
            sources_payload.append({
                "case_id": case_id,
                "title": src.title,
                "url": src.url,
                "source_name": src.source_name,
                "published_at": src.published_at,
                "content": src.content
            })
        
        sources_list = []
        if sources_payload:
            sources_res = db.table("sources").insert(sources_payload).execute()
            sources_list = sources_res.data or []

        # 4. Extract evidence
        from app.services.evidence_engine import EvidenceEngine
        evidence_engine = EvidenceEngine()
        evidence_schemas = await evidence_engine.extract_evidence(sources_payload)

        # 5. Store evidence
        evidence_payload = []
        for ev in evidence_schemas:
            evidence_payload.append({
                "case_id": case_id,
                "claim": ev.claim,
                "source": ev.source,
                "confidence": ev.confidence,
                "evidence_type": ev.evidence_type,
                "reasoning": ev.reasoning
            })

        evidence_list = []
        if evidence_payload:
            evidence_res = db.table("evidence").insert(evidence_payload).execute()
            evidence_list = evidence_res.data or []

        # 6. Generate timeline
        from app.services.timeline_engine import TimelineEngine
        timeline_engine = TimelineEngine()
        timeline_schemas = await timeline_engine.extract_timeline_async(evidence_schemas)

        # 7. Store timeline
        timeline_payload = []
        for evt in timeline_schemas:
            timeline_payload.append({
                "case_id": case_id,
                "time": evt.time,
                "event": evt.event,
                "confidence": evt.confidence,
                "supporting_evidence": evt.supporting_evidence
            })

        timeline_list = []
        if timeline_payload:
            timeline_res = db.table("timeline_events").insert(timeline_payload).execute()
            timeline_list = timeline_res.data or []

        # 8. Generate theories
        from app.services.theory_engine import generate_theories
        theories_resp = await generate_theories(evidence_payload, timeline_payload)
        
        # 9. Store theories
        theories_list = []
        if theories_resp and theories_resp.theories:
            theories_payload = []
            for th in theories_resp.theories:
                theories_payload.append({
                    "case_id": case_id,
                    "theory": th.get("theory"),
                    "confidence": th.get("confidence"),
                    "supporting_evidence": th.get("supporting_evidence", []),
                    "timeline_events": th.get("timeline_events", []),
                    "summary": th.get("summary")
                })
            if theories_payload:
                theories_res = db.table("theories").insert(theories_payload).execute()
                theories_list = theories_res.data or []

        # Assemble and return result
        result = {
            **case_data,
            "sources": sources_list,
            "evidence": evidence_list,
            "timeline_events": timeline_list,
            "theories": theories_list
        }
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running investigation analysis pipeline: {str(e)}"
        )

from app.schemas.source import SourceSchema

@router.post("/{case_id}/sources", response_model=SourceSchema)
async def add_source_to_case(
    case_id: str,
    source_in: SourceSchema,
    db: Client = Depends(get_user_db_client)
):
    """Manually insert/link a scraped source to a specific case file."""
    try:
        # Check if case exists and is owned by the user
        check_res = db.table("cases").select("id").eq("id", case_id).execute()
        if not check_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or access denied."
            )

        payload = {
            "case_id": case_id,
            "title": source_in.title,
            "url": source_in.url,
            "source_name": source_in.source_name,
            "published_at": source_in.published_at,
            "content": source_in.content
        }

        res = db.table("sources").insert(payload).execute()
        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to insert source."
            )
        return SourceSchema(
            title=res.data[0].get("title"),
            url=res.data[0].get("url"),
            source_name=res.data[0].get("source_name"),
            published_at=res.data[0].get("published_at"),
            content=res.data[0].get("content")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during source insertion: {str(e)}"
        )
