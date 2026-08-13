import pytest
import asyncio
from backend.app.services.evidence_engine import EvidenceEngine

class DummyGemini:
    async def complete(self, prompt: str) -> str:
        return '[{"claim": "Sky is blue.", "confidence": 0.95, "evidence_type": "media_report", "reasoning": "Widely reported.", "source": ""}]'

def test_extract_evidence_from_sources():
    sources = [
        {"title": "Science News", "url": "https://news.example.com/sky", "content": "Scientists say the sky is blue."},
        {"title": "Science News", "url": "https://news.example.com/sky", "content": "Scientists say the sky is blue."}  # Duplicate
    ]
    engine = EvidenceEngine(model=DummyGemini())
    results = asyncio.run(engine.extract_evidence(sources))
    assert len(results) == 1  # Deduped
    ev = results[0]
    assert ev.claim == "Sky is blue."
    assert ev.confidence == 0.95
    assert ev.evidence_type == "media_report"
    assert ev.reasoning == "Widely reported."
    assert ev.source == "https://news.example.com/sky"
