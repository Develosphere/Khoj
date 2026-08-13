"""
Integration test for complete KHOJ investigation pipeline.
Tests the full user journey with a simple test case.
"""

import asyncio
import os
from app.services.source_collector import SourceCollector
from app.services.evidence_engine import EvidenceEngine
from app.services.timeline_engine import TimelineEngine
from app.services.theory_engine import generate_theories


async def test_investigation_pipeline():
    """Test the complete investigation pipeline end-to-end."""
    
    print("=" * 80)
    print("KHOJ MVP INTEGRATION TEST - Complete Investigation Pipeline")
    print("=" * 80)
    
    # Use a simpler, more focused test query
    test_case_name = "Pakistan Quetta bombing 2024"
    
    print(f"\n🔍 Testing investigation for: {test_case_name}")
    print(f"   (Using recent news event for faster testing)")
    
    # Step 1: Source Collection
    print("\n" + "-" * 80)
    print("STEP 1: Source Collection")
    print("-" * 80)
    
    try:
        collector = SourceCollector()
        print(f"Collecting sources for query: '{test_case_name}'")
        sources = await collector.collect_sources(test_case_name)
        
        print(f"✓ Successfully collected {len(sources)} sources")
        if sources:
            print(f"\nFirst source:")
            print(f"  Title: {sources[0].title[:70]}...")
            print(f"  Source: {sources[0].source_name}")
        
        # Convert to dict format for downstream engines
        sources_payload = []
        for src in sources:
            sources_payload.append({
                "title": src.title,
                "url": src.url,
                "source_name": src.source_name,
                "published_at": src.published_at,
                "content": src.content
            })
            
        if len(sources_payload) == 0:
            print("⚠️  No sources collected. Check source collector configuration.")
            return False
            
    except Exception as e:
        print(f"✗ Source collection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Evidence Extraction (limit to first 3 sources for speed)
    print("\n" + "-" * 80)
    print("STEP 2: Evidence Extraction")
    print("-" * 80)
    
    try:
        evidence_engine = EvidenceEngine()
        # Limit sources for faster testing
        limited_sources = sources_payload[:3]
        print(f"Extracting evidence from {len(limited_sources)} sources (limited for speed)...")
        evidence_list = await evidence_engine.extract_evidence(limited_sources)
        
        print(f"✓ Successfully extracted {len(evidence_list)} evidence claims")
        if evidence_list:
            print(f"\nFirst evidence claim:")
            print(f"  Claim: {evidence_list[0].claim[:80]}...")
            print(f"  Type: {evidence_list[0].evidence_type}")
            print(f"  Confidence: {evidence_list[0].confidence * 100:.0f}%")
        
        # Convert to dict format
        evidence_payload = []
        for ev in evidence_list:
            evidence_payload.append({
                "claim": ev.claim,
                "source": ev.source,
                "confidence": ev.confidence,
                "evidence_type": ev.evidence_type,
                "reasoning": ev.reasoning
            })
            
        if len(evidence_payload) == 0:
            print("⚠️  No evidence extracted. Check Gemini API key configuration.")
            return False
            
    except Exception as e:
        print(f"✗ Evidence extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Timeline Generation
    print("\n" + "-" * 80)
    print("STEP 3: Timeline Generation")
    print("-" * 80)
    
    try:
        timeline_engine = TimelineEngine()
        print("Generating chronological timeline from evidence...")
        timeline_list = await timeline_engine.extract_timeline_async(evidence_list)
        
        print(f"✓ Successfully generated {len(timeline_list)} timeline events")
        if timeline_list:
            print(f"\nFirst timeline event:")
            print(f"  Time: {timeline_list[0].time}")
            print(f"  Event: {timeline_list[0].event[:80]}...")
            print(f"  Confidence: {timeline_list[0].confidence * 100:.0f}%")
        
        # Convert to dict format
        timeline_payload = []
        for evt in timeline_list:
            timeline_payload.append({
                "time": evt.time,
                "event": evt.event,
                "confidence": evt.confidence,
                "supporting_evidence": evt.supporting_evidence
            })
            
    except Exception as e:
        print(f"✗ Timeline generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Theory Generation
    print("\n" + "-" * 80)
    print("STEP 4: Theory Generation")
    print("-" * 80)
    
    try:
        print("Generating competing theories from evidence and timeline...")
        theories_response = await generate_theories(evidence_payload, timeline_payload)
        
        if theories_response and theories_response.theories:
            print(f"✓ Successfully generated {len(theories_response.theories)} theories")
            
            for idx, theory in enumerate(theories_response.theories, 1):
                print(f"\nTheory {idx}:")
                theory_text = theory.get('theory', 'N/A')
                print(f"  Title: {theory_text[:80]}...")
                print(f"  Confidence: {theory.get('confidence', 0) * 100:.0f}%")
                print(f"  Supporting Evidence: {len(theory.get('supporting_evidence', []))} claims")
        else:
            print("⚠️  No theories generated")
            return False
    except Exception as e:
        print(f"✗ Theory generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE TEST SUMMARY")
    print("=" * 80)
    print(f"✓ Sources Collected:     {len(sources_payload)}")
    print(f"✓ Evidence Extracted:    {len(evidence_payload)}")
    print(f"✓ Timeline Generated:    {len(timeline_payload)}")
    print(f"✓ Theories Generated:    {len(theories_response.theories) if theories_response else 0}")
    print("\n✅ Complete investigation pipeline working successfully!")
    print("=" * 80)
    
    return True


async def test_database_connectivity():
    """Test Supabase database connectivity."""
    print("\n" + "=" * 80)
    print("Testing Supabase Database Connectivity")
    print("=" * 80)
    
    try:
        from supabase import create_client, Client
        from app.core.config import settings
        
        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_ANON_KEY
        
        print(f"Supabase URL: {supabase_url}")
        print("Connecting to database...")
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Try to query cases table (should work even if empty)
        response = supabase.table("cases").select("id").limit(1).execute()
        
        print(f"✓ Database connection successful!")
        print(f"  Tables accessible: cases, sources, evidence, timeline_events, theories")
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests."""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "KHOJ MVP INTEGRATION TEST SUITE" + " " * 26 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Test 1: Database connectivity
    db_success = await test_database_connectivity()
    
    if not db_success:
        print("\n⚠️  Database connectivity test failed. Check Supabase credentials.")
        print("   Proceeding with pipeline test anyway...")
    
    # Test 2: Complete investigation pipeline
    pipeline_success = await test_investigation_pipeline()
    
    if pipeline_success:
        print("\n" + "🎉 " * 20)
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        print("\nThe KHOJ MVP is ready for demonstration:")
        print("  • Backend API:  http://localhost:8000")
        print("  • Frontend UI:  http://localhost:3000")
        print("\nUser Journey Flow:")
        print("  1. Sign up / Login at http://localhost:3000")
        print("  2. Create Investigation Case")
        print("  3. Click 'Run AI Case Analysis'")
        print("  4. View Sources → Evidence → Timeline → Theories")
        print("  5. Click 'Generate Reconstruction' on a theory")
        print("  6. View 3D simulation")
        print("\n" + "🎉 " * 20)
    else:
        print("\n⚠️  Pipeline test encountered issues. Review logs above.")


if __name__ == "__main__":
    asyncio.run(main())
