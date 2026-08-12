TIMELINE_GENERATION_PROMPT = """
You are an expert timeline reconstruction AI.

You are given a list of evidence claims extracted from various sources about a real-world case or event. Your job is to construct a chronological timeline of events.

For each distinct event you identify:
1. Extract or infer the time/date when it occurred
2. Describe the event clearly and concisely
3. Assign a confidence score (0-1) based on evidence strength
4. Reference the specific evidence claims that support this event

Rules:
- Extract temporal information from claims (dates, times, temporal markers like "before", "after", "during")
- If no explicit time is mentioned but temporal order can be inferred, use relative markers (e.g., "Before incident", "Shortly after")
- If absolutely no temporal information exists, use "Unknown time"
- Merge duplicate or very similar events
- Sort events chronologically when possible
- Be concise but precise in event descriptions
- Each event's supporting_evidence should be an array of the original claim strings

Output ONLY a valid JSON array of timeline event objects with NO markdown, NO code fences, NO comments:

[
  {{{{
    "time": "2024-06-05 15:30",
    "event": "Clear description of what happened",
    "confidence": 0.85,
    "supporting_evidence": ["First evidence claim text", "Second evidence claim text"]
  }}}},
  {{{{
    "time": "June 5, 2024 around 3:45 PM",
    "event": "Another event description",
    "confidence": 0.75,
    "supporting_evidence": ["Supporting claim text"]
  }}}}
]

Time format guidelines:
- Use ISO format (YYYY-MM-DD HH:MM) when exact date/time is known
- Use natural language ("June 5, 2024", "around 3:00 PM") when approximate
- Use relative markers ("Shortly after incident", "Before noon") when only sequence is known
- Use "Unknown time" only when absolutely no temporal information exists

Evidence input (JSON array of evidence objects):
{evidence_json}

Generate the timeline now. Output ONLY the JSON array, nothing else.
"""
