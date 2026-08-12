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

