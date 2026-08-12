import asyncio
import json
import logging
import re
from typing import List, Dict, Optional
from collections import defaultdict

from pydantic import ValidationError

from app.ai.gemini import GeminiClient
from app.ai.prompts.timeline_prompt import TIMELINE_GENERATION_PROMPT
from app.schemas.evidence import EvidenceSchema
from app.schemas.timeline import TimelineEventSchema

logger = logging.getLogger(__name__)


class TimelineEngine:
    """
    Timeline generation engine using AI to extract temporal events from evidence.
    
    Responsibilities:
    - Accept a list of EvidenceSchema objects
    - Use AI to extract events with temporal information
    - Merge duplicate events, order chronologically
    - Attach supporting evidence references
    - Validate outputs, handle errors gracefully
    """
    
    def __init__(self, model: Optional[GeminiClient] = None):
        self.model = model or GeminiClient()
    
    async def extract_timeline_async(self, evidence_items: List[EvidenceSchema]) -> List[TimelineEventSchema]:
        """Async version - Generate timeline events from evidence using AI."""
        if not evidence_items:
            logger.warning("TimelineEngine: No evidence provided, returning empty timeline")
            return []
        
        # Convert evidence to plain dicts for the prompt
        evidence_dicts = [
            {
                "claim": e.claim,
                "confidence": e.confidence,
                "evidence_type": e.evidence_type,
                "source": e.source
            }
            for e in evidence_items
        ]
        
        prompt = TIMELINE_GENERATION_PROMPT.format(
            evidence_json=json.dumps(evidence_dicts, ensure_ascii=False, indent=2)
        )
        
        try:
            ai_response = await self.model.complete(prompt, response_format="json", temperature=0.5)
            timeline_events = self._parse_ai_response(ai_response, evidence_items)
            
            # Sort chronologically (attempting to parse dates, fall back to string sort)
            timeline_events = self._sort_chronologically(timeline_events)
            
            return timeline_events
        except Exception as e:
            logger.error(f"TimelineEngine: AI extraction failed: {e}")
            # Fallback to basic extraction
            return self._fallback_extraction(evidence_items)
    
    def extract_timeline(self, evidence_items: List[EvidenceSchema]) -> List[TimelineEventSchema]:
        """Synchronous wrapper for extract_timeline_async."""
        return asyncio.run(self.extract_timeline_async(evidence_items))
    
    def _parse_ai_response(
        self, 
        ai_response: str, 
        evidence_items: List[EvidenceSchema]
    ) -> List[TimelineEventSchema]:
        """Parse AI response and validate timeline events."""
        if not ai_response or not ai_response.strip():
            logger.warning("TimelineEngine: Empty AI response")
            return []
        
        try:
            # Strip markdown code fences if present
            text = ai_response.strip()
            if text.startswith("```"):
                lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
                text = "\n".join(lines).strip()
            
            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("Expected JSON array of timeline events")
            
            validated_events: List[TimelineEventSchema] = []
            event_keys_seen = set()
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                try:
                    # Validate and deduplicate
                    event = TimelineEventSchema(**item)
                    
                    # Deduplicate by normalized time + event description
                    key = (self._normalize_time(event.time), event.event.lower().strip())
                    if key in event_keys_seen:
                        continue
                    event_keys_seen.add(key)
                    
                    validated_events.append(event)
                except ValidationError as ve:
                    logger.warning(f"TimelineEngine: Invalid event dropped: {ve} | item={item}")
                    continue
            
            return validated_events
        
        except Exception as e:
            logger.error(
                f"TimelineEngine: Failed to parse AI response: {e}\n"
                f"Response (truncated): {ai_response[:500]}"
            )
            return []
    
    def _fallback_extraction(self, evidence_items: List[EvidenceSchema]) -> List[TimelineEventSchema]:
        """Fallback extraction using regex pattern matching when AI fails."""
        logger.info("TimelineEngine: Using fallback extraction method")
        
        # Patterns for common time expressions
        time_patterns = [
            r'(?:on|at|in|during)\s+([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',  # "on June 5th, 2024"
            r'(?:on|at|in)\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',  # "at 3:45 PM"
            r'(\d{4}-\d{2}-\d{2})',  # "2024-06-05"
            r'(\d{1,2}/\d{1,2}/\d{2,4})',  # "6/5/2024"
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',  # "June 5, 2024"
        ]
        
        event_map: Dict[tuple, dict] = {}
        
        for evidence in evidence_items:
            claim = evidence.claim.strip()
            
            # Try to extract time information
            time_found = None
            for pattern in time_patterns:
                match = re.search(pattern, claim, re.IGNORECASE)
                if match:
                    time_found = match.group(1).strip()
                    break
            
            if not time_found:
                # Use "Unknown time" for events without temporal information
                time_found = "Unknown time"
            
            # The event is the full claim
            event_text = claim
            
            # Create or merge event
            key = (self._normalize_time(time_found), event_text.lower())
            if key not in event_map:
                event_map[key] = {
                    'time': time_found,
                    'event': event_text,
                    'confidence': evidence.confidence,
                    'supporting_evidence': [claim]
                }
            else:
                # Merge: max confidence, accumulate evidence
                event_map[key]['confidence'] = max(
                    event_map[key]['confidence'], 
                    evidence.confidence
                )
                if claim not in event_map[key]['supporting_evidence']:
                    event_map[key]['supporting_evidence'].append(claim)
        
        # Convert to validated schemas
        timeline_events = []
        for val in event_map.values():
            try:
                event_obj = TimelineEventSchema(**val)
                timeline_events.append(event_obj)
            except ValidationError as ve:
                logger.warning(f"TimelineEngine: Fallback event validation failed: {ve}")
                continue
        
        return self._sort_chronologically(timeline_events)
    
    def _normalize_time(self, time_str: str) -> str:
        """Normalize time string for consistent sorting and comparison."""
        return time_str.strip().lower()
    
    def _sort_chronologically(self, events: List[TimelineEventSchema]) -> List[TimelineEventSchema]:
        """Sort timeline events chronologically, handling various date formats."""
        def sort_key(event: TimelineEventSchema) -> tuple:
            time_str = event.time.lower()
            
            # Try ISO date format (YYYY-MM-DD)
            iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', time_str)
            if iso_match:
                return (0, int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)), time_str)
            
            # Try to extract year for rough chronological ordering
            year_match = re.search(r'\b(19|20)\d{2}\b', time_str)
            if year_match:
                year = int(year_match.group(0))
                return (1, year, 0, 0, time_str)
            
            # Unknown time goes to end, sorted lexicographically
            if time_str.startswith('unknown'):
                return (2, 9999, 0, 0, time_str)
            
            # Everything else sorted lexicographically
            return (1, 0, 0, 0, time_str)
        
        try:
            return sorted(events, key=sort_key)
        except Exception as e:
            logger.warning(f"TimelineEngine: Sorting failed: {e}, using default order")
            return events
