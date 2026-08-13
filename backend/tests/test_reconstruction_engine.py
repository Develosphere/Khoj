import pytest

from app.schemas.simulation import ReconstructionContext, SimulationScreenplay
from app.services.reconstruction_engine import (
    GeneratedGroundingError,
    InvalidInputProvenanceError,
    normalize_screenplay,
    validate_context,
    validate_screenplay,
)


def context() -> ReconstructionContext:
    return ReconstructionContext.model_validate({
        "investigation_id": "case-1",
        "evidence": [{"id": "e-1", "claim": "Observed arrival", "source": "report", "confidence": 0.9}],
        "timeline": [{"id": "t-1", "sequence": 0, "event": "Arrival", "evidence_ids": ["e-1"]}],
        "selected_theory": {
            "id": "th-1", "title": "Arrival theory", "confidence": 0.8, "narrative": "An arrival occurred.",
            "timeline_event_ids": ["t-1"], "supporting_evidence_ids": ["e-1"], "contradicting_evidence_ids": [],
        },
    })


def screenplay_payload() -> dict:
    return {
        "schema_version": "1.0", "id": "draft", "investigation_id": "case-1", "title": "Reconstruction", "duration_seconds": 5,
        "environment": {"preset": "urban_street", "time_of_day": "day"},
        "actors": [], "vehicles": [],
        "events": [{"id": "event-1", "time": 1, "type": "arrival", "label": "Arrival", "certainty": "supported", "evidence_ids": ["e-1"], "timeline_event_ids": ["t-1"]}],
        "camera_shots": [{"start": 0, "end": 5, "type": "wide"}],
    }


def test_rejects_unknown_input_provenance():
    invalid = context().model_copy(deep=True)
    invalid.selected_theory.supporting_evidence_ids = ["missing"]
    with pytest.raises(InvalidInputProvenanceError):
        validate_context(invalid)


def test_normalizes_order_without_rewriting_provenance():
    payload = screenplay_payload()
    payload["events"].append({"id": "event-0", "time": 0, "type": "context", "label": "Context", "certainty": "inferred", "evidence_ids": [], "timeline_event_ids": []})
    screenplay = normalize_screenplay(payload)
    assert [event.id for event in screenplay.events] == ["event-0", "event-1"]
    assert screenplay.events[1].evidence_ids == ["e-1"]


def test_rejects_unknown_camera_target():
    screenplay = SimulationScreenplay.model_validate(screenplay_payload())
    screenplay.camera_shots[0].target_id = "missing"
    with pytest.raises(GeneratedGroundingError):
        validate_screenplay(screenplay, context())
