import pytest
import asyncio
from app.services.source_collector import SourceCollector

@pytest.mark.asyncio
async def test_collect_sources_returns_list():
    collector = SourceCollector()
    sources = await collector.collect_sources('Ukraine conflict')
    assert isinstance(sources, list)
    assert len(sources) >= 1
    for s in sources:
        assert 'title' in s.dict()
        assert 'url' in s.dict()
        assert 'source_name' in s.dict()
        assert 'content' in s.dict()
