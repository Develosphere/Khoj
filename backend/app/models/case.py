from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Case(BaseModel):
    """Domain model for a case/investigation.

    Represents a case containing metadata, sources, evidence, and theories.
    """

    id: Optional[str] = Field(None, description="Unique case ID (UUID)")
    user_id: Optional[str] = Field(None, description="Owner user ID (auth.users UUID)")
    title: str = Field(..., description="Title of the case/investigation.")
    description: Optional[str] = Field(None, description="Detailed description or context of the investigation.")
    status: str = Field("active", description="Status of the case (active, archived)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
