# Investigation Engine - Technical Documentation

## Overview

The Investigation Engine is a complete AI-powered pipeline that transforms a case name into a structured investigation with sources, evidence, timeline, theories, and summary.

## Architecture

```
Case Name Input
      ↓
Source Collection (DuckDuckGo)
      ↓
Evidence Extraction (Gemini AI)
      ↓
Timeline Generation (Gemini AI + Regex Fallback)
      ↓
Theory Generation (Gemini AI)
      ↓
Summary Generation (Gemini AI)
      ↓
Unified Investigation Object
```

## Pipeline Stages

### 1. Source Collection

**Service:** `source_collector.py`  
**Model:** `Source`  
**Schema:** `SourceSchema`  
**Endpoint:** `GET /api/v1/investigations/sources?case_name={name}`

**Input:**
- `case_name` (string): Name of the case to investigate

**Output:**
```json
{
  "sources": [
    {
      "title": "Article title",
      "url": "https://...",
      "source_name": "domain.com",
      "published_at": "2024-01-01T00:00:00Z",
      "content": "Article content..."
    }
  ]
}
```

**Features:**
- Async web scraping via DuckDuckGo News API
- URL deduplication
- Content filtering (removes empty sources)
- Provider-based architecture (extensible to other sources)

**Target:** Collect 10+ sources when available

---

### 2. Evidence Extraction

**Service:** `evidence_engine.py`  
**Model:** `Evidence`  
**Schema:** `EvidenceSchema`  
**AI Provider:** Gemini 2.0 Flash Lite

**Input:** List of source objects

**Output:**
```json
{
  "evidence": [
    {
      "claim": "Factual claim extracted from source",
      "source": "https://source-url.com",
      "confidence": 0.85,
      "evidence_type": "media_report",
      "reasoning": "Why this classification and confidence"
    }
  ]
}
```

**Evidence Types:**
- `eyewitness` - Direct witness accounts
- `official_statement` - Government/official declarations
- `media_report` - News reporting
- `forensic` - Scientific/technical analysis
- `unknown` - Cannot be categorized

**Features:**
- Async parallel processing of sources
- Gemini AI prompt engineering for claim extraction
- Claim deduplication (normalized text matching)
- Pydantic validation of all AI outputs
- Defensive error handling (malformed AI responses logged, never crash)
- Per-source timeout and retry logic

**Prompt Strategy:**
- Instructs model to return ONLY valid JSON
- Enforces confidence range (0.0 - 1.0)
- Requires evidence type categorization
- Demands reasoning/justification
- Truncates very long content to 4000 chars

---

### 3. Timeline Generation

**Service:** `timeline_engine.py`  
**Model:** `TimelineEvent`  
**Schema:** `TimelineEventSchema`  
**Endpoint:** `POST /api/v1/investigations/timeline/generate`  
**AI Provider:** Gemini 2.0 Flash Lite (with regex fallback)

**Input:** List of evidence objects

**Output:**
```json
{
  "timeline": [
    {
      "time": "2024-06-05 15:30",
      "event": "Description of what happened",
      "confidence": 0.85,
      "supporting_evidence": ["claim 1", "claim 2"]
    }
  ]
}
```

**Features:**
- AI-powered temporal extraction from evidence claims
- Multiple date format support:
  - ISO format: `2024-06-05 15:30`
  - Natural language: `June 5, 2024 around 3:30 PM`
  - Relative: `Shortly after incident`, `Before noon`
  - Unknown: `Unknown time` (when no temporal info exists)
- Event deduplication by normalized time + description
- Chronological sorting with intelligent date parsing
- Fallback regex-based extraction when AI fails
- Confidence aggregation (max confidence across merged events)
- Supporting evidence accumulation

**Temporal Extraction Patterns (Fallback):**
```regex
on|at|in|during + [Month Day, Year]
at + [HH:MM AM/PM]
YYYY-MM-DD
MM/DD/YYYY
Month DD, YYYY
```

**Sorting Logic:**
1. ISO dates (YYYY-MM-DD) - precise chronological
2. Dates with year - rough chronological by year
3. "Unknown time" - sorted to end
4. Everything else - lexicographic

---

### 4. Theory Generation

