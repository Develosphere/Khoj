import logging
from typing import Any, Dict, List, Optional

from app.schemas.evidence import EvidenceSchema
from app.schemas.source import SourceSchema
from app.schemas.summary import SummarySchema
from app.schemas.theory import TheorySchema
from app.schemas.timeline import TimelineEventSchema
from app.services.evidence_engine import EvidenceEngine
from app.services.source_collector import SourceCollector
from app.services.summary_engine import generate_summary
from app.services.timeline_engine import TimelineEngine
from app.services.theory_engine import generate_theories

logger = logging.getLogger(__name__)


class InvestigationOrchestrator:
    """Coordinate the full investigation pipeline for a given case.

    Pipeline:
        case_name -> sources -> evidence -> timeline -> theories -> summary

    On failure of any stage, the orchestrator logs the error and returns
    partial results up to the last successful stage, leaving downstream
    collections empty (or summary as {}).
    """

    def __init__(
        self,
        source_collector: Optional[SourceCollector] = None,
        evidence_engine: Optional[EvidenceEngine] = None,
        timeline_engine: Optional[TimelineEngine] = None,
    ) -> None:
        self.source_collector = source_collector or SourceCollector()
        self.evidence_engine = evidence_engine or EvidenceEngine()
        self.timeline_engine = timeline_engine or TimelineEngine()

    async def run_investigation(
        self,
        case_name: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the full investigation pipeline for the given case name."""

        investigation: Dict[str, Any] = {
            "case_name": case_name,
            "sources": [],
            "evidence": [],
            "timeline": [],
            "theories": [],
            "summary": {},
        }

        logger.info(
            "InvestigationOrchestrator: starting pipeline case_name=%s user_id=%s",
            case_name,
            user_id,
        )

        # 1. Source collection
        try:
            sources: List[SourceSchema] = await self.source_collector.collect_sources(case_name)
            investigation["sources"] = [s.dict() for s in sources]
        except Exception as exc:
            logger.exception(
                "InvestigationOrchestrator: source collection failed for case=%s user_id=%s: %s",
                case_name,
                user_id,
                exc,
            )
            return investigation

        # 2. Evidence extraction
        try:
            source_dicts = [s.dict() for s in sources]
            evidence_items: List[EvidenceSchema] = await self.evidence_engine.extract_evidence(source_dicts)
            investigation["evidence"] = [e.dict() for e in evidence_items]
        except Exception as exc:
            logger.exception(
                "InvestigationOrchestrator: evidence extraction failed for case=%s user_id=%s: %s",
                case_name,
                user_id,
                exc,
            )
            return investigation

        # 3. Timeline generation
        try:
            timeline_events: List[TimelineEventSchema] = self.timeline_engine.extract_timeline(evidence_items)
            investigation["timeline"] = [t.dict() for t in timeline_events]
        except Exception as exc:
            logger.exception(
                "InvestigationOrchestrator: timeline generation failed for case=%s user_id=%s: %s",
                case_name,
                user_id,
                exc,
            )
            return investigation

        # Prepare plain JSON for AI-based stages
        evidence_payload = [e.dict() for e in evidence_items]
        timeline_payload = [t.dict() for t in timeline_events]

        # 4. Theory generation
        try:
            theories_response = await generate_theories(evidence_payload, timeline_payload)
            theories: List[TheorySchema] = theories_response.theories
            if not theories:
                logger.warning(
                    "InvestigationOrchestrator: theory generation returned no valid theories for case=%s user_id=%s",
                    case_name,
                    user_id,
                )
                return investigation
            investigation["theories"] = [th.dict() for th in theories]
        except Exception as exc:
            logger.exception(
                "InvestigationOrchestrator: theory generation failed for case=%s user_id=%s: %s",
                case_name,
                user_id,
                exc,
            )
            return investigation

        # 5. Summary generation
        try:
            summary: Optional[SummarySchema] = await generate_summary(
                evidence=evidence_payload,
                timeline=timeline_payload,
                theories=[th.dict() for th in theories],
            )
            if summary is None:
                logger.warning(
                    "InvestigationOrchestrator: summary generation returned no result for case=%s user_id=%s",
                    case_name,
                    user_id,
                )
                return investigation
            investigation["summary"] = summary.dict()
        except Exception as exc:
            logger.exception(
                "InvestigationOrchestrator: summary generation failed for case=%s user_id=%s: %s",
                case_name,
                user_id,
                exc,
            )
            return investigation

        logger.info(
            "InvestigationOrchestrator: completed pipeline case_name=%s user_id=%s",
            case_name,
            user_id,
        )
        return investigation
