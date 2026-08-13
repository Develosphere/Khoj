from pydantic import BaseModel, Field
from typing import List, Literal


class EvidenceSchema(BaseModel):
    """API schema for a single evidence item returned by the engine."""

    id: str | None = None
    claim: str = Field(..., description="Factual claim extracted from the source.")
    source: str = Field(..., description="Source URL or unique identifier.")
    source_title: str | None = Field(None, description="Title of the source article.")
    source_url: str | None = Field(None, description="URL of the source article.")
    publisher: str | None = Field(None, description="Publisher/source name.")
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence score between 0 and 1 inclusive."
    )
    evidence_type: Literal[
        "eyewitness",
        "official_statement",
        "media_report",
        "forensic",
        "circumstantial",
        "unknown",
    ] = Field(..., description="Type/category of evidence.")
    reasoning: str = Field(
        ..., description="Reasoning or justification for classification/confidence."
    )


class EvidenceListResponse(BaseModel):
    """Wrapper schema for a list of evidence items."""

    evidence: List[EvidenceSchema]
