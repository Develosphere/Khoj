from fastapi import APIRouter

from app.api.simulations import router as simulation_router
from app.api.v1.endpoints import auth, case, dashboard, source

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(source.router, prefix="/investigations")
api_router.include_router(case.router, prefix="/cases", tags=["cases"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(simulation_router, prefix="/simulation")
