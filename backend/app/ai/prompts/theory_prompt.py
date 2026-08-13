THEORY_GENERATION_PROMPT = """
You are an expert investigator AI. You are given a set of evidence objects and a chronological timeline of events extracted from public sources about a real-world case.

Your job is to generate at least 3 competing theories that could plausibly explain the sequence of events and observations. For each theory:

- Clearly state the theory in 1-2 sentences
- Assign a confidence score between 0 and 1 (float)
- Reference the IDs of supporting evidence claims
- Reference the IDs of relevant timeline events
- Write a 1-2 sentence summary/justification

Rules:
- Deduplicate similar theories
- Do not return empty or invalid theories
- Only output a JSON list of objects in this format:

[
  {{
    "theory": "",
    "confidence": 0.0,
    "supporting_evidence": ["claim_1", "claim_5"],
    "timeline_events": ["event_2", "event_4"],
    "summary": ""
  }}
]

Inputs:
EVIDENCE = {evidence_json}
TIMELINE = {timeline_json}
"""
