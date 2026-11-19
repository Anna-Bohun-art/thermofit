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
    chunks = []      # the finished chunks (our result)
    heading = ""     # the heading we are currently under
    buffer = []      # lines of the current section, collected so far

    def flush():
        """Turn the collected lines into chunk(s) and empty the buffer."""
        body = "\n".join(buffer).strip()   # glue the lines together again
        buffer.clear()
        if not body:                       # nothing collected -> nothing to do
            return
        for piece in _split_long(body, max_chars):
            chunks.append({
                "id": f"{source}#{len(chunks)}",   # number = how many chunks exist so far
                "source": source,
                "heading": heading,
                "text": piece,
            })

    for line in text.splitlines():
        if line.startswith("#"):
            flush()                          # close the previous section first
            heading = line.lstrip("#").strip()   # "## B" -> "B"
        else:
            buffer.append(line)
    flush()                                  # don't forget the last section
    return chunks


def _split_long(body: str, max_chars: int) -> list[str]:
    """Split a long text at blank lines so that each piece is <= max_chars."""
    pieces = []
    current = ""
    for paragraph in body.split("\n\n"):
        if current and len(current) + len(paragraph) + 2 > max_chars:
            pieces.append(current)       # current piece is full -> store it
            current = paragraph          # start a new piece
        elif current:
            current = current + "\n\n" + paragraph   # still fits -> append
        else:
            current = paragraph          # first paragraph of a piece
    pieces.append(current)
    return pieces


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
    system = (
        "Du erklärst die Ergebnisse einer thermischen Entfaltungskurve (Thermofit).\n"
        "Regeln:\n"
        "1. Zahlen nimmst du ausschließlich aus dem FIT-ERGEBNIS. Erfinde keine Werte.\n"
        "2. Erkläre nur mit Hilfe der QUELLEN. Kein Wissen von außerhalb.\n"
        "3. Nenne nach jeder Aussage die Quelle in eckigen Klammern, z. B. [doc#0].\n"
        f'4. Wenn die Quellen die Frage nicht abdecken, antworte genau: "{NO_BASIS}"'
    )

    # one line per parameter: "- Tm = 61.2 degC"
    param_lines = [
        f"- {p['name']} = {p['value']} {p['unit']}" for p in fit_result["params"]
    ]
    # one block per chunk: "[doc#0] (A)" + the text
    source_blocks = [
        f"[{c['id']}] ({c['heading']})\n{c['text']}" for c in chunks
    ]

    user = (
        f"FIT-ERGEBNIS (Modell: {fit_result['model']}):\n"
        + "\n".join(param_lines)
        + "\n\nQUELLEN:\n"
        + "\n\n".join(source_blocks)
        + f"\n\nFRAGE: {question}"
    )
    return system, user
