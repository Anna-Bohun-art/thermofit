"""RAG core -- written by Anna (chunking, retrieval, prompt). Stubs with the contract.

Each function has a test skeleton in tests/test_rag_core.py (currently xfail).
Remove the xfail marker as you implement them.
"""
from __future__ import annotations

import numpy as np

NO_BASIS = "Dazu habe ich keine Grundlage in meiner Wissensbasis."


def chunk_markdown(text: str, source: str, max_chars: int = 1800) -> list[dict]:
    """Split one markdown file into chunks (~300-500 tokens).

    Return [{"id": f"{source}#{n}", "source": source, "heading": str, "text": str}, ...].
    Idea: split at '#'/'##' headings, keep the heading as metadata, split overly long
    sections at paragraph boundaries.
    """
    raise NotImplementedError


def top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int = 4) -> list[tuple[int, float]]:
    """Cosine similarity of query_vec (dim,) against matrix (n, dim).

    Return [(row_index, score), ...] sorted by score, best first, at most k.
    """
    # Step 1: dot product of every chunk row with the question -> one number per chunk
    dots = matrix @ query_vec
    # Step 2: divide by the lengths, so only the direction counts (cosine similarity)
    row_lengths = np.linalg.norm(matrix, axis=1)
    query_length = np.linalg.norm(query_vec)
    scores = dots / (row_lengths * query_length)
    # Step 3: positions sorted from worst to best, reverse them, keep the first k
    best = np.argsort(scores)[::-1][:k]
    # Step 4: list of (position, score) tuples as normal Python numbers
    return [(int(i), float(scores[i])) for i in best]


def build_prompt(fit_result: dict, question: str, chunks: list[dict]) -> tuple[str, str]:
    """Return (system, user) for the LLM.

    Rules for the system prompt (see PLAN_RAG.md): numbers only from fit_result,
    rely only on the sources, cite chunk ids, otherwise answer NO_BASIS.
    Fit result goes in directly (no retrieval); chunks are listed with their ids.
    """
    raise NotImplementedError
