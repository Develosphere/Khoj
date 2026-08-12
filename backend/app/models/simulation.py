from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime

class Simulation(BaseModel):
    """Domain model for a 3D reconstruction simulation."""

    id: Optional[str] = Field(None, description="Unique simulation ID (UUID)")
    case_id: str = Field(..., description="Associated case ID (UUID)")
    theory_id: Optional[str] = Field(None, description="Associated theory ID if linked to a theory (UUID)")
    instructions: Dict[str, Any] = Field(default_factory=dict, description="JSON instructions for the 3D visual reconstruction")
    created_at: Optional[datetime] = None
