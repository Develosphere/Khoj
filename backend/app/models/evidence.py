from pydantic import BaseModel, Field
from typing import Literal


class EvidenceType:
    """Canonical evidence type labels used throughout the investigation stack."""

    EYEWITNESS = "eyewitness"
    OFFICIAL_STATEMENT = "official_statement"
    MEDIA_REPORT = "media_report"
    FORENSIC = "forensic"
    UNKNOWN = "unknown"


class Evidence(BaseModel):
    """Domain model for a single piece of extracted evidence.

    This mirrors the EvidenceSchema fields but is placed under `models` for
    future persistence or richer domain logic.
    """

    claim: str = Field(..., description="Factual claim extracted from the source.")
    source: str = Field(..., description="Source URL or unique identifier.")
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence score between 0 and 1 inclusive."
    )
    evidence_type: Literal[
        EvidenceType.EYEWITNESS,
        EvidenceType.OFFICIAL_STATEMENT,
        EvidenceType.MEDIA_REPORT,
        EvidenceType.FORENSIC,
        EvidenceType.UNKNOWN,
    ] = Field(..., description="Type/category of evidence.")
    reasoning: str = Field(
        ..., description="Reasoning or justification for classification/confidence."
    )
