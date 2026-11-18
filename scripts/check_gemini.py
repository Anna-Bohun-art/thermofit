"""Quick check that the key works: python scripts/check_gemini.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.rag import llm  # noqa: E402

print("embedding shape:", llm.embed(["test"]).shape)
print("chat reply:", llm.chat("Answer in one word.", "Say hello."))
