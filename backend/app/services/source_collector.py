import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from typing import List
from app.models.source import Source
from app.schemas.source import SourceSchema
from datetime import datetime
from urllib.parse import urlparse, quote_plus
import logging
import re

logger = logging.getLogger(__name__)


class BaseSourceProvider:
    async def search(self, query: str) -> List[Source]:
        raise NotImplementedError


class GoogleNewsRSSProvider(BaseSourceProvider):
    """
    Google News RSS feed provider - uses official Google News RSS API
    No API key required
    """
    BASE_URL = "https://news.google.com/rss/search"

    async def search(self, query: str) -> List[Source]:
        """Search Google News via RSS feed"""
        try:
            # Build URL
            encoded_query = quote_plus(query)
            url = f"{self.BASE_URL}?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            logger.info(f"GoogleNewsRSS: Fetching {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"GoogleNewsRSS: HTTP {resp.status}")
                        return []
                    
                    xml_content = await resp.text()
                    
            # Parse RSS feed using ElementTree
            root = ET.fromstring(xml_content)
            results = []
            
            # Find all items in the feed
            for item in root.findall('.//item')[:20]:  # Limit to 20 entries
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    
                    title = title_elem.text if title_elem is not None else ''
                    link = link_elem.text if link_elem is not None else ''
                    published = pubdate_elem.text if pubdate_elem is not None else ''
                    description = description_elem.text if description_elem is not None else ''
                    
                    # Extract source name from link
                    source_name = urlparse(link).netloc if link else 'Unknown'
                    
                    # Clean HTML from description
                    description = re.sub('<[^<]+?>', '', description)
                    
                    if title and link:
                        results.append(Source(
                            title=title,
                            url=link,
                            source_name=source_name,
                            published_at=published,
                            content=description or title
                        ))
                except Exception as e:
                    logger.warning(f"GoogleNewsRSS: Failed to parse item: {e}")
                    continue
            
            logger.info(f"GoogleNewsRSS: Collected {len(results)} sources")
            return results
            
        except asyncio.TimeoutError:
            logger.error("GoogleNewsRSS: Request timeout")
            return []
        except Exception as e:
            logger.error(f"GoogleNewsRSS: Error: {e}")
            return []


class DuckDuckGoNewsProvider(BaseSourceProvider):
    """
    DuckDuckGo news provider - DEPRECATED: API returns 403
    Kept for reference but not used by default
    """
    API_URL = "https://duckduckgo.com/news.js"

    async def search(self, query: str) -> List[Source]:
        logger.warning("DuckDuckGoNewsProvider: This provider is deprecated (403 errors)")
        return []


class SourceCollector:
    def __init__(self, providers: List[BaseSourceProvider] = None):
        if providers is None:
            # Use Google News RSS as default provider
            providers = [GoogleNewsRSSProvider()]
        self.providers = providers

    async def collect_sources(self, case_name: str, min_results: int = 10) -> List[SourceSchema]:
        all_sources = []
        for provider in self.providers:
            try:
                results = await provider.search(case_name)
                all_sources.extend(results)
            except Exception as e:
                logger.error(f"SourceCollector: Provider {provider.__class__.__name__} failed: {e}")
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
        
        # Limit to reasonable number (take up to min_results or all if less)
        filtered = filtered[:max(min_results, len(filtered)) if filtered else 0]
        
        logger.info(f"SourceCollector: Collected {len(filtered)} sources after dedup and filter")
        
        return [SourceSchema(**s.dict()) for s in filtered]
