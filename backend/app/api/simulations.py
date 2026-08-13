from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from supabase import Client

from app.api.v1.endpoints.case import get_user_db_client
from app.schemas.simulation import GenerateSimulationRequest, SimulationScreenplay
from app.services.reconstruction_engine import ReconstructionError, generate_reconstruction

router = APIRouter(tags=["simulation"])


@router.post("/generate", response_model=SimulationScreenplay, status_code=status.HTTP_201_CREATED)
async def generate_simulation(
    request: GenerateSimulationRequest,
    db: Client = Depends(get_user_db_client),
):
    try:
        screenplay = await generate_reconstruction(request.context)
        payload = screenplay.model_dump(mode="json")
        result = db.table("simulations").insert({
            "case_id": request.investigation_id,
            "theory_id": request.selected_theory_id,
            "instructions": payload,
        }).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Unable to persist reconstruction.")
        simulation_id = str(result.data[0]["id"])
        screenplay.id = simulation_id
        db.table("simulations").update({"instructions": screenplay.model_dump(mode="json")}).eq("id", simulation_id).execute()
        return screenplay
    except HTTPException:
        raise
    except ReconstructionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Reconstruction generation failed.") from exc


@router.get("/{simulation_id}", response_model=SimulationScreenplay)
async def get_simulation(
    simulation_id: str,
    db: Client = Depends(get_user_db_client),
):
    try:
        result = db.table("simulations").select("id,instructions").eq("id", simulation_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Simulation not found.")
        screenplay = SimulationScreenplay.model_validate(result.data[0]["instructions"])
        screenplay.id = str(result.data[0]["id"])
        return screenplay
    except HTTPException:
        raise
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail="Stored simulation has an invalid screenplay schema.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to load simulation.") from exc
