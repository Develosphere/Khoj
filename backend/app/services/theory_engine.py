import json
import logging
from typing import List

from pydantic import ValidationError

from app.ai.gemini import GeminiClient
from app.ai.prompts.theory_prompt import THEORY_GENERATION_PROMPT
from app.models.theory import Theory
from app.schemas.theory import TheoryListResponse, TheorySchema

logger = logging.getLogger(__name__)


def deduplicate_theories(theories: List[Theory]) -> List[Theory]:
    """Remove duplicate theories based on normalized theory text."""
    seen = set()
    unique = []
    for t in theories:
        # Normalize theory text for comparison
        key = t.theory.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique


async def generate_theories(evidence: list, timeline: list) -> TheoryListResponse:
    """Generate at least 3 competing theories from evidence and timeline.
    
    Args:
        evidence: List of evidence objects (dicts or schemas)
        timeline: List of timeline event objects (dicts or schemas)
    
    Returns:
        TheoryListResponse with list of validated theories
    """
    # Convert inputs to plain dicts for JSON serialization
    def _to_dict(obj):
        if hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump()
        return obj
    
    evidence_dicts = [_to_dict(e) for e in evidence]
    timeline_dicts = [_to_dict(t) for t in timeline]
    
    prompt = THEORY_GENERATION_PROMPT.format(
        evidence_json=json.dumps(evidence_dicts, ensure_ascii=False, indent=2),
        timeline_json=json.dumps(timeline_dicts, ensure_ascii=False, indent=2),
    )
    
    gemini = GeminiClient()
    
    try:
        ai_response = await gemini.complete(prompt, response_format="json", temperature=0.8)
    except Exception as ex:
        logger.error(f"TheoryEngine: Gemini request failed: {ex}")
        return TheoryListResponse(theories=[])
    
    if not ai_response or not ai_response.strip():
        logger.warning("TheoryEngine: Empty AI response")
        return TheoryListResponse(theories=[])
    
    # Parse AI response
    try:
        # Strip markdown code fences if present
        text = ai_response.strip()
        if text.startswith("```"):
            lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
            text = "\n".join(lines).strip()
        
        parsed = json.loads(text)
        
        if not isinstance(parsed, list):
            raise ValueError("Expected JSON array of theories")
    except Exception as ex:
        logger.error(
            f"TheoryEngine: Failed to parse Gemini response as JSON: {ex}\n"
            f"Response (truncated): {ai_response[:500]}"
        )
        return TheoryListResponse(theories=[])
    
    # Validate each theory
    valid_theories = []
    for obj in parsed:
        if not isinstance(obj, dict):
            logger.warning(f"TheoryEngine: Skipping non-dict item: {obj}")
            continue
        
        try:
            theory = Theory.model_validate(obj)
            valid_theories.append(theory)
        except ValidationError as ve:
            logger.warning(
                f"TheoryEngine: Dropping invalid theory: {ve}\n"
                f"Object: {json.dumps(obj, indent=2)}"
            )
            continue
    
    # Deduplicate theories
    unique_theories = deduplicate_theories(valid_theories)
    
    # Require at least 3 valid theories
    if len(unique_theories) < 3:
        logger.warning(
            f"TheoryEngine: Only {len(unique_theories)} valid theories generated, "
            f"minimum 3 required"
        )
        return TheoryListResponse(theories=[])
    
    # Convert to schemas for API response
    theory_schemas = [
        TheorySchema(
            theory=t.theory,
            confidence=t.confidence,
            supporting_evidence=t.supporting_evidence,
            timeline_events=t.timeline_events,
            summary=t.summary
        )
        for t in unique_theories
    ]
    
    return TheoryListResponse(theories=theory_schemas)
