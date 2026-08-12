import logging
from typing import List, Dict
from app.schemas.evidence import EvidenceSchema
from app.schemas.timeline import TimelineEventSchema
from collections import defaultdict
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class TimelineEngine:
    """
    Timeline generation engine.
    Responsibilities:
    - Accept a list of EvidenceSchema objects
    - Extract events with time, merge duplicates, order chronologically
    - Attach supporting evidence references
    - Validate outputs, handle errors gracefully
    """
    
    def extract_timeline(self, evidence_items: List[EvidenceSchema]) -> List[TimelineEventSchema]:
        """Generate a list of timeline events from evidence list."""
        event_map: Dict[str, dict] = {}
        for evidence in evidence_items:
            # Extract time and event from claim (placeholder logic, refine as needed)
            # Assume claim contains time as first word (improve with NLP or Regex)
            claim = evidence.claim.strip()
            try:
                time, event = claim.split(' ', 1)
            except ValueError:
                # No time found, skip this evidence
                logger.warning(f"Claim has no time component: '{claim}'")
                continue
            key = (time, event.lower())
            if key not in event_map:
                event_map[key] = {
                    'time': time,
                    'event': event,
                    'confidence': evidence.confidence,
                    'supporting_evidence': [claim]
                }
            else:
                # Merge: aggregate confidence as max, append supporting evidence
                event_map[key]['confidence'] = max(event_map[key]['confidence'], evidence.confidence)
                event_map[key]['supporting_evidence'].append(claim)
        # Convert to TimelineEventSchema and sort by time (lexicographically)
        timeline_events = []
        for val in event_map.values():
            try:
                event_obj = TimelineEventSchema(**val)
                timeline_events.append(event_obj)
            except ValidationError as ve:
                logger.warning(f"Invalid timeline event: {ve}")
                continue
        timeline_events.sort(key=lambda e: e.time)
        return timeline_events
