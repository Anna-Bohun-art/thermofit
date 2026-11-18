"""Offline: backend/knowledge/*.md -> backend/app/rag/{chunks.json,index.npz}.

Run from repo root with GEMINI_API_KEY set:  python scripts/build_index.py
Needs core.chunk_markdown (Anna).
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.rag import core, llm  # noqa: E402


def main() -> None:
    chunks: list[dict] = []
    for md in sorted((ROOT / "backend" / "knowledge").glob("*.md")):
        chunks += core.chunk_markdown(md.read_text(encoding="utf-8"), md.stem)
    if not chunks:
        sys.exit("No chunks: add .md files to backend/knowledge/")
    vecs = []
    for i in range(0, len(chunks), 50):  # batches keep requests small
        vecs.append(llm.embed([c["text"] for c in chunks[i:i + 50]]))
    out = ROOT / "backend" / "app" / "rag"
    np.savez_compressed(out / "index.npz", embeddings=np.vstack(vecs))
    (out / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(chunks)} chunks indexed")


if __name__ == "__main__":
    main()
