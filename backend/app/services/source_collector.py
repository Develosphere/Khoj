import aiohttp
import asyncio
from typing import List
from app.models.source import Source
from app.schemas.source import SourceSchema
from datetime import datetime
from urllib.parse import urlparse, quote_plus
import logging

logger = logging.getLogger(__name__)


class BaseSourceProvider:
    async def search(self, query: str) -> List[Source]:
        raise NotImplementedError


class GoogleNewsRSSProvider(BaseSourceProvider):
    """Fetch news from Google News RSS feed"""
    
    async def search(self, query: str) -> List[Source]:
        try:
            # Google News RSS URL
            encoded_query = quote_plus(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(rss_url) as resp:
                    if resp.status != 200:
                        logger.warning(f"Google News RSS returned {resp.status}")
                        return []
                    
                    text = await resp.text()
                    
                    # Parse RSS XML
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(text)
                    
                    results = []
                    # Find all items in the RSS feed
                    for item in root.findall(".//item")[:10]:  # Limit to 10 items
                        title_elem = item.find("title")
                        link_elem = item.find("link")
                        pub_date_elem = item.find("pubDate")
                        description_elem = item.find("description")
                        source_elem = item.find("source")
                        
                        if title_elem is not None and link_elem is not None:
                            title = title_elem.text or ""
                            url = link_elem.text or ""
                            pub_date = pub_date_elem.text if pub_date_elem is not None else None
                            description = description_elem.text if description_elem is not None else ""
                            source_name = source_elem.text if source_elem is not None else "Google News"
                            
                            # Clean HTML from description
                            import re
                            description = re.sub(r'<[^>]+>', '', description)
                            
                            results.append(Source(
                                title=title,
                                url=url,
                                source_name=source_name,
                                published_at=pub_date,
                                content=description[:500] if description else title
                            ))
                    
                    logger.info(f"Google News RSS: Found {len(results)} articles")
                    return results
                    
        except Exception as e:
            logger.error(f"Google News RSS error: {e}")
            return []


class DuckDuckGoNewsProvider(BaseSourceProvider):
    """Fetch news from DuckDuckGo HTML search"""
    
    async def search(self, query: str) -> List[Source]:
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}&ia=news"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(search_url) as resp:
                    if resp.status != 200:
                        logger.warning(f"DuckDuckGo returned {resp.status}")
                        return []
                    
                    html = await resp.text()
                    
                    # Basic HTML parsing
                    import re
                    results = []
                    
                    # Extract links and titles from search results
                    link_pattern = r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
                    matches = re.findall(link_pattern, html)
                    
                    for url, title in matches[:8]:
                        if url and title:
                            # Clean URL
                            if url.startswith('//'):
                                url = 'https:' + url
                            
                            domain = urlparse(url).netloc
                            
                            results.append(Source(
                                title=title.strip(),
                                url=url,
                                source_name=domain or "DuckDuckGo News",
                                published_at=datetime.now().strftime("%Y-%m-%d"),
                                content=f"News article about {query} from {domain}"
                            ))
                    
                    logger.info(f"DuckDuckGo: Found {len(results)} articles")
                    return results
                    
        except Exception as e:
            logger.error(f"DuckDuckGo error: {e}")
            return []


class SourceCollector:
    def __init__(self, providers: List[BaseSourceProvider] = None):
        if providers is None:
            # Try Google News first, then DuckDuckGo as backup
            providers = [
                GoogleNewsRSSProvider(),
                DuckDuckGoNewsProvider()
            ]
        self.providers = providers

    async def collect_sources(self, case_name: str, min_results: int = 3) -> List[SourceSchema]:
        """
        Collect sources from multiple providers.
        Returns at least min_results sources or empty list if all fail.
        """
        all_sources = []
        
        for provider in self.providers:
            try:
                logger.info(f"Trying provider: {provider.__class__.__name__}")
                results = await provider.search(case_name)
                all_sources.extend(results)
                
                # If we have enough sources, stop trying other providers
                if len(all_sources) >= min_results:
                    logger.info(f"Collected {len(all_sources)} sources, stopping")
                    break
                    
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
                continue
        
        # Deduplicate by URL
        seen = set()
        deduped = []
        for src in all_sources:
            if src.url and src.url not in seen:
                seen.add(src.url)
                deduped.append(src)
        
        # Filter: require title and URL at minimum
        filtered = [s for s in deduped if s.title and s.url]
        
        # Limit to reasonable number
        filtered = filtered[:15]
        
        logger.info(f"Final result: {len(filtered)} unique sources")
        
        return [SourceSchema(**s.dict()) for s in filtered]
