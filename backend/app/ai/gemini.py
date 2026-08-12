import os
import aiohttp
import asyncio
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Async Gemini Flash Lite client for AI completion requests.
    Uses Google's Generative Language API.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required for GeminiClient"
            )
        
        # Use gemini-2.0-flash-lite-latest model for best performance/cost
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
        """
        Send a prompt to Gemini and return the generated text.

        Args:
            prompt: The text prompt to send
            response_format: Optional format hint (e.g., "json")
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text response as string

        Raises:
            Exception: On API errors after retries exhausted
        """
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
        
        # Build request payload according to Gemini API specification
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
        
        # If JSON response is requested, add it to the prompt as instruction
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
                
                # Extract text from Gemini response structure
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return text.strip()
                except (KeyError, IndexError) as e:
                    logger.error(
                        f"GeminiClient: Unexpected response structure: {e}\n"
                        f"Response: {json.dumps(data, indent=2)[:500]}"
                    )
                    raise ValueError(f"Malformed Gemini API response: {e}")
