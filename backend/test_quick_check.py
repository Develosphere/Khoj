"""
Quick sanity check test - verifies imports and basic structure without API calls.
"""

print("=" * 80)
print("KHOJ MVP - Quick Import Sanity Check")
print("=" * 80)

# Test 1: Configuration
print("\n[1/6] Testing configuration...")
try:
    from app.core.config import settings
    print(f"    ✓ Config loaded successfully")
    print(f"    ✓ Supabase URL: {settings.SUPABASE_URL[:30]}...")
    print(f"    ✓ Gemini API key: {'SET' if settings.GEMINI_API_KEY else 'NOT SET'}")
except Exception as e:
    print(f"    ✗ Configuration failed: {e}")
    exit(1)

# Test 2: Service imports
print("\n[2/6] Testing service imports...")
try:
    from app.services.source_collector import SourceCollector
    from app.services.evidence_engine import EvidenceEngine
    from app.services.timeline_engine import TimelineEngine
    from app.services.theory_engine import generate_theories
    print("    ✓ All service modules imported successfully")
except Exception as e:
    print(f"    ✗ Service import failed: {e}")
    exit(1)

# Test 3: Schema imports
print("\n[3/6] Testing schema imports...")
try:
    from app.schemas.source import SourceSchema
    from app.schemas.evidence import EvidenceSchema
    from app.schemas.timeline import TimelineEventSchema
    from app.schemas.theory import TheorySchema
    print("    ✓ All schema modules imported successfully")
except Exception as e:
    print(f"    ✗ Schema import failed: {e}")
    exit(1)

# Test 4: API endpoint imports
print("\n[4/6] Testing API endpoint imports...")
try:
    from app.api.v1.endpoints import case, auth, source, dashboard
    print("    ✓ All API endpoints imported successfully")
except Exception as e:
    print(f"    ✗ API endpoint import failed: {e}")
    exit(1)

# Test 5: Main app
print("\n[5/6] Testing main FastAPI app...")
try:
    from app.main import app
    print("    ✓ FastAPI app initialized successfully")
except Exception as e:
    print(f"    ✗ FastAPI app initialization failed: {e}")
    exit(1)

# Test 6: Service instantiation
print("\n[6/6] Testing service instantiation...")
try:
    collector = SourceCollector()
    evidence_engine = EvidenceEngine()
    timeline_engine = TimelineEngine()
    print("    ✓ All services can be instantiated")
except Exception as e:
    print(f"    ✗ Service instantiation failed: {e}")
    exit(1)

print("\n" + "=" * 80)
print("✅ ALL QUICK CHECKS PASSED!")
print("=" * 80)
print("\nBackend is properly configured and ready.")
print("Next step: Test with actual API calls using test_pipeline_integration.py")
print("\nServers status:")
print("  • Backend:  http://localhost:8000 (should be running)")
print("  • Frontend: http://localhost:3000 (should be running)")
print("=" * 80)
