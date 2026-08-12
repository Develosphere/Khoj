2024-06-09 12:45 PKT — Source Collection Engine (Module 3.1) implemented
- Modular async service for web source collection
- Type-safe Source model/schema
- Deduplication, normalization, filtering logic
- FastAPI endpoint under /api/v1/investigations/sources
2024-06-09 13:20 PKT — Evidence Extraction Engine (Module 3.2) implemented
- Modular async service for extracting structured evidence from sources
- Type-safe Evidence model/schema (claim, source, confidence, evidence_type, reasoning)
- Gemini Flash Lite integration via isolated `GeminiClient` service
- Deduplication of claims across sources, categorization into evidence types, and strict Pydantic validation
- Defensive handling of malformed AI output (JSON parsing + schema validation errors are logged and safely ignored)

2024-06-09 14:00 PKT — Timeline Engine (Module 3.3) implemented
- Modular service generates timeline events from evidence objects
- Type-safe TimelineEvent model/schema (time, event, confidence, supporting_evidence)
- Merges duplicate events, preserves supporting evidence references, chronological ordering, robust validation
- FastAPI endpoint under /api/v1/investigations/timeline/generate

2024-06-09 14:40 PKT — Theory Engine (Module 3.4) implemented
- Modular async service generates at least 3 competing theories from evidence and timeline events
- Type-safe Theory model/schema (theory, confidence, supporting_evidence, timeline_events, summary)
- Deduplication, strict validation, robust error handling, Gemini Flash Lite integration
- FastAPI endpoint under /api/v1/investigations/theories/generate

2024-06-09 14:00 PKT — Timeline Engine (Module 3.3) implemented
- Modular service generates timeline events from evidence objects
- Type-safe TimelineEvent model/schema (time, event, confidence, supporting_evidence)
- Merges duplicate events, preserves supporting evidence references, chronological ordering, robust validation
- FastAPI endpoint under /api/v1/investigations/timeline/generate

2024-06-09 14:40 PKT — Theory Engine (Module 3.4) implemented
- Modular async service generates at least 3 competing theories from evidence and timeline events
- Type-safe Theory model/schema (theory, confidence, supporting_evidence, timeline_events, summary)
- Deduplication, strict validation, robust error handling, Gemini Flash Lite integration
- FastAPI endpoint under /api/v1/investigations/theories/generate


Summary Engine (Module 3.5) implemented
- Added Summary domain model (`backend/app/models/summary.py`) and API schema (`backend/app/schemas/summary.py`).
- Implemented async `generate_summary` service in `backend/app/services/summary_engine.py` using Gemini Flash Lite and a dedicated prompt in `backend/app/ai/prompts/summary_prompt.py`.
- Enforced structured JSON output with Pydantic validation and defensive parsing of AI responses.
- Exposed authenticated FastAPI endpoint `POST /api/v1/investigations/summary/generate` returning:
  {
    "summary": "",
    "key_findings": [],
    "top_theory": "",
    "confidence": 0
  }

2024-08-12 23:45 PKT — Phase 3 Investigation Engine COMPLETE

**Module 3.1 - Source Collection**
- DuckDuckGo news provider with async HTTP requests
- URL deduplication and content filtering
- GET /api/v1/investigations/sources endpoint

**Module 3.2 - Evidence Extraction** 
- Real Gemini 2.0 Flash Lite API integration implemented
- Async evidence extraction with retry logic and timeout handling
- Pydantic validation of all AI outputs
- Defensive parsing of malformed responses
- Claim deduplication across sources

**Module 3.3 - Timeline Engine**
- AI-powered timeline event extraction from evidence
- Fallback regex-based extraction for temporal information
- Chronological sorting with multiple date format support
- Event deduplication and confidence aggregation
- POST /api/v1/investigations/timeline/generate endpoint

**Module 3.4 - Theory Engine**
- Gemini-powered generation of ≥3 competing theories
- Theory deduplication by normalized text
- Validation requiring minimum 3 theories
- Supporting evidence and timeline event references
- POST /api/v1/investigations/theories/generate endpoint

**Module 3.5 - Summary Engine**
- Generates investigation summary from all pipeline outputs
- Produces key findings list and top theory identification
- Confidence scoring for theories
- POST /api/v1/investigations/summary/generate endpoint

**Module 3.6 - Investigation Orchestrator**
- Unified pipeline: sources → evidence → timeline → theories → summary
- Graceful error handling with partial results
- Authenticated user tracking in logs
- POST /api/v1/investigations/run endpoint

**Infrastructure Improvements**
- Added GEMINI_API_KEY and OPENROUTER_API_KEY to environment config
- Implemented OpenRouterClient as fallback AI provider
- Created timeline_prompt.py for AI-based timeline extraction
- All 27 Investigation Engine files validated for syntax correctness
- Complete async/await consistency across all services
