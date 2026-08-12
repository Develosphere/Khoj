"""Test Google News RSS feed directly"""
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

async def test_google_news():
    query = "OpenAI GPT-5"
    encoded_query = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    print(f"Testing Google News RSS Feed...")
    print(f"URL: {url}")
    print()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            print(f"Status: {resp.status}")
            
            if resp.status == 200:
                xml_content = await resp.text()
                print(f"XML length: {len(xml_content)} chars")
                print()
                
                # Parse with ElementTree
                root = ET.fromstring(xml_content)
                items = root.findall('.//item')
                
                print(f"Found {len(items)} entries")
                print()
                
                for i, item in enumerate(items[:5], 1):
                    title = item.find('title')
                    link = item.find('link')
                    pubdate = item.find('pubDate')
                    
                    print(f"{i}. {title.text if title is not None else 'No title'}")
                    print(f"   URL: {link.text if link is not None else 'No link'}")
                    print(f"   Published: {pubdate.text if pubdate is not None else 'Unknown'}")
                    print()
            else:
                text = await resp.text()
                print(f"Error: {text[:500]}")

asyncio.run(test_google_news())
