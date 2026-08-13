import asyncio
import json
import logging
from typing import List, Optional

from app.schemas.evidence import EvidenceSchema
from app.ai.gemini import GeminiClient
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class EvidenceExtractionError(Exception):
    """Raised for unrecoverable evidence extraction errors (not used in normal flow)."""


class EvidenceEngine:
    """Async, provider-independent evidence extraction engine.

    Responsibilities:
    - Accept a list of collected source objects (dicts or Pydantic models).
    - Call an AI provider (Gemini Flash Lite by default) to extract factual claims.
    - Deduplicate claims across sources.
    - Assign confidence scores and evidence categories.
    - Validate all outputs with Pydantic.
    - Fail gracefully on any AI / parsing errors, never crashing the server.
    """

    def __init__(self, model: Optional[GeminiClient] = None) -> None:
        # GeminiClient is our default provider, but any compatible client
        # implementing `async def complete(prompt: str) -> str` can be injected.
        self.model = model or GeminiClient()

    async def extract_evidence(self, sources: List[dict]) -> List[EvidenceSchema]:
        """Extract structured evidence from a list of collected sources.

        Args:
            sources: Iterable of source-like dicts with at least `title`, `url`, `content`.

        Returns:
            List of Pydantic-validated EvidenceSchema items, deduplicated by claim text.
        """
        evidence_items: List[EvidenceSchema] = []
        seen_claims: set[str] = set()

        tasks = [self._extract_from_source(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.warning("Evidence extraction failed for a source: %s", result)
                continue

            for item in result:
                # Deduplicate by normalized claim string
                claim_norm = item.claim.strip().lower()
                if claim_norm in seen_claims:
                    continue
                seen_claims.add(claim_norm)
                evidence_items.append(item)

        return evidence_items

    async def _extract_from_source(self, source: dict) -> List[EvidenceSchema]:
        """Extract evidence from a single source using the configured provider.

        All errors are logged and result in an empty list for this source.
        """
        try:
            content = source.get("content", "") or ""
            title = source.get("title", "") or ""
            url = source.get("url", "") or ""
            source_name = source.get("source_name", "") or ""

            if not content.strip():
                # Nothing to analyze
                return []

            prompt = self._build_prompt(title=title, content=content)
            ai_response = await self.model.complete(prompt)
            parsed_items = self._parse_ai_response(ai_response, url, title, source_name)

            validated: List[EvidenceSchema] = []
            for raw in parsed_items:
                try:
                    validated.append(EvidenceSchema(**raw))
                except ValidationError as ve:
                    logger.warning("Invalid evidence item discarded for url=%s: %s", url, ve)
                    continue

            return validated

        except Exception as e:  # Defensive: never allow a single source to crash the flow
            logger.warning("Gemini evidence extraction failed for %s: %s", source.get("url", ""), e)
            return []

    def _build_prompt(self, title: str, content: str) -> str:
        """Constructs the Gemini prompt for factual-claim extraction.

        The model is instructed to output ONLY a JSON array of objects using
        the Evidence schema fields (except `source`, which is filled in by the engine).
        """
        # Trim very long content to keep requests efficient and within model limits
        truncated_content = content[:4000]

        return (
            "You are an AI investigator.\n"
            "Given the following news/reporting source, extract all distinct factual claims "
            "as structured JSON. Focus on verifiable facts, not opinions.\n\n"
            f"Title: {title}\n"
            f"Content: {truncated_content}\n\n"
            "Output a JSON array of objects, with no extra commentary, exactly in this shape:\n"
            "[\n"
            "  {\n"
            "    \"claim\": \"string factual claim\",\n"
            "    \"confidence\": 0.0,\n"
            "    \"evidence_type\": \"eyewitness\" | \"official_statement\" | \"media_report\" | \"forensic\" | \"unknown\",\n"
            "    \"reasoning\": \"short explanation for the confidence and classification\"\n"
            "  }\n"
            "]\n\n"
            "Rules:\n"
            "- Return ONLY valid JSON (no Markdown, no code fences, no trailing commas).\n"
            "- Use only double quotes in the JSON.\n"
            "- confidence is a float between 0.0 and 1.0.\n"
            "- Choose evidence_type from: eyewitness, official_statement, media_report, forensic, unknown.\n"
            "- If there are no clear factual claims, return an empty JSON array: [].\n"
        )

    def _parse_ai_response(self, ai_response: str, url: str, source_title: str, publisher: str) -> List[dict]:
        """Parse Gemini response, attach source metadata, and handle malformed output.

        Any parsing issues result in an empty list.
        """
        if not ai_response or not str(ai_response).strip():
            return []

        try:
            # Some providers may wrap the JSON in Markdown fences; strip them crudely.
            text = str(ai_response).strip()
            if text.startswith("```"):
                # Remove first and last fenced code block markers
                lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
                text = "\n".join(lines).strip()

            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("Expected a JSON array of evidence items.")

            for item in data:
                # Ensure each item is a dict we can enrich
                if isinstance(item, dict):
                    # Attach source metadata so every evidence can be traced
                    item["source"] = url
                    item["source_url"] = url
                    item["source_title"] = source_title
                    item["publisher"] = publisher
            # Filter out any non-dict entries
            return [item for item in data if isinstance(item, dict)]

        except Exception as e:
            logger.warning(
                "Malformed AI response for url=%s: %s. Raw response (truncated): %s",
                url,
                e,
                str(ai_response)[:300],
            )
            return []
