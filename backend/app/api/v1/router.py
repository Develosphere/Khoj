from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import source
from app.api.v1.endpoints import summary
from app.api.v1.endpoints import timeline
from app.api.v1.endpoints import theory
from app.api.v1.endpoints import investigations
from app.api.v1.endpoints import case
from app.api.v1.endpoints import dashboard

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(source.router, prefix="/investigations")
api_router.include_router(timeline.router, prefix="/investigations")
api_router.include_router(theory.router, prefix="/investigations")
api_router.include_router(summary.router, prefix="/investigations")
api_router.include_router(investigations.router, prefix="/investigations")
api_router.include_router(case.router, prefix="/cases", tags=["cases"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
