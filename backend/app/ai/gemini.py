import logging
import aiohttp

from app.core.config import settings


class GeminiClient:
    """Small async boundary around Gemini's generateContent REST API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.logger = logging.getLogger(__name__)

    async def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini is not configured. Set GEMINI_API_KEY.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.15,
            },
        }
        timeout = aiohttp.ClientTimeout(total=90)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, params={"key": self.api_key}, json=payload) as response:
                if response.status >= 400:
                    self.logger.error("Gemini request failed with status %s", response.status)
                    raise RuntimeError("Gemini reconstruction request failed.")
                body = await response.json()
        try:
            return body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini returned an empty reconstruction response.") from exc
