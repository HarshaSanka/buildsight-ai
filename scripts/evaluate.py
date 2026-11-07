"""Tiny hand-authored retrieval regression set; not a field accuracy benchmark."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.knowledge import Knowledge

cases = [
    ("reinforcing drainage conflict", "RFI-014"),
    ("concrete placement mix design", "SPEC-0330"),
    ("curing barrier schedule", "PLAN-001"),
    ("field leadership safety", "SAFETY-001"),
    ("approved mix submittal", "SUB-008"),
]
k = Knowledge()
hits = sum(expected in [d["id"] for d in k.search(q)] for q, expected in cases)
quotes = [c for q, _ in cases for c in k.answer(q)["citations"]]
faithful = all(any(c["document_id"] == d["id"] and c["quote"] == d["text"] for d in k.docs) for c in quotes)
print(
    json.dumps(
        {
            "cases": len(cases),
            "recall_at_3": hits / len(cases),
            "exact_quote_integrity": faithful,
            "scope": "synthetic fixture regression only",
        },
        indent=2,
    )
)
assert hits == len(cases) and faithful
