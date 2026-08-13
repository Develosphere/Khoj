import aiohttp
import asyncio
from typing import List
from app.models.source import Source
from app.schemas.source import SourceSchema
from datetime import datetime
from urllib.parse import urlparse

class BaseSourceProvider:
    async def search(self, query: str) -> List[Source]:
        raise NotImplementedError

class DuckDuckGoNewsProvider(BaseSourceProvider):
    # Example using DuckDuckGo's unofficial news API endpoint
    API_URL = "https://duckduckgo.com/news.js"

    async def search(self, query: str) -> List[Source]:
        params = {"q": query, "o": "json"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL, params=params, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                results = []
                for item in data.get("results", []):
                    results.append(Source(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        source_name=urlparse(item.get("url", "")).netloc,
                        published_at=item.get("date", None),
                        content=item.get("excerpt", "")
                    ))
                return results

class SourceCollector:
    def __init__(self, providers: List[BaseSourceProvider]=None):
        if providers is None:
            providers = [DuckDuckGoNewsProvider()]
        self.providers = providers

    async def collect_sources(self, case_name: str, min_results: int = 10) -> List[SourceSchema]:
        all_sources = []
        for provider in self.providers:
            try:
                results = await provider.search(case_name)
                all_sources.extend(results)
            except Exception:
                continue
        # Deduplicate by URL
        seen = set()
        deduped = []
        for src in all_sources:
            if src.url not in seen and src.url:
                seen.add(src.url)
                deduped.append(src)
        # Basic filtering: remove sources missing title/content/url
        filtered = [s for s in deduped if s.title and s.content and s.url]
        # Limit to min_results
        filtered = filtered[:max(min_results, len(filtered))]
        return [SourceSchema(**s.dict()) for s in filtered]

# Example usage:
# collector = SourceCollector()
# asyncio.run(collector.collect_sources("case name"))