**Service:** `theory_engine.py`  
**Model:** `Theory`  
**Schema:** `TheorySchema`  
**Endpoint:** `POST /api/v1/investigations/theories/generate`  
**AI Provider:** Gemini 2.0 Flash Lite

**Input:** 
- Evidence objects (list)
- Timeline events (list)

**Output:**
```json
{
  "theories": [
    {
      "theory": "Hypothesis explaining the evidence",
      "confidence": 0.75,
      "supporting_evidence": ["claim1", "claim2"],
      "timeline_events": ["event1", "event2"],
      "summary": "1-2 sentence justification"
    }
  ]
}
```

**Requirements:**
- Minimum 3 valid theories
- Each theory must have confidence score (0.0 - 1.0)
- Each theory references supporting evidence and timeline events
- Theories must be distinct (deduplication by normalized text)

**Features:**
- Higher temperature (0.8) for creative hypothesis generation
- Theory deduplication
- Strict validation (returns empty if <3 theories)
- JSON-only output enforcement
- Handles malformed AI responses gracefully

**Endpoint Behavior:**
- Returns `422 Unprocessable Entity` if <3 valid theories generated
- Logs all validation failures with details

---

### 5. Summary Generation

**Service:** `summary_engine.py`  
**Model:** `Summary`  
**Schema:** `SummarySchema`  
**Endpoint:** `POST /api/v1/investigations/summary/generate`  
**AI Provider:** Gemini 2.0 Flash Lite

**Input:**
- Evidence objects (list)
- Timeline events (list)
- Theory objects (list)

**Output:**
```json
{
  "summary": "3-6 sentence overview of the case",
  "key_findings": [
    "Important finding 1",
    "Important finding 2",
    "Important finding 3"
  ],
  "top_theory": "Description of strongest theory",
  "confidence": 0.80
}
```

**Features:**
- Synthesizes all pipeline outputs
- Produces natural language case summary
- Extracts key findings as bullet points
- Identifies strongest theory with confidence
- Defensive parsing (handles malformed key_findings)
- Returns `422` on generation failure

**Summary Guidelines:**
- Condenses complex investigation into digestible format
- Never claims absolute certainty
- Highlights most important evidence/timeline insights
- Explains why top theory is best-supported

---

### 6. Investigation Orchestrator

**Service:** `investigation_orchestrator.py`  
**Endpoint:** `POST /api/v1/investigations/run`

**Input:**
```json
{
  "case_name": "JFK Assassination Investigation"
}
```

**Output:**
```json
{
  "case_name": "JFK Assassination Investigation",
  "sources": [...],
  "evidence": [...],
  "timeline": [...],
  "theories": [...],
  "summary": {...}
}
```

**Features:**
- Executes full pipeline sequentially
- Graceful error handling:
  - Logs all failures with user_id when authenticated
  - Returns partial results up to failure point
  - Downstream stages receive empty inputs if upstream fails
- User tracking in logs
- Authenticated endpoint (requires Supabase JWT)

**Failure Behavior:**
```
Source collection fails → returns empty investigation
Evidence extraction fails → returns sources only
Timeline generation fails → returns sources + evidence
Theory generation fails → returns sources + evidence + timeline
Summary generation fails → returns all except summary
```

---

## Error Handling Strategy

### Defensive Programming
Every stage is designed to NEVER crash the server:

1. **AI Response Parsing:**
   - Strip markdown code fences
   - Validate JSON structure
   - Log malformed responses (truncated to 500 chars)
   - Return empty results on parse failure

2. **Validation:**
   - Pydantic validation on all outputs
   - Log validation errors with full context
   - Skip invalid items, continue processing valid ones

3. **Provider Failures:**
   - Retry logic with exponential backoff (3 attempts)
   - Timeout protection (30s default)
   - Clear error messages in logs
   - Graceful degradation

4. **Empty Results:**
   - Every stage handles empty input safely
   - Minimum requirements enforced (e.g., 3 theories)
   - Clear HTTP status codes:
     - `200 OK` - Success
     - `400 Bad Request` - Client error
     - `422 Unprocessable Entity` - Validation failure
     - `500 Internal Server Error` - Server error (avoided via defensive coding)

---

## Configuration

### Environment Variables

