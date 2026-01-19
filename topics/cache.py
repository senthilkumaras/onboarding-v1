import os
import json
import hashlib
from pathlib import Path

CACHE_DIR = Path(os.getenv("RAG_CACHE_DIR", "./rag_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key(topic: str, question: str) -> str:
    raw = f"{topic}||{question}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def get_cached_answer(topic: str, question: str):
    fp = CACHE_DIR / f"{_key(topic, question)}.json"
    if fp.exists():
        return json.loads(fp.read_text(encoding="utf-8"))
    return None


def set_cached_answer(topic: str, question: str, payload: dict):
    fp = CACHE_DIR / f"{_key(topic, question)}.json"
    fp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
