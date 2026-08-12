from typing import List

from pydantic import BaseModel, Field


class Summary(BaseModel):
    """Domain model for an investigation summary.

    This mirrors the API schema fields so it can later be persisted or
    extended with additional domain logic without impacting the transport
    contract.
    """

    summary: str = Field(..., description="High-level narrative summary of the case.")
    key_findings: List[str] = Field(
        default_factory=list,
        description="Bullet-style list of the most important findings.",
    )
    top_theory: str = Field(
        ..., description="Short description of the best-supported theory."
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence (0-1) in the top theory."
    )
