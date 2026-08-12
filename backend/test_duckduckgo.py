"""Test DuckDuckGo API directly"""
import aiohttp
import asyncio
import json

async def test_ddg_api():
    print("Testing DuckDuckGo News API...")
    
    # Try the news endpoint
    url = "https://duckduckgo.com/news.js"
    query = "OpenAI GPT-5"
    params = {"q": query, "o": "json"}
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            print(f"Status: {resp.status}")
            print(f"Headers: {dict(resp.headers)}")
            print()
            
            text = await resp.text()
            print(f"Response (first 1000 chars):")
            print(text[:1000])
            print()
            
            if resp.status == 200:
                try:
                    data = await resp.json()
                    print("JSON Response:")
                    print(json.dumps(data, indent=2)[:500])
                except:
                    print("Not valid JSON")

asyncio.run(test_ddg_api())
