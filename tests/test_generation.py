import json
from io import BytesIO
from app.knowledge import Knowledge


def test_optional_model_validated(monkeypatch):
    monkeypatch.setenv("BUILDSIGHT_OLLAMA_MODEL", "test-model")
    k = Knowledge()
    doc = k.extract("reinforcing conflict")["citations"][0]
    claim = {"text": "Review the reinforcing conflict.", "document_id": doc["document_id"], "quote": doc["quote"]}
    body = json.dumps({"message": {"content": json.dumps({"claims": [claim]})}}).encode()
    monkeypatch.setattr("app.generation.urlopen", lambda *a, **kw: BytesIO(body))
    answer = k.answer("reinforcing conflict")
    assert answer["mode"] == "ollama"
    assert answer["citations"][0]["quote"] == doc["quote"]


def test_optional_model_invalid_quote_falls_back(monkeypatch):
    monkeypatch.setenv("BUILDSIGHT_OLLAMA_MODEL", "test-model")
    claim = {"text": "Release the pour.", "document_id": "RFI-014", "quote": "Made up engineering approval"}
    body = json.dumps({"message": {"content": json.dumps({"claims": [claim]})}}).encode()
    monkeypatch.setattr("app.generation.urlopen", lambda *a, **kw: BytesIO(body))
    answer = Knowledge().answer("reinforcing conflict")
    assert answer["mode"] == "extractive_tfidf"
    assert "generation_fallback" in answer


def test_optional_model_timeout_falls_back(monkeypatch):
    monkeypatch.setenv("BUILDSIGHT_OLLAMA_MODEL", "test-model")

    def unavailable(*args, **kwargs):
        raise TimeoutError()

    monkeypatch.setattr("app.generation.urlopen", unavailable)
    assert "generation_fallback" in Knowledge().answer("deck pour")
