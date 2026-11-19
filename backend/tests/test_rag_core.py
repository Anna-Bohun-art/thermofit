"""Test skeletons for Anna's RAG core. Remove xfail as each function is implemented."""
import numpy as np
from app.rag import core

def test_chunk_keeps_heading_and_ids():
    chunks = core.chunk_markdown("# A\ntext one\n\n## B\ntext two\n", "doc")
    assert [c["heading"] for c in chunks] == ["A", "B"]
    assert chunks[0]["id"] == "doc#0"


def test_top_k_orders_by_cosine():
    m = np.array([[1, 0], [0, 1], [1, 1]], dtype=np.float32)
    hits = core.top_k(np.array([1, 0.1], dtype=np.float32), m, k=2)
    assert [i for i, _ in hits] == [0, 2]


def test_prompt_contains_numbers_sources_and_rules():
    fit = {"model": "two_state", "params": [{"name": "Tm", "value": 61.2, "unit": "degC"}]}
    chunks = [{"id": "doc#0", "heading": "A", "text": "Two-state model ..."}]
    system, user = core.build_prompt(fit, "Was bedeutet Tm?", chunks)
    assert "61.2" in user and "doc#0" in user and "Was bedeutet Tm?" in user
    assert core.NO_BASIS in system
