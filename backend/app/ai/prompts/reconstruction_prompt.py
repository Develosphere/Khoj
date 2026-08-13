import json

from app.schemas.simulation import ReconstructionContext, SimulationScreenplay


def build_reconstruction_prompt(context: ReconstructionContext) -> str:
    return f"""You are KHOJ's reconstruction director. Return only one JSON object matching the supplied JSON schema.
Build a restrained, non-graphic, deterministic 3D screenplay for the selected theory.
Use only evidence, timeline, actor, vehicle, and provenance IDs present in the context. Never fabricate provenance.
Mark an event supported only when it has real evidence_ids and timeline_event_ids; otherwise mark minimal visual continuity inferred.
Keep every timestamp between zero and duration_seconds. Keep coordinates between -50 and 50.

CONTEXT:
{context.model_dump_json(indent=2)}

OUTPUT JSON SCHEMA:
{json.dumps(SimulationScreenplay.model_json_schema(), indent=2)}
"""
