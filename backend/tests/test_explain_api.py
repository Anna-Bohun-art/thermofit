from fastapi.testclient import TestClient

from app import main
from app.rag import llm

client = TestClient(main.app)
BODY = {"fit_result": {"model": "two_state", "params": []}, "question": "Was ist Tm?"}


def test_explain_ok(monkeypatch):
    monkeypatch.setattr(main.service, "explain", lambda f, q: {"answer": "x", "sources": []})
    r = client.post("/api/explain", json=BODY)
    assert r.status_code == 200 and r.json()["answer"] == "x"


def test_explain_question_too_long():
    r = client.post("/api/explain", json={**BODY, "question": "a" * 301})
    assert r.status_code == 422


def test_explain_not_set_up():
    # no index.npz yet -> 503, not 500
    assert client.post("/api/explain", json=BODY).status_code == 503


def test_explain_llm_error(monkeypatch):
    def boom(f, q):
        raise llm.LLMError("down")
    monkeypatch.setattr(main.service, "explain", boom)
    assert client.post("/api/explain", json=BODY).status_code == 502