```env
GEMINI_API_KEY=your-key-here              # Required for all AI stages
OPENROUTER_API_KEY=your-key-here          # Optional fallback
SUPABASE_URL=https://....supabase.co      # Required for auth
SUPABASE_ANON_KEY=your-key-here           # Required for auth
BACKEND_CORS_ORIGINS=http://localhost:3000  # CORS config
```

### AI Client Configuration

```python
# Gemini Client
GeminiClient(
    api_key="...",
    timeout=30,          # seconds
    max_retries=3
)

# OpenRouter Client (Fallback)
OpenRouterClient(
    api_key="...",
    model="openai/gpt-3.5-turbo",
    timeout=30,
    max_retries=3
)
```

---

## Testing

### Syntax Validation
```bash
cd backend
python validate_imports.py
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Full investigation (requires auth token)
curl -X POST http://localhost:8000/api/v1/investigations/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_name": "Test Case"}'
```

### Unit Tests (Future)
```bash
pytest backend/tests/
```

---

## Performance Characteristics

### Latency (estimated)
- Source Collection: 3-5 seconds
- Evidence Extraction: 10-20 seconds (depends on source count)
- Timeline Generation: 5-10 seconds
- Theory Generation: 10-15 seconds
- Summary Generation: 5-10 seconds
- **Total Pipeline: 35-60 seconds**

### Rate Limits
- Gemini API: 60 requests/minute (free tier)
- Consider caching investigation results

### Scalability
- All services are stateless
- Async processing allows concurrent requests
- DuckDuckGo provider has no auth (public scraping)

---

## Known Limitations

1. **Source Coverage:**
   - Currently limited to DuckDuckGo News results
   - No access to paywalled content
   - English-language sources only

2. **AI Output Quality:**
   - Gemini may produce incomplete/incorrect claims
   - Timeline extraction depends on explicit temporal markers
   - Theory generation quality varies by case complexity

3. **Deduplication:**
   - Text-based (may miss semantic duplicates)
   - Case-insensitive but not fuzzy matching

4. **Temporal Extraction:**
   - Fallback regex patterns limited to common formats
   - Relative time references ("yesterday", "last week") not handled

5. **No Persistence:**
   - Investigation results not stored in database yet
   - Each run regenerates from scratch

---

## Future Improvements

1. **Source Providers:**
   - Google News API
   - Reddit/Twitter scraping
   - Academic paper databases

2. **AI Enhancements:**
   - Multi-model ensemble (Gemini + Claude + GPT)
   - Fine-tuned models for evidence classification
   - Confidence calibration

3. **Timeline:**
   - Fuzzy temporal resolution ("early morning" → time range)
   - Dependency graph (event X must precede Y)
   - Conflict detection (contradictory timestamps)

4. **Caching:**
   - Store investigation results in Supabase
   - Cache AI responses to reduce API costs
   - Incremental updates (add new sources without reprocessing)

5. **Validation:**
   - Cross-reference claims across sources
   - Fact-checking integration
   - Source credibility scoring

---

## API Examples

### Source Collection
```bash
curl "http://localhost:8000/api/v1/investigations/sources?case_name=Watergate" \
  -H "Authorization: Bearer TOKEN"
```

### Timeline Generation
```bash
curl -X POST "http://localhost:8000/api/v1/investigations/timeline/generate" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "claim": "Break-in occurred at 2:30 AM",
      "source": "https://example.com",
      "confidence": 0.9,
      "evidence_type": "official_statement",
      "reasoning": "Police report"
    }
  ]'
```

### Full Pipeline
```bash
curl -X POST "http://localhost:8000/api/v1/investigations/run" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_name": "Watergate Scandal"}'
```

---

## Code Quality Metrics

✅ All 27 Investigation Engine files validated for Python syntax  
✅ Async/await consistency across all services  
✅ Pydantic validation on all inputs/outputs  
✅ Type hints throughout codebase  
✅ Comprehensive error logging  
✅ No hardcoded credentials  
✅ Provider abstraction for extensibility  

---

## Maintenance Notes

- Update `timeline_prompt.py` if temporal extraction patterns change
- Update `theory_prompt.py` if theory generation requirements change
- Monitor Gemini API rate limits in production
- Consider retry budget if API costs spike
- Rotate API keys regularly

---

**Last Updated:** 2024-08-12 PKT  
**Status:** Phase 3 Complete ✅
