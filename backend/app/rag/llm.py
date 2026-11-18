"""Thin OpenAI-compatible client (Gemini by default, LM Studio for local chat).

Embeddings must always come from the SAME model as the index (gemini-embedding-001).
Env vars:
  GEMINI_API_KEY        key (Render env var only, never committed)
  LLM_BASE_URL          chat endpoint, default Gemini's OpenAI-compatible URL
  LLM_MODEL             default gemini-3.1-flash-lite
  EMBED_MODEL           default gemini-embedding-001
"""
from __future__ import annotations

import os
from pathlib import Path

import httpx
import numpy as np
from dotenv import load_dotenv

# Local dev: read backend/.env (on Render the key is a real env var; this does nothing there)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
TIMEOUT = 30.0


class LLMError(RuntimeError):
    pass


def _headers() -> dict:
    key = os.environ.get("GEMINI_API_KEY", "")
    return {"Authorization": f"Bearer {key}"}


def embed(texts: list[str]) -> np.ndarray:
    """Return an (n, dim) float32 array of embeddings (always via Gemini)."""
    model = os.environ.get("EMBED_MODEL", "gemini-embedding-001")
    try:
        r = httpx.post(f"{GEMINI_URL}/embeddings", headers=_headers(),
                       json={"model": model, "input": texts}, timeout=TIMEOUT)
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMError(f"Embedding request failed: {exc}") from exc
    data = r.json()["data"]  # returned in input order
    return np.asarray([d["embedding"] for d in data], dtype=np.float32)


def chat(system: str, user: str, max_tokens: int = 400) -> str:
    base = os.environ.get("LLM_BASE_URL", GEMINI_URL)
    model = os.environ.get("LLM_MODEL", "gemini-3.1-flash-lite")
    try:
        r = httpx.post(f"{base}/chat/completions", headers=_headers(), timeout=TIMEOUT, json={
            "model": model, "max_tokens": max_tokens, "temperature": 0.2,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        })
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMError(f"Chat request failed: {exc}") from exc
    return r.json()["choices"][0]["message"]["content"]
