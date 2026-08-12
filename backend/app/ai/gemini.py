import os
import aiohttp
import asyncio
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """Async Gemini client for factual claim and theory generation.

    Integrates with the live Google Gemini API if GEMINI_API_KEY is configured.
    Falls back to high-quality, contextual simulated responses for developers
    who haven't configured a key yet.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        # Use gemini-flash-lite-latest model for best performance/cost
        self.model = "gemini-flash-lite-latest"
        self.base_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )
        self.timeout = timeout
        self.max_retries = max_retries

    async def complete(
        self, 
        prompt: str, 
        response_format: Optional[str] = None,
        temperature: float = 0.7,
        **_: object
    ) -> str:
        """Send a prompt to Gemini and return the generated text.

        If GEMINI_API_KEY is missing or set to demo-key, it falls back to a high-quality simulated response.
        """
        if not self.api_key or self.api_key == "demo-key" or self.api_key == "":
            logger.info("GEMINI_API_KEY is not configured. Returning simulated case data.")
            return self._simulate_response(prompt)

        for attempt in range(self.max_retries):
            try:
                return await self._make_request(prompt, temperature, response_format)
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"GeminiClient: All {self.max_retries} attempts failed: {e}")
                    raise
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(
                    f"GeminiClient: Request failed (attempt {attempt + 1}/{self.max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"GeminiClient: Unexpected error: {e}")
                raise

    async def _make_request(
        self, 
        prompt: str, 
        temperature: float,
        response_format: Optional[str]
    ) -> str:
        """Make the actual HTTP request to Gemini API."""
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }
        
        if response_format == "json":
            payload["generationConfig"]["response_mime_type"] = "application/json"

        url = f"{self.base_url}?key={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"GeminiClient: API error {response.status}: {error_text}"
                    )
                    raise aiohttp.ClientError(
                        f"Gemini API returned {response.status}: {error_text}"
                    )
                
                data = await response.json()
                
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return text.strip()
                except (KeyError, IndexError) as e:
                    logger.error(
                        f"GeminiClient: Unexpected response structure: {e}\n"
                        f"Response: {json.dumps(data, indent=2)[:500]}"
                    )
                    raise ValueError(f"Malformed Gemini API response: {e}")

    def _simulate_response(self, prompt: str) -> str:
        """Generate high-quality mock data depending on the prompt type (evidence extraction vs theory generation)."""
        prompt_lower = prompt.lower()

        # A. Theory Generation Prompt
        if "competing theories" in prompt_lower or "timeline" in prompt_lower:
            dummy_theories = [
                {
                    "theory": "Accidental Thermal Runaway: The sector generator overheated due to a failure in the primary cooling valve, leading to a system shutoff.",
                    "confidence": 0.85,
                    "supporting_evidence": [
                        "An explosion occurred at Grid Sector 7 power generator.",
                        "Initial reports indicate a minor collision between two transport vessels."
                    ],
                    "timeline_events": ["12:00 event_1", "12:05 event_2"],
                    "summary": "This explanation fits the observed sequence of temperature rises and sudden pressure drop without assuming malicious activity."
                },
                {
                    "theory": "Targeted Cyber Sabotage: An external adversary compromised the OT control system, overriding automatic safety shutdown routines.",
                    "confidence": 0.70,
                    "supporting_evidence": [
                        "An explosion occurred at Grid Sector 7 power generator.",
                        "Witnesses saw a vehicle speeding away from the grid sector just before the incident."
                    ],
                    "timeline_events": ["12:00 event_1", "12:10 event_3"],
                    "summary": "Explains the override patterns observed on network switches, matching the temporal overlap of local activity."
                },
                {
                    "theory": "Physical Insider Intrusion: A disgruntled technician manually disabled cooling indicators before exiting the facility in haste.",
                    "confidence": 0.60,
                    "supporting_evidence": [
                        "Witnesses saw a vehicle sighting speeding away from the grid gates minutes before alarms sounded."
                    ],
                    "timeline_events": ["12:10 event_3"],
                    "summary": "Corroborated by the suspicious vehicle sighting speeding away from the grid gates minutes before alarms sounded."
                }
            ]
            return json.dumps(dummy_theories)

        # B. Evidence Extraction Prompt
        if "sector 7" in prompt_lower or "grid" in prompt_lower:
            dummy_evidence = [
                {
                    "claim": "An explosion occurred at Grid Sector 7 power generator.",
                    "confidence": 0.95,
                    "evidence_type": "official_statement",
                    "reasoning": "Confirmed by grid operator public status board."
                },
                {
                    "claim": "Witnesses saw a vehicle speeding away from the grid sector just before the incident.",
                    "confidence": 0.80,
                    "evidence_type": "eyewitness",
                    "reasoning": "Reported in interviews by three nearby residents."
                }
            ]
            return json.dumps(dummy_evidence)

        # Catch-all default evidence items
        dummy_default = [
            {
                "claim": "Initial reports indicate a minor collision between two transport vessels.",
                "confidence": 0.85,
                "evidence_type": "media_report",
                "reasoning": "Reported by local coast guard news bulletin."
            }
        ]
        return json.dumps(dummy_default)
