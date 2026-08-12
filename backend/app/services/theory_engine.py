import json
from typing import List
from app.models.theory import Theory
from app.schemas.theory import TheoryListResponse
from app.ai.gemini import GeminiClient
from app.ai.prompts.theory_prompt import THEORY_GENERATION_PROMPT
from pydantic import ValidationError
import logging

def deduplicate_theories(theories: List[Theory]) -> List[Theory]:
    seen = set()
    unique = []
    for t in theories:
        key = (t.theory.strip().lower(), tuple(sorted(t.supporting_evidence)), tuple(sorted(t.timeline_events)))
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique

async def generate_theories(evidence: list, timeline: list) -> TheoryListResponse:
    prompt = THEORY_GENERATION_PROMPT.format(
        evidence_json=json.dumps(evidence, ensure_ascii=False),
        timeline_json=json.dumps(timeline, ensure_ascii=False),
    )
    gemini = GeminiClient()
    ai_response = await gemini.complete(prompt, response_format="json")
    try:
        parsed = json.loads(ai_response)
    except Exception as ex:
        logging.error(f"TheoryEngine: Failed to parse Gemini response as JSON: {ex}\n{ai_response}")
        return TheoryListResponse(theories=[])
    valid_theories = []
    for obj in parsed:
        try:
            theory = Theory.model_validate(obj)
            valid_theories.append(theory)
        except ValidationError as ve:
            logging.warning(f"TheoryEngine: Dropping invalid theory: {ve}\n[obj]={obj}")
            continue
    unique_theories = deduplicate_theories(valid_theories)
    # Only return if at least 3 valid theories
    if len(unique_theories) < 3:
        logging.warning(f"TheoryEngine: Less than 3 valid theories generated.")
        return TheoryListResponse(theories=[])
    return TheoryListResponse(theories=[t.model_dump() for t in unique_theories])
