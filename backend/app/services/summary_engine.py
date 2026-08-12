import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.ai.gemini import GeminiClient
from app.ai.prompts.summary_prompt import SUMMARY_GENERATION_PROMPT
from app.models.summary import Summary
from app.schemas.summary import SummarySchema

logger = logging.getLogger(__name__)


async def generate_summary(
    evidence: List[Any],
    timeline: List[Any],
    theories: List[Any],
) -> Optional[SummarySchema]:
    """Generate an investigation summary from evidence, timeline, and theories.

    This function:
    - Builds a structured prompt for Gemini Flash Lite
    - Requests JSON-only output
    - Defensively parses and validates the response using Pydantic

    Returns a SummarySchema on success, or None on any parsing/validation
    failure so the API layer can surface a clean 4xx error.
    """
    # Normalize inputs to plain JSON-serializable structures
    def _to_plain(obj: Any) -> Any:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if isinstance(obj, dict):
            return obj
        return obj

    evidence_json = json.dumps([_to_plain(e) for e in (evidence or [])], ensure_ascii=False)
    timeline_json = json.dumps([_to_plain(t) for t in (timeline or [])], ensure_ascii=False)
    theories_json = json.dumps([_to_plain(t) for t in (theories or [])], ensure_ascii=False)

    prompt = SUMMARY_GENERATION_PROMPT.format(
        evidence_json=evidence_json,
        timeline_json=timeline_json,
        theories_json=theories_json,
    )

    client = GeminiClient()
    try:
        raw = await client.complete(prompt, response_format="json")  # type: ignore[arg-type]
    except Exception as exc:  # Defensive: never propagate provider errors
        logger.error("SummaryEngine: Gemini request failed: %s", exc)
        return None

    if not raw or not str(raw).strip():
        logger.warning("SummaryEngine: Empty AI response received.")
        return None

    text = str(raw).strip()

    # Strip possible Markdown code fences crudely
    if text.startswith("```"):
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object for summary output.")
    except Exception as exc:
        logger.error(
            "SummaryEngine: Failed to parse AI response as JSON: %s | raw=%s",
            exc,
            text[:300],
        )
        return None

    # Pydantic validation via domain model first, then API schema
    try:
        # Coerce key_findings into a list of strings if it exists but is not well-formed
        key_findings = data.get("key_findings")
        if key_findings is None:
            data["key_findings"] = []
        elif not isinstance(key_findings, list):
            data["key_findings"] = [str(key_findings)]

        summary_model = Summary.model_validate(data)
        schema = SummarySchema(**summary_model.model_dump())
        return schema
    except ValidationError as ve:
        logger.error("SummaryEngine: Invalid summary output dropped: %s | data=%s", ve, data)
        return None
