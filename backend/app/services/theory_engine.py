"""
Theory Engine - Generates competing theories from evidence and timeline using Gemini AI.
"""

import json
import logging
from typing import List, Dict, Any

from app.ai.gemini import GeminiClient
from app.ai.prompts.theory_prompt import THEORY_GENERATION_PROMPT
from app.schemas.theory import TheoryListResponse


logger = logging.getLogger(__name__)


async def generate_theories(
    evidence_list: List[Dict[str, Any]],
    timeline_list: List[Dict[str, Any]]
) -> TheoryListResponse:
    """
    Generate competing theories from evidence and timeline data.
    
    Args:
        evidence_list: List of evidence dictionaries with keys: claim, source, confidence, evidence_type, reasoning
        timeline_list: List of timeline event dictionaries with keys: time, event, confidence, supporting_evidence
        
    Returns:
        TheoryListResponse containing list of generated theories
    """
    if not evidence_list and not timeline_list:
        logger.warning("No evidence or timeline provided for theory generation")
        return TheoryListResponse(theories=[])

    logger.info(f"Generating theories from {len(evidence_list)} evidence and {len(timeline_list)} timeline events")

    # Prepare JSON inputs for prompt
    evidence_json = json.dumps(evidence_list, indent=2)
    timeline_json = json.dumps(timeline_list, indent=2)
    
    # Generate theories using Gemini
    gemini_client = GeminiClient()
    prompt = THEORY_GENERATION_PROMPT.format(
        evidence_json=evidence_json,
        timeline_json=timeline_json
    )
    
    try:
        response_text = await gemini_client.complete(prompt)
        
        # Parse JSON response
        theories_data = json.loads(response_text)
        
        if not isinstance(theories_data, list):
            logger.error("Theory response is not a JSON array")
            return TheoryListResponse(theories=[])
        
        # Validate and structure theories
        valid_theories = []
        for theory_dict in theories_data:
            try:
                # Ensure all required fields exist
                if not theory_dict.get("theory") or not theory_dict.get("summary"):
                    continue
                    
                valid_theories.append({
                    "theory": theory_dict.get("theory", ""),
                    "confidence": float(theory_dict.get("confidence", 0.5)),
                    "supporting_evidence": theory_dict.get("supporting_evidence", []),
                    "timeline_events": theory_dict.get("timeline_events", []),
                    "summary": theory_dict.get("summary", "")
                })
            except Exception as e:
                logger.warning(f"Failed to parse theory: {e}")
                continue
        
        logger.info(f"Successfully generated {len(valid_theories)} theories")
        return TheoryListResponse(theories=valid_theories)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse theory JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        return TheoryListResponse(theories=[])
    except Exception as e:
        logger.error(f"Theory generation failed: {e}")
        return TheoryListResponse(theories=[])
