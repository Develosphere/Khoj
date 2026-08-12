import os
import aiohttp
import asyncio
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Async OpenRouter client for AI completion requests.
    Can be used as fallback when Gemini is unavailable.
    """

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "openai/gpt-3.5-turbo",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required for OpenRouterClient"
            )
        
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
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
        Send a prompt to OpenRouter and return the generated text.

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
                    logger.error(
                        f"OpenRouterClient: All {self.max_retries} attempts failed: {e}"
                    )
                    raise
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(
                    f"OpenRouterClient: Request failed (attempt {attempt + 1}/{self.max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"OpenRouterClient: Unexpected error: {e}")
                raise

    async def _make_request(
        self,
        prompt: str,
        temperature: float,
        response_format: Optional[str]
    ) -> str:
        """Make the actual HTTP request to OpenRouter API."""
        
        # Build request payload
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 8192,
        }
        
        # Add JSON mode if requested
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://khoj-investigation.app",
            "X-Title": "KHOJ Investigation Platform"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"OpenRouterClient: API error {response.status}: {error_text}"
                    )
                    raise aiohttp.ClientError(
                        f"OpenRouter API returned {response.status}: {error_text}"
                    )
                
                data = await response.json()
                
                # Extract text from OpenRouter response
                try:
                    text = data["choices"][0]["message"]["content"]
                    return text.strip()
                except (KeyError, IndexError) as e:
                    logger.error(
                        f"OpenRouterClient: Unexpected response structure: {e}\n"
                        f"Response: {json.dumps(data, indent=2)[:500]}"
                    )
                    raise ValueError(f"Malformed OpenRouter API response: {e}")
