"""
Timeline Engine - Generates chronological timeline from evidence claims using Gemini AI.
"""

import json
import logging
from typing import List

from app.ai.gemini import GeminiClient
from app.ai.prompts.timeline_prompt import TIMELINE_GENERATION_PROMPT
from app.schemas.evidence import EvidenceSchema
from app.schemas.timeline import TimelineEventSchema


logger = logging.getLogger(__name__)


class TimelineEngine:
    """Service for generating chronological timelines from evidence using AI."""

    def __init__(self):
        self.gemini_client = GeminiClient()

    async def extract_timeline_async(self, evidence_list: List[EvidenceSchema]) -> List[TimelineEventSchema]:
        """
        Generate a chronological timeline of events from evidence claims.
        
        Args:
            evidence_list: List of evidence schema objects
            
        Returns:
            List of timeline event schemas sorted chronologically
        """
        if not evidence_list:
            logger.warning("No evidence provided for timeline generation")
            return []

        logger.info(f"Generating timeline from {len(evidence_list)} evidence claims")

        # Convert evidence to JSON for prompt
        evidence_dicts = []
        for ev in evidence_list:
            evidence_dicts.append({
                "claim": ev.claim,
                "source": ev.source,
                "confidence": ev.confidence,
                "evidence_type": ev.evidence_type,
                "reasoning": ev.reasoning
            })

        evidence_json = json.dumps(evidence_dicts, indent=2)
        
        # Generate timeline using Gemini
        prompt = TIMELINE_GENERATION_PROMPT.format(evidence_json=evidence_json)
        
        try:
            response_text = await self.gemini_client.complete(prompt)
            
            # Parse JSON response
            timeline_data = json.loads(response_text)
            
            if not isinstance(timeline_data, list):
                logger.error("Timeline response is not a JSON array")
                return []
            
            # Convert to schemas
            timeline_events = []
            for event_dict in timeline_data:
                try:
                    event = TimelineEventSchema(
                        time=event_dict.get("time", "Unknown time"),
                        event=event_dict.get("event", ""),
                        confidence=float(event_dict.get("confidence", 0.5)),
                        supporting_evidence=event_dict.get("supporting_evidence", [])
                    )
                    timeline_events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse timeline event: {e}")
                    continue
            
            logger.info(f"Successfully generated {len(timeline_events)} timeline events")
            return timeline_events
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse timeline JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"Timeline generation failed: {e}")
            return []
