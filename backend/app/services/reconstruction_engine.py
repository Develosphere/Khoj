import json
import re

from pydantic import ValidationError

from app.ai.gemini import GeminiClient
from app.ai.prompts.reconstruction_prompt import build_reconstruction_prompt
from app.schemas.simulation import ReconstructionContext, SimulationScreenplay


class ReconstructionError(ValueError):
    pass


class InvalidInputProvenanceError(ReconstructionError):
    pass


class InvalidGeneratedSchemaError(ReconstructionError):
    pass


class GeneratedGroundingError(ReconstructionError):
    pass


def validate_context(context: ReconstructionContext) -> None:
    evidence_ids = {item.id for item in context.evidence}
    timeline_ids = {item.id for item in context.timeline}
    theory = context.selected_theory
    unknown_evidence = (
        set(theory.supporting_evidence_ids)
        | set(theory.contradicting_evidence_ids)
        | {evidence_id for event in context.timeline for evidence_id in event.evidence_ids}
    ) - evidence_ids
    unknown_timeline = set(theory.timeline_event_ids) - timeline_ids
    if unknown_evidence:
        raise InvalidInputProvenanceError(f"Unknown input evidence reference: {sorted(unknown_evidence)[0]}")
    if unknown_timeline:
        raise InvalidInputProvenanceError(f"Unknown input timeline reference: {sorted(unknown_timeline)[0]}")


def _clean_json(raw: str) -> object:
    text = raw.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidGeneratedSchemaError("Gemini returned invalid screenplay JSON.") from exc


def _trim(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [_trim(item) for item in value]
    if isinstance(value, dict):
        return {key: _trim(item) for key, item in value.items()}
    return value


def normalize_screenplay(payload: object) -> SimulationScreenplay:
    if not isinstance(payload, dict):
        raise InvalidGeneratedSchemaError("Gemini screenplay must be a JSON object.")
    normalized = _trim(payload)
    assert isinstance(normalized, dict)
    for collection in ("actors", "vehicles"):
        for entity in normalized.get(collection, []):
            entity["motion_track"] = sorted(entity.get("motion_track", []), key=lambda frame: frame.get("time", 0))
    normalized["events"] = sorted(normalized.get("events", []), key=lambda event: event.get("time", 0))
    normalized["camera_shots"] = sorted(normalized.get("camera_shots", []), key=lambda shot: shot.get("start", 0))
    try:
        return SimulationScreenplay.model_validate(normalized)
    except ValidationError as exc:
        raise InvalidGeneratedSchemaError("Gemini returned an invalid screenplay schema.") from exc


def validate_screenplay(screenplay: SimulationScreenplay, context: ReconstructionContext) -> None:
    evidence_ids = {item.id for item in context.evidence}
    timeline_ids = {item.id for item in context.timeline}
    entity_ids = [item.id for item in screenplay.actors] + [item.id for item in screenplay.vehicles]
    if len(entity_ids) != len(set(entity_ids)):
        raise GeneratedGroundingError("Actor and vehicle IDs must be globally unique.")
    entity_id_set = set(entity_ids)
    duration = screenplay.duration_seconds

    for event in screenplay.events:
        if event.time > duration or event.time + (event.duration or 0) > duration:
            raise GeneratedGroundingError("Invalid event timestamp.")
        if set(event.evidence_ids) - evidence_ids:
            raise GeneratedGroundingError("Unknown evidence reference in generated screenplay.")
        if set(event.timeline_event_ids) - timeline_ids:
            raise GeneratedGroundingError("Unknown timeline reference in generated screenplay.")
        if event.certainty == "supported" and (not event.evidence_ids or not event.timeline_event_ids):
            raise GeneratedGroundingError("Supported events require evidence and timeline provenance.")

    for entity in [*screenplay.actors, *screenplay.vehicles]:
        timestamps = [entity.spawn.time, *(frame.time for frame in entity.motion_track), *(action.start for action in entity.actions)]
        timestamps.extend(action.end for action in entity.actions if action.end is not None)
        if any(timestamp > duration for timestamp in timestamps):
            raise GeneratedGroundingError("Invalid entity timestamp.")
    for shot in screenplay.camera_shots:
        if shot.start > duration or shot.end > duration:
            raise GeneratedGroundingError("Invalid camera timestamp.")
        if shot.target_id and shot.target_id not in entity_id_set:
            raise GeneratedGroundingError("Unknown camera target.")


async def generate_reconstruction(
    context: ReconstructionContext,
    client: GeminiClient | None = None,
) -> SimulationScreenplay:
    validate_context(context)
    raw = await (client or GeminiClient()).complete(build_reconstruction_prompt(context))
    screenplay = normalize_screenplay(_clean_json(raw))
    if screenplay.investigation_id != context.investigation_id:
        raise GeneratedGroundingError("Generated investigation reference does not match the request.")
    validate_screenplay(screenplay, context)
    return screenplay
