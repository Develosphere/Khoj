from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import source
from app.api.v1.endpoints import timeline

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(source.router, prefix="/investigations")
api_router.include_router(timeline.router, prefix="/investigations")
