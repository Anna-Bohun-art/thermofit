"""Glue: question + fit result -> answer + sources. Uses Anna's core functions."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import core, llm

RAG_DIR = Path(__file__).parent


@lru_cache(maxsize=1)
def _index() -> tuple[np.ndarray, list[dict]]:
    matrix = np.load(RAG_DIR / "index.npz")["embeddings"]
    chunks = json.loads((RAG_DIR / "chunks.json").read_text(encoding="utf-8"))
    return matrix, chunks


def explain(fit_result: dict, question: str, k: int = 4) -> dict:
    matrix, chunks = _index()
    qvec = llm.embed([question])[0]
    hits = core.top_k(qvec, matrix, k)
    used = [chunks[i] for i, _ in hits]
    system, user = core.build_prompt(fit_result, question, used)
    answer = llm.chat(system, user)
    return {"answer": answer, "sources": [{"id": c["id"], "heading": c["heading"], "text": c["text"]} for c in used]}
