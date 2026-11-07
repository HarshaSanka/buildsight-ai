"""Exercise the running HTTP service (also used against the CI container)."""

import json
import os
from urllib.request import Request, urlopen

base = os.getenv("BUILDSIGHT_SMOKE_URL", "http://127.0.0.1:8000")


def request(path, body=None):
    req = Request(
        base + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", "x-api-key": os.getenv("BUILDSIGHT_API_KEY", "local-demo-key")},
    )
    with urlopen(req, timeout=15) as response:
        return json.load(response)


assert request("/health")["status"] == "ok"
answer = request("/ask", {"question": "reinforcing drainage conflict"})
assert any(c["document_id"] == "RFI-014" for c in answer["citations"])
run = request("/runs", {"question": "deck pour", "kind": "schedule"})
assert run["status"] == "awaiting_approval"
assert run["state"]["findings"][0]["severity"] == "high"
final = request(f"/runs/{run['id']}/decision", {"approve": False, "reason": "HTTP smoke test: synthetic review"})
assert final["status"] == "rejected"
assert request("/integrations/procore")["simulated"]
print("HTTP smoke passed: health, citations, pending review, risk finding, rejection, simulated integration")
