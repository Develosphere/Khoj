from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime

class SimulationCreate(BaseModel):
    case_id: str = Field(..., description="ID of the case (UUID)")
    theory_id: Optional[str] = Field(None, description="ID of the associated theory (UUID)")
    instructions: Dict[str, Any] = Field(..., description="JSON layout of the 3D scene")

class SimulationResponse(BaseModel):
    id: str
    case_id: str
    theory_id: Optional[str]
    instructions: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
