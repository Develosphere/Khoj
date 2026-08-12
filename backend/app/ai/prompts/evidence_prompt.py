"""
Evidence extraction prompt builder.

The EvidenceEngine constructs prompts dynamically in the _build_prompt method.
This file exists for documentation and potential future centralization.

The prompt instructs Gemini to extract factual claims from source content and
output them as a JSON array with the following structure:

[
  {
    "claim": "string factual claim",
    "confidence": 0.0,
    "evidence_type": "eyewitness" | "official_statement" | "media_report" | "forensic" | "unknown",
    "reasoning": "short explanation for the confidence and classification"
  }
]

Rules enforced by the prompt:
- Return ONLY valid JSON (no Markdown, no code fences, no trailing commas)
- Use only double quotes in JSON
- confidence is a float between 0.0 and 1.0
- Choose evidence_type from: eyewitness, official_statement, media_report, forensic, unknown
- If there are no clear factual claims, return an empty JSON array: []
- Focus on verifiable facts, not opinions

The prompt is built inline in EvidenceEngine._build_prompt() method.
"""
