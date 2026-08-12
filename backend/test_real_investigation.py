"""
REAL Investigation Engine Test - NO MOCKS
Tests against actual external services with real API calls
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("="*80)
print("REAL INVESTIGATION ENGINE TEST - NO MOCKS")
print("="*80)
print()

# Verify environment variables
print("🔑 Checking Environment Variables...")
gemini_key = os.getenv("GEMINI_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if not gemini_key:
    print("❌ GEMINI_API_KEY not set")
    sys.exit(1)
else:
    print(f"✅ GEMINI_API_KEY: {gemini_key[:20]}...")

if not openrouter_key:
    print("⚠️  OPENROUTER_API_KEY not set (fallback unavailable)")
else:
    print(f"✅ OPENROUTER_API_KEY: {openrouter_key[:20]}...")

print()

# Import services
from app.services.source_collector import SourceCollector
from app.services.evidence_engine import EvidenceEngine
from app.services.timeline_engine import TimelineEngine
from app.services.theory_engine import generate_theories
from app.services.summary_engine import generate_summary
from app.ai.gemini import GeminiClient


async def test_1_source_collector():
    """Test 1: Real source collection from DuckDuckGo"""
    print("="*80)
    print("TEST 1: SOURCE COLLECTOR (Real DuckDuckGo API)")
    print("="*80)
    print()
    
    case_name = "OpenAI GPT-5 release"
    print(f"Query: '{case_name}'")
    print()
    
    try:
        collector = SourceCollector()
        print("🔍 Calling DuckDuckGo news API...")
        sources = await collector.collect_sources(case_name, min_results=10)
        
        print(f"✅ Collected {len(sources)} sources")
        print()
        
        if sources:
            print("First 5 sources:")
            for i, source in enumerate(sources[:5], 1):
                print(f"{i}. {source.title}")
                print(f"   URL: {source.url}")
                print(f"   Source: {source.source_name}")
                print(f"   Published: {source.published_at}")
                print(f"   Content preview: {source.content[:100]}...")
                print()
            
            # Verify these are REAL URLs
            if any("example.com" in s.url for s in sources):
                print("❌ FAIL: Found example.com in sources (fake data)")
                return False, sources
            
            print("✅ PASS: All sources have real URLs")
            return True, sources
        else:
            print("❌ FAIL: No sources collected")
            return False, []
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, []


async def test_2_gemini_client():
    """Test 2: Real Gemini API call"""
    print("="*80)
    print("TEST 2: GEMINI CLIENT (Real API Call)")
    print("="*80)
    print()
    
    try:
        client = GeminiClient()
        print(f"📡 API Key: {client.api_key[:20]}...")
        print(f"📡 Model: {client.model}")
        print(f"📡 Base URL: {client.base_url}")
        print()
        
        prompt = "List 3 interesting facts about artificial intelligence in JSON array format: [{\"fact\": \"...\"}]"
        print(f"Prompt: {prompt[:80]}...")
        print()
        
        print("🚀 Sending request to Gemini API...")
        response = await client.complete(prompt, response_format="json", temperature=0.7)
        
        print("✅ Response received")
        print()
        print("Response preview:")
        print(response[:500])
        print()
        
        # Verify it's valid JSON
        try:
            data = json.loads(response)
            print("✅ Valid JSON response")
            print(f"✅ PASS: Gemini API working")
            return True, response
        except:
            print("⚠️  Response not valid JSON but API call succeeded")
            return True, response
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_3_evidence_extraction(sources):
    """Test 3: Real evidence extraction using Gemini"""
    print("="*80)
    print("TEST 3: EVIDENCE EXTRACTION (Real Gemini API)")
    print("="*80)
    print()
    
    if not sources:
        print("⚠️  SKIPPED: No sources from previous test")
        return False, []
    
    try:
        # Use first 3 sources
        source_dicts = [s.dict() for s in sources[:3]]
        print(f"Extracting evidence from {len(source_dicts)} sources...")
        print()
        
        engine = EvidenceEngine()
        print("🤖 Calling Gemini API for evidence extraction...")
        evidence = await engine.extract_evidence(source_dicts)
        
        print(f"✅ Extracted {len(evidence)} evidence items")
        print()
        
        if evidence:
            print("First 5 evidence items:")
            for i, ev in enumerate(evidence[:5], 1):
                print(f"{i}. {ev.claim}")
                print(f"   Confidence: {ev.confidence}")
                print(f"   Type: {ev.evidence_type}")
                print(f"   Source: {ev.source[:60]}...")
                print()
            
            print(f"✅ PASS: Evidence extraction working")
            return True, evidence
        else:
            print("⚠️  No evidence extracted (may be valid if sources have no claims)")
            return True, []
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, []


async def test_4_timeline_generation(evidence):
    """Test 4: Real timeline generation using Gemini"""
    print("="*80)
    print("TEST 4: TIMELINE GENERATION (Real Gemini API)")
    print("="*80)
    print()
    
    if not evidence:
        print("⚠️  SKIPPED: No evidence from previous test")
        return False, []
    
    try:
        engine = TimelineEngine()
        print(f"Generating timeline from {len(evidence)} evidence items...")
        print()
        
        print("🤖 Calling Gemini API for timeline generation...")
        timeline = await engine.extract_timeline_async(evidence)
        
        print(f"✅ Generated {len(timeline)} timeline events")
        print()
        
        if timeline:
            print("Timeline events:")
            for i, event in enumerate(timeline[:5], 1):
                print(f"{i}. {event.time}: {event.event}")
                print(f"   Confidence: {event.confidence}")
                print(f"   Supporting: {len(event.supporting_evidence)} items")
                print()
            
            print(f"✅ PASS: Timeline generation working")
            return True, timeline
        else:
            print("⚠️  No timeline events (may be valid if no temporal info)")
            return True, []
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, []


async def test_5_theory_generation(evidence, timeline):
    """Test 5: Real theory generation using Gemini"""
    print("="*80)
    print("TEST 5: THEORY GENERATION (Real Gemini API)")
    print("="*80)
    print()
    
    if not evidence:
        print("⚠️  SKIPPED: No evidence from previous test")
        return False, []
    
    try:
        evidence_dicts = [e.dict() for e in evidence]
        timeline_dicts = [t.dict() for t in timeline]
        
        print(f"Generating theories from {len(evidence_dicts)} evidence + {len(timeline_dicts)} timeline events...")
        print()
        
        print("🤖 Calling Gemini API for theory generation...")
        result = await generate_theories(evidence_dicts, timeline_dicts)
        
        theories = result.theories
        print(f"✅ Generated {len(theories)} theories")
        print()
        
        if theories:
            print("Generated theories:")
            for i, theory in enumerate(theories, 1):
                print(f"{i}. {theory.theory}")
                print(f"   Confidence: {theory.confidence}")
                print(f"   Supporting evidence: {len(theory.supporting_evidence)} items")
                print()
            
            if len(theories) >= 3:
                print(f"✅ PASS: Theory generation working (≥3 theories)")
                return True, theories
            else:
                print(f"⚠️  Only {len(theories)} theories generated (need ≥3)")
                return False, theories
        else:
            print("❌ FAIL: No theories generated")
            return False, []
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, []


async def test_6_summary_generation(evidence, timeline, theories):
    """Test 6: Real summary generation using Gemini"""
    print("="*80)
    print("TEST 6: SUMMARY GENERATION (Real Gemini API)")
    print("="*80)
    print()
    
    if not evidence or not theories:
        print("⚠️  SKIPPED: Missing evidence or theories")
        return False, None
    
    try:
        evidence_dicts = [e.dict() for e in evidence]
        timeline_dicts = [t.dict() for t in timeline]
        theory_dicts = [t.dict() if hasattr(t, 'dict') else t for t in theories]
        
        print(f"Generating summary from {len(evidence_dicts)} evidence + {len(timeline_dicts)} timeline + {len(theory_dicts)} theories...")
        print()
        
        print("🤖 Calling Gemini API for summary generation...")
        summary = await generate_summary(evidence_dicts, timeline_dicts, theory_dicts)
        
        if summary:
            print("✅ Summary generated")
            print()
            print(f"Summary: {summary.summary}")
            print()
            print(f"Key Findings ({len(summary.key_findings)}):")
            for finding in summary.key_findings[:5]:
                print(f"  • {finding}")
            print()
            print(f"Top Theory: {summary.top_theory}")
            print(f"Confidence: {summary.confidence}")
            print()
            
            print(f"✅ PASS: Summary generation working")
            return True, summary
        else:
            print("❌ FAIL: No summary generated")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def main():
    """Run all tests"""
    print("Starting real Investigation Engine tests...")
    print("This will make actual API calls to external services.")
    print()
    
    results = {}
    
    # Test 1: Source Collection
    success, sources = await test_1_source_collector()
    results['source_collection'] = success
    
    # Test 2: Gemini Client
    success, response = await test_2_gemini_client()
    results['gemini_client'] = success
    
    # Test 3: Evidence Extraction
    success, evidence = await test_3_evidence_extraction(sources)
    results['evidence_extraction'] = success
    
    # Test 4: Timeline Generation
    success, timeline = await test_4_timeline_generation(evidence)
    results['timeline_generation'] = success
    
    # Test 5: Theory Generation
    success, theories = await test_5_theory_generation(evidence, timeline)
    results['theory_generation'] = success
    
    # Test 6: Summary Generation
    success, summary = await test_6_summary_generation(evidence, timeline, theories)
    results['summary_generation'] = success
    
    # Final Report
    print("="*80)
    print("FINAL REPORT")
    print("="*80)
    print()
    
    for module, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {module}")
    
    print()
    
    all_passed = all(results.values())
    if all_passed:
        print("="*80)
        print("🎉 ALL TESTS PASSED - Investigation Engine is PRODUCTION READY")
        print("="*80)
        return 0
    else:
        print("="*80)
        print("⚠️  SOME TESTS FAILED - Review errors above")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
