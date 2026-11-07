from datetime import date
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.knowledge import Knowledge

HEAD = {"x-api-key": "local-demo-key"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("BUILDSIGHT_API_KEY", "local-demo-key")
    monkeypatch.delenv("BUILDSIGHT_OLLAMA_MODEL", raising=False)
    with TestClient(create_app(str(tmp_path / "test.sqlite"))) as c:
        yield c


def test_auth_and_validation(client):
    assert client.post("/ask", json={"question": "deck"}).status_code == 401
    assert client.post("/ask", headers=HEAD, json={"question": ""}).status_code == 422
    assert client.post("/runs", headers=HEAD, json={"question": "deck", "kind": "unsafe"}).status_code == 422


def test_citations_and_abstention(client):
    d = client.post("/ask", headers=HEAD, json={"question": "reinforcing conflict"}).json()
    originals = {d["id"]: d for d in Knowledge().docs}
    assert d["citations"]
    for c in d["citations"]:
        assert c["quote"] == originals[c["document_id"]]["text"]
    assert client.post("/ask", headers=HEAD, json={"question": "quantum cryptocurrency"}).json()["abstained"]


@pytest.mark.parametrize("kind", ["rfi", "schedule", "risk"])
@pytest.mark.parametrize("approve", [True, False])
def test_workflow(client, kind, approve):
    d = client.post("/runs", headers=HEAD, json={"question": "deck pour RFI", "kind": kind}).json()
    assert d["status"] == "awaiting_approval"
    assert "decision" not in d["state"]
    assert d["state"]["findings"][0]["downstream"] == ["ACT-040", "ACT-050"]
    url = f"/runs/{d['id']}/decision"
    assert client.post(url, json={"approve": True, "reason": "test"}).status_code == 401
    decided = client.post(url, headers=HEAD, json={"approve": approve, "reason": "Reviewed fixture"})
    assert decided.json()["status"] == ("approved" if approve else "rejected")
    assert client.post(url, headers=HEAD, json={"approve": approve, "reason": "duplicate"}).status_code == 409


def test_restart(tmp_path, monkeypatch):
    monkeypatch.setenv("BUILDSIGHT_API_KEY", "local-demo-key")
    monkeypatch.delenv("BUILDSIGHT_OLLAMA_MODEL", raising=False)
    p = str(tmp_path / "persist.sqlite")
    with TestClient(create_app(p)) as c:
        rid = c.post("/runs", headers=HEAD, json={"question": "deck", "kind": "rfi"}).json()["id"]
    with TestClient(create_app(p)) as c:
        assert c.get(f"/runs/{rid}", headers=HEAD).json()["status"] == "awaiting_approval"
        assert (
            c.post(f"/runs/{rid}/decision", headers=HEAD, json={"approve": False, "reason": "after restart"}).json()[
                "status"
            ]
            == "rejected"
        )


def test_graph_and_mocks(client):
    assert any(e["relation"] == "blocks" for e in client.get("/graph", headers=HEAD).json()["edges"])
    for vendor in ["procore", "autodesk"]:
        assert client.get(f"/integrations/{vendor}", headers=HEAD).json()["simulated"]
    assert client.get("/runs/missing", headers=HEAD).status_code == 404


def test_risk_rules():
    k = Knowledge()
    assert k.risks(date(2026, 11, 7))[0]["severity"] == "high"
    assert k.risks(date(2026, 10, 1))[0]["severity"] == "medium"
    assert k.risks(date(2026, 11, 12))[0]["overdue"]
    k.data["rfis"][0]["status"] = "closed"
    assert k.risks(date(2026, 11, 7)) == []
